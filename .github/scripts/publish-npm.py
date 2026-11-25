import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError
from urllib.request import Request, urlopen

NAME = "com.duolabz.monetization"
REGISTRY = "https://registry.npmjs.org"
REPOSITORY = "git+https://github.com/JunaidUmar/DuoFrameworkBinary.git"
UPM_ARCHIVE_URL = "https://cdn.packages.unity.com/upm-cli/releases/v10.0.0/upm-linux-x64.zip"
UPM_ARCHIVE_SHA256 = "85852820608b9bb81bf112f8a9f242e06bbed0fceabb0eab24e4cabbdbec08a2"
SIGNATURE = ".attestation.p7m"
SIGNING_CREDENTIALS = {"UPM_SERVICE_ACCOUNT_KEY_ID", "UPM_SERVICE_ACCOUNT_KEY_SECRET"}
STABLE_VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
AUTOMATION = {".github/workflows/npm-publish.yml", ".github/scripts/publish-npm.py"}
BINARIES = {
    "Editor/DuoLabz.Monetization.Binary.Installer.dll",
    "Editor/DuoLabz.Monetization.Editor.dll",
    "Runtime/DuoLabz.Monetization.dll",
}


def archive_files(data, prefix=""):
    files = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
        for member in archive:
            if member.isdir():
                continue
            name = member.name.removeprefix(prefix)
            path = PurePosixPath(name)
            if (not member.isfile() or not member.name.startswith(prefix) or path.is_absolute()
                    or ".." in path.parts or name in files):
                raise RuntimeError(f"Unexpected archive entry: {member.name}")
            files[name] = archive.extractfile(member).read()
    return files


def release_files(tag, version):
    ref = f"refs/tags/{tag}"
    subprocess.run(["git", "merge-base", "--is-ancestor", ref, "refs/remotes/origin/main"], check=True)
    files = archive_files(subprocess.check_output(["git", "archive", "--format=tar", ref]))
    for path in AUTOMATION:
        files.pop(path, None)

    for name in files:
        path = PurePosixPath(name)
        if path.suffix == ".cs" and path.parts[0] == "Samples~":
            continue
        if path.suffix not in {".md", ".meta", ".xml", ".json"} and name not in BINARIES:
            raise RuntimeError(f"Unexpected binary release file: {name}")

    metadata = json.loads(files["package.json"])
    manifest = json.loads(files["release-manifest.json"])
    hashes = {name: hashlib.sha256(contents).hexdigest()
              for name, contents in files.items() if name != "release-manifest.json"}
    if metadata["name"] != NAME or metadata["version"] != version or manifest["version"] != version:
        raise RuntimeError("Git tag, package name or release version mismatch")
    if hashes != manifest["sha256"] or not BINARIES <= files.keys():
        raise RuntimeError("Release files do not match the audited binary manifest")
    return files


def registry_package():
    request = Request(f"{REGISTRY}/{NAME}", headers={"Cache-Control": "no-cache"})
    with urlopen(request, timeout=15) as response:
        return json.load(response)


def check_package(contents, files, require_signature):
    packed = archive_files(contents, prefix="package/")
    attestation = packed.pop(SIGNATURE, b"")
    if packed != files:
        raise RuntimeError("The tarball files differ from the audited binary Git tag")
    if require_signature and not attestation:
        raise RuntimeError("The tarball lacks its Unity package signature")
    return attestation


def verify_on_npm(metadata, version, files, require_signature, expected_signature=None):
    if version not in metadata.get("versions", {}):
        return False
    url = f"{REGISTRY}/{NAME}/-/{NAME}-{version}.tgz"
    try:
        with urlopen(Request(url, headers={"Cache-Control": "no-cache"}), timeout=20) as response:
            attestation = check_package(response.read(), files, require_signature)
    except HTTPError as error:
        if error.code == 404:
            return False
        raise
    if expected_signature is not None and attestation != expected_signature:
        raise RuntimeError(f"The Unity signature on npm differs from the tarball published for {NAME}@{version}")
    return True


