# Duo Monetization — binary package

Stable release **2.0.0**, built for Unity **6000.4.1f1**, approved by the project owner on **2026-10-20 for Android production rollout** after Android device testing, including the app-open consent-startup fix. **iOS device acceptance is still pending; this release is not a claim of iOS production verification.** Runtime and Editor implementation is compiled into DLLs; usage examples remain readable. This does not prevent decompilation.

This update starts the SDK callback processor before requesting UMP consent, correcting a startup-order issue that could hold consent completion until the 15-second watchdog. Ads still initialize only after the privacy/configuration gates permit them. Update the Git tag in your existing package dependency; migration does not need to be repeated when updating from rc.1.

## Installation

1. Authenticate GitHub with an account authorized for the private `DuoFrameworkBinary` repository. Install Git; Git LFS is not required.
2. Install through Package Manager > Install package from Git URL:

   `https://github.com/JunaidUmar/DuoFrameworkBinary.git#v2.0.0`

3. Open Tools > DuoLabz > Monetization > Setup Assistant. Install **Google Mobile Ads 11.4.0**, **Firebase App, Analytics and Remote Config 13.16.0**, and **External Dependency Manager 1.2.188** as Unity packages. The DLLs enable automatically after dependencies are present and Unity recompiles. This release deliberately requires the validated versions; changing SDK versions requires a new tested binary release. Install dependencies before importing the usage sample or compiling gameplay scripts that call the framework.
4. Add the game's Firebase configuration files and AdMob app IDs using the official SDK tools.
5. Run Create or Repair Setup. This creates the settings asset, bootstrap prefab and `Assets/DuoMonetization/link.xml`. Keep the preservation file in the game; Unity does not support placing that file only inside a package.
6. Configure Android/iOS fallback IDs and the per-game telemetry endpoint/credential in the settings Inspector. Keep production credentials out of shared repositories and samples.
7. Add one bootstrap prefab to the game's first scene. Use `DuoMonetization` and `DuoAnalytics` in gameplay. See the Basic Integration sample.

Official guides: [Google Mobile Ads](https://developers.google.com/admob/unity/quick-start), [Firebase Unity](https://firebase.google.com/docs/unity/setup).

## Upgrade from the source package

Commit your game first. Do not install source and binary implementations simultaneously.

1. Save scenes and assets, then replace the existing `com.duolabz.monetization` Git dependency with the binary Git URL. Remove any copied legacy framework scripts; duplicate types are not supported.
2. Ensure the validated SDKs are installed and let Unity compile.
3. Run Tools > DuoLabz > Monetization > Migrate Source Package References to DLLs. This explicitly confirms changes, remaps known source-package script references in text-serialized scenes/prefabs/settings and backs up originals under `Library/DuoBinaryMigration`. It does not migrate custom copies with different GUIDs, binary-serialized assets, or Addressables bundles. Contact the framework maintainer for those cases.
4. Reopen affected scenes, run Create or Repair Setup, verify there are no missing scripts and review all settings. Rebuild any previously built bundles.
5. Test Android and iOS before shipping. Revert the game commit and restore the v1.3.1 Git URL if rollback is needed. Do not remove the old release during the transition.

## Supported behavior and release checks

Public gameplay calls, priority/fallback handling, UMP-owned consent and telemetry environments are retained. The optional custom manual ATT fallback is not included in this candidate; use the normal Google UMP configuration.

Use development/test-ad builds for QA. Check consent allow/deny, all ad formats, rewarded callbacks, app-open suppression, platform-specific IDs, Remote Config/cache/Inspector fallback, analytics, recorded revenue and telemetry uploads. Check both development and release IL2CPP builds. This package contains no Firebase or AdMob SDK binaries or their native installers; install those official dependencies separately.

## Updating

Change the Git URL tag to an approved newer version in Package Manager or `Packages/manifest.json`. Release tags are immutable. SDK compatibility is listed for each release; do not silently upgrade third-party SDKs beyond the validated version set.
