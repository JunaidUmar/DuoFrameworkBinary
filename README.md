# Duo Monetization — binary package

Release **2.2.0**, built for Unity **6000.4.1f1**. Adds immediate ad telemetry capture, durable queue backups, conservative retry pacing, ad-source/revenue-precision metadata and delivery diagnostics. The owner authorized production release based on automated validation on 2026-10-21. **This telemetry update has not received new Android or iOS physical-device testing.** Earlier tags remain available for rollback. Runtime and Editor implementation is compiled into DLLs; usage examples remain readable. This does not prevent decompilation.

Consent startup and gameplay callbacks retain their main-thread dispatch. Impression, click and revenue callbacks are persisted before waiting for Unity to resume. Server 1.3.0 stores the optional diagnostics; older clients and older telemetry servers remain compatible. Update the Git tag in your game, then rebuild and release the game to deliver these fixes to players. Migration does not need to be repeated for an existing binary installation.

## Installation

1. Install Git; Git LFS is not required. The binary repository is public, so GitHub authentication and collaborator invitations are not required for installation. The software remains proprietary under the included license; public download does not grant unrestricted redistribution rights.
2. Install through Package Manager > Install package from Git URL:

   `https://github.com/JunaidUmar/DuoFrameworkBinary.git#v2.2.0`

3. Open Tools > DuoLabz > Monetization > Setup Assistant. Install **Google Mobile Ads 11.4.0**, **Firebase App, Analytics and Remote Config 13.16.0**, and **External Dependency Manager 1.2.188** as Unity packages. The DLLs enable automatically after dependencies are present and Unity recompiles. This release deliberately requires the validated versions; changing SDK versions requires a new tested binary release. Install dependencies before importing the usage sample or compiling gameplay scripts that call the framework.
4. Add the game's Firebase configuration files and AdMob app IDs using the official SDK tools.
5. Run Create or Repair Setup. This creates the settings asset, bootstrap prefab and `Assets/DuoMonetization/link.xml`. Keep the preservation file in the game; Unity does not support placing that file only inside a package.
6. Configure Android/iOS fallback IDs and the per-game telemetry endpoint/credential in the settings Inspector. Keep production credentials out of shared repositories and samples.
7. Add one bootstrap prefab to the game's first scene. Use `DuoMonetization` and `DuoAnalytics` in gameplay. See the Basic Integration sample.

Official guides: [Google Mobile Ads](https://developers.google.com/admob/unity/quick-start), [Firebase Unity](https://firebase.google.com/docs/unity/setup).

## Optional progression and funnels

Enable **Progression Enabled** in Duo settings and select its server/Firebase/GameAnalytics destinations. It is disabled by default, preserving existing games. The existing standard telemetry endpoint resolves `/api/v1/progression/events`; use the same per-application credential.

For GameAnalytics, install/configure the [official SDK](https://docs.gameanalytics.com/event-tracking-and-integrations/sdks-and-collection-api/game-engine-sdks/unity/) separately (validated against **8.3.0**, source revision `7f661deab09d5224fbd32af5c24f7259c11b238f`). Add Android/iOS keys in GameAnalytics settings. Remove other initialization and duplicate progression calls; Duo owns initialization after collection is allowed. Run **Create or Repair Setup** after upgrading to generate the game's updated preservation file for IL2CPP.

```csharp
using DuoLabz.Monetization;

// Apply the game's analytics privacy decision after bootstrap initialization.
DuoProgression.SetCollectionAllowed(analyticsAllowed);
DuoProgression.Start("level_001");
DuoProgression.Complete("level_001", score: 0);

DuoProgression.Start("Classic", "World_2", "Level_5");
DuoProgression.Fail("Classic", "World_2", "Level_5", reason: "time_limit");
```

Use exactly the same path for an attempt's start/outcome. Call on the Unity main thread. Names are stable strings (1–64 characters per part, no colons/control characters), not random IDs. Repeated Start on an active path is ignored; retries begin after an outcome. Outcomes without Start are ignored with a warning. Quitting/backgrounding is not failure. Duration measures elapsed time including background time.

Each newly recorded progression event writes a Unity Console/Android Logcat line, including in non-development builds: `[Duo Progression] Recorded locally | start | level_001 | environment=development`. Filter for `[Duo Progression]` to check call timing. This confirms local queue acceptance, not Firebase/GameAnalytics/server receipt. Duplicate Starts and events blocked by collection permission do not log as recorded. Player identifiers, credentials and free-text failure details are not logged; keep level names free of personal data.

Progression Requires Consent defaults on: no collection/replay before `SetCollectionAllowed(true)`. This is separate from ad consent and does not control Firebase automatic events or code outside Duo. Configure the game's privacy disclosures and applicable SDK controls. Automatic development/staging progression goes only to Duo unless the corresponding vendor QA option is explicitly enabled **with separate QA projects/games**.

The app/environment-specific random Duo reference persists across sessions; clearing app data/reinstall may reset it, subject to OS backups. No device registration or advertising identifier is used for Duo. `SetCollectionAllowed(false)` clears unsent progression. `ResetLocalIdentity()` does not delete historical data. `RequestServerDataDeletion(callback)` requests Duo erasure, stops collection, and rotates the reference on success; retry failures before resetting it. Vendor history requires vendor-specific deletion.

Open the application's **Progression overview** or **Player funnels** in Console. Choices appear only after matching events are received. Optional empty hierarchy parts mean no further part, not any descendant. Reports support ordered/unordered steps after entry, completion windows, revisions, environments and CSV export. Dates select each installation's first matching entry, not all later outcomes. Pending is not confirmed churn. Reports may differ from vendor charts due to session/identity, timing and counting definitions. Server retries are deduplicated; vendor SDK delivery across crashes is not guaranteed exactly once.

Validate each target platform, consent allow/deny, flat/nested paths, retries, offline/restart delivery, QA separation, SDK dashboards and known funnel journeys before rolling out to its production games. Production rollout is owner-approved on automated evidence; new Android/iOS physical-device testing of this release remains pending.

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