def install_signer(destination):
    with urlopen(UPM_ARCHIVE_URL, timeout=40) as response:
        archive = response.read()
    if hashlib.sha256(archive).hexdigest() != UPM_ARCHIVE_SHA256:
        raise RuntimeError("Pinned Unity signing tool checksum mismatch")
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        bundle.extractall(destination)
    binary = destination / "UnityPackageManager"
    binary.chmod(0o700)
    return binary


def sign_and_publish(files, sign_only=False):
    organization = os.environ.get("UPM_ORGANIZATION_ID")
    if not organization or any(not os.environ.get(name) for name in SIGNING_CREDENTIALS):
        raise RuntimeError("Configure the Unity organization ID and both signing secrets in npm-production")
    metadata = json.loads(files["package.json"])
    if not sign_only and metadata.get("repository", {}).get("url") != REPOSITORY:
        raise RuntimeError("package.json must identify the public binary repository for npm provenance")

    with tempfile.TemporaryDirectory(prefix="duoframework-npm-") as temporary:
        root = Path(temporary)
        package = root / "package"
        output = root / "signed"
        output.mkdir()
        for name, content in files.items():
            path = package / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        signer = install_signer(root / "upm-cli")
        signing_environment = {name: value for name, value in os.environ.items()
                               if not name.startswith("ACTIONS_ID_TOKEN_REQUEST_")}
        subprocess.run([str(signer), "pack", str(package), "--organization-id", organization,
                        "--destination", str(output)], check=True, env=signing_environment)
        tarballs = list(output.glob("*.tgz"))
        if len(tarballs) != 1:
            raise RuntimeError("Unity Package Manager must produce exactly one signed tarball")
        tarball = tarballs[0]
        attestation = check_package(tarball.read_bytes(), files, require_signature=True)
        print(f"Unity signing produced the audited package and its attestation for {NAME}@{metadata['version']}.",
              flush=True)
        if not sign_only:
            npm_environment = {name: value for name, value in os.environ.items()
                               if name not in SIGNING_CREDENTIALS}
            subprocess.run(
                ["npm", "publish", str(tarball), "--registry", REGISTRY, "--tag", "latest", "--ignore-scripts"],
                cwd=package,
                check=True,
                env=npm_environment,
            )
        return attestation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tag")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verify-only", action="store_true")
    mode.add_argument("--sign-only", action="store_true")
    options = parser.parse_args()
    if not re.fullmatch(f"v{STABLE_VERSION}", options.tag):
        parser.error("Expected a stable tag such as v2.8.2")
    version = options.tag[1:]
    files = release_files(options.tag, version)
    if options.sign_only:
        sign_and_publish(files, sign_only=True)
        return

    metadata = registry_package()
    latest = metadata.get("dist-tags", {}).get("latest", "")
    if verify_on_npm(metadata, version, files, require_signature=not options.verify_only):
        if not options.verify_only and (
            not re.fullmatch(STABLE_VERSION, latest)
            or tuple(map(int, latest.split("."))) < tuple(map(int, version.split(".")))
        ):
            raise RuntimeError(f"{NAME}@{version} exists, but npm latest is {latest!r}")
        print(f"Verified {NAME}@{version} matches the stable Git tag.")
        return
    if options.verify_only:
        raise RuntimeError(f"{NAME}@{version} is not publicly available on npm")
    if not re.fullmatch(STABLE_VERSION, latest):
        raise RuntimeError(f"Expected npm to have a stable latest version, found {latest!r}")
    if tuple(map(int, version.split("."))) < tuple(map(int, latest.split("."))):
        raise RuntimeError(f"Refusing to replace npm latest {latest} with {version}")

    expected_signature = None
    if version != latest and version not in metadata.get("versions", {}):
        expected_signature = sign_and_publish(files)
    print(f"Waiting for {NAME}@{version} to become public on npm.", flush=True)
    deadline = time.monotonic() + 15 * 60
    while time.monotonic() < deadline:
        metadata = registry_package()
        if metadata.get("dist-tags", {}).get("latest") == version and verify_on_npm(
            metadata, version, files, require_signature=True, expected_signature=expected_signature
        ):
            print(f"Verified {NAME}@{version} is public and marked latest.")
            return
        time.sleep(15)
    raise RuntimeError("npm has not made this version available as latest. Check the npm release status before retrying.")


if __name__ == "__main__":
    main()
