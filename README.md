# Duo Monetization — binary package

Binary release **2.5.0**, built for Unity **6000.4.1f1**. Adds Game Parameters, Framework Settings, and A/B group filters in Player Funnels. Physical-device acceptance for this release remains pending on Android and iOS.

## SDK installation and cleanup

Open **Tools > DuoLabz > Monetization > Manage SDKs** (also available through **SDK Installation** in the Setup Assistant). Review installed, recommended and tested/untested status. **Preview SDK installation** shows every install/replacement before confirmation. Optional GameAnalytics is off by default; its archive opens Unity's import preview. Existing Firebase configuration files, AdMob app IDs and Duo settings are preserved.

The installer configures the narrow AdMob OpenUPM registry when needed, downloads versioned Google/GameAnalytics archives from official HTTPS sources and verifies SHA-256 hashes before installation. Downloads finish before the package manifest changes. The manifest and existing lock file are backed up under `Library/DuoSdkSetup/backups`; setup resumes after recompilation. The window offers a guarded manifest restore, and never automatically deletes legacy SDKs from Assets. Migrate duplicate SDK copies manually first.

Temporary `.part` files and imported/cancelled GameAnalytics `.unitypackage` downloads are removed automatically. **Referenced Firebase/Dependency Manager `.tgz` files are not disposable installers:** they stay in `Packages/DuoSdkArchives`. Commit that folder with `Packages/manifest.json` and `Packages/packages-lock.json` so teammates can resolve the same dependencies. **Clean unused setup files** removes only unchanged archives downloaded by Duo that no manifest, lock file or rollback backup references. Backups and user-owned files are preserved.

Supported stable ranges: AdMob >=11.4.0 and <12.0.0; Firebase >=13.16.0 and <14.0.0 (all installed Firebase products must match); Dependency Manager >=1.2.186 and <2.0.0. Untested versions inside those ranges show a warning. Optional GameAnalytics is validated against 8.3.0. Major upgrades and prerelease SDKs require separate compatibility work. Direct source/download buttons remain available as an installation fallback.

## Installation

1. Install Git; Git LFS is not required. The binary repository is public, so GitHub authentication and collaborator invitations are not required for installation. The software remains proprietary under the included license; public download does not grant unrestricted redistribution rights.
2. In Package Manager choose Add package from git URL and enter `https://github.com/JunaidUmar/DuoFrameworkBinary.git#v2.5.0`. If you have the release ZIP, extract it and choose Add package from disk to select its `package.json`.

3. Open Tools > DuoLabz > Monetization > Manage SDKs, then preview and install the recommended SDK selection. The installer is available even when Google/Firebase SDKs are missing. The DLLs activate after compatible dependencies resolve and Unity recompiles. Install dependencies before importing the usage sample or compiling gameplay scripts that call the framework.
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

Public gameplay calls, priority/fallback handling, UMP-owned consent and telemetry environments are retained. Use the normal Google UMP configuration for consent.

Use development/test-ad builds for QA. Check consent allow/deny, all ad formats, rewarded callbacks, app-open suppression, platform-specific IDs, Remote Config/cache/Inspector fallback, analytics, recorded revenue and telemetry uploads. Check both development and release IL2CPP builds. This package contains no Firebase or AdMob SDK binaries or their native installers; install those official dependencies separately.

## Updating

Change the Git URL tag to an approved newer version in Package Manager or `Packages/manifest.json`. Release tags are immutable. SDK compatibility is listed for each release; do not silently upgrade third-party SDKs beyond the validated version set.

Crashlytics is available as an optional SDK in Manage SDKs and matches the installed Firebase release. New settings prefill the Duo telemetry URL; Create or Repair Setup fills a blank URL while preserving custom URLs. Progression derives its route from telemetry; existing custom overrides are preserved and hidden from normal editing. Verify Crashlytics reporting with a device test crash and platform symbol setup.

## DuoPulse integration checklist

Keep **Integration Reporting Enabled** and **Telemetry Enabled** on in Duo settings. Development/staging reporting is automatic; production/release builds additionally require **Integration Reporting In Production** to be enabled explicitly. The standard configured telemetry URL resolves `/api/v1/integration/reports` on the same HTTPS host, supporting both Pulse and the legacy host. Custom nonstandard telemetry paths do not enable this feature. Editor play mode does not upload reports; make an Android/iOS build and run it on a device.

Build processing embeds a generated per-build UUID and non-secret setup results into the compiled scene's bootstrap. Original scenes, prefabs, Google files and credential settings are not rewritten. No requests are made on the build machine. When the game runs, it reports those embedded build facts and a separate runtime snapshot. The report timestamp is when the snapshot was produced for upload, not a claim about when an SDK was installed or when the build was compiled. Existing binaries cannot begin reporting without rebuilding.

Build checks cover Duo settings, installed Firebase/AdMob SDKs, optional GameAnalytics compatibility/keys, the platform Google services file and identifier match, and the AdMob app ID. Multiple matching Google config files fail the file check rather than choosing one silently. Runtime checks report observed Firebase initialization, fresh Remote Config fetch/activation, ad initialization/load, and GameAnalytics initialization when Duo owns it. Cached defaults do not count as a fresh server fetch. Collection states and vendor delivery are not inferred from SDK presence.

Firebase Analytics collection stays **unknown** unless your game explicitly reports the state it set after its privacy decision:

```csharp
DuoLabz.Monetization.DuoIntegrationChecklist.ReportFirebaseAnalyticsCollection(analyticsEnabled);
```

This method reports a state; it does not enable/disable Firebase, grant consent, or prove Firebase received events. Optional GameAnalytics remains not applicable when its destination is disabled, and waits for the existing progression privacy flow when enabled.

Leave **Integration Details Revision** at `-1` unless the developer knows the portal revision actually used. This is not the Firebase Remote Config revision. Matching revision numbers are client-reported evidence, not independent content verification.

The dashboard is application > **Integration checklist**. Select the correct platform/environment/build. Runtime snapshots are coalesced (at least 60 seconds between changes), with unchanged callbacks suppressed. The eight-entry persistent retry queue is scoped to endpoint, credential, environment and build using a hash; files contain reports, not credentials, player/device IDs, raw logs or Google file contents. Retries preserve report UUID/body, back off to 30 minutes, expire after seven days, reject redirects, and require a matching server acknowledgment before removal. Invalid reports are discarded; rejected credentials suspend uploads for the current run. Reporting failures do not stop gameplay. Disabling telemetry or checklist reporting stops checklist uploads. Device networking, native SDK behavior and Google file packaging still require a game/device test.


### Banner layout API

Inspector settings select Adaptive/Standard banner size, Top/Bottom banner position and one of seven rectangle presets (Top, Bottom, Center, or any corner). Standard is 320×50 dp; Medium Rectangle remains 300×250 dp using the separate rectangle IDs. Existing no-argument calls keep using configured defaults (adaptive-bottom and rectangle-top for existing projects).

```csharp
using DuoLabz.Monetization;
DuoMonetization.ConfigureBanner(BannerSize.Standard, BannerPosition.Bottom);
DuoMonetization.ConfigureMediumRectangle(RectanglePosition.Center);
DuoMonetization.ShowBanner();
DuoMonetization.ShowBanner(BannerPosition.Top, BannerSize.Adaptive);
DuoMonetization.ShowMediumRectangle(RectanglePosition.Center);
DuoMonetization.ShowMediumRectangle(RectanglePosition.BottomRight);
DuoMonetization.SetBannerPosition(BannerPosition.Bottom);
DuoMonetization.SetMediumRectanglePosition(RectanglePosition.Top);
DuoMonetization.HideBanner();
DuoMonetization.HideMediumRectangle();
```

Configure calls may precede initialization; show/hide calls require the Duo instance. Call these APIs on Unity's main thread. Size changes reload while retaining visibility intent; position-only changes move existing views. `GetBannerSizeInPixels()` and `GetMediumRectangleSizeInPixels()` return actual loaded screen-pixel sizes, or zero before ready. Respect Canvas scaling when reserving UI space. Automatic-refresh flags must match AdMob's per-format settings. Physical Android/iOS validation remains pending.

## DuoPulse Game Settings

Use DuoPulse 1.8.0 or later for Game Parameters and Framework Settings. In the application workspace, developers register stable keys with a type and default. Scoped studio managers edit draft values, preview and publish a version for Development, Staging or Production, or restore an earlier version as a new revision. Ad Unit Configuration has its own editor. Keep keys stable for installed builds and use a new key when a type changes.

In the Unity settings asset, enable **Use DuoPulse Game Settings**, copy the application ID from the Game Parameters page into **Duo Pulse Game Id**, and use the existing per-game telemetry URL and token. Choose **Game Settings Environment** or leave it on Automatic, which uses Development for Editor/development builds and Production for release builds. Settings retrieval uses the application token independently of telemetry collection.

At startup, Unity loads the last valid snapshot for this game and environment. Background refresh downloads a complete published version and stages it. Call `DuoConfig.ActivatePending()` on the main thread at a safe transition, such as opening the lobby or starting a new run. `DuoConfig.HasPendingChanges` indicates that a version is available. The first launch can use the fallbacks bundled in game code.

```csharp
DuoConfig.ActivatePending();
int interval = DuoConfig.GetInt("special_level_counter", fallback: 5);
var order = DuoConfig.GetStringList("level_order", new[] { "level_01", "level_02" });
```

Use `GetBool`, `GetInt`, `GetNumber`, `GetString`, `GetDateTime`, `GetStringList` or `GetIntList` for the matching type. Dates are UTC. Unknown keys and mismatched types use the caller's fallback. `DuoConfig.Revision` identifies the active version. Removing a published framework override lets the current local/Firebase interval take over again. Existing game code decides when to request an interstitial.

For an A/B test, the manager sets the regular parameter value for group A and a second value plus a percentage for group B, then publishes to the selected environment. Unity chooses the group using a random installation identifier stored locally. The existing typed getters return that group's value after activation. Older Game Settings builds use the regular value. Removing the test and publishing gives everyone the regular value again.

For funnel reporting, publish a named test and enable DuoPulse Game Settings and server progression reporting in the same environment. Apply the settings at your usual safe transition. The first regular progression start reports the active group using the existing progression identity. Existing progression events from that point are eligible for the group comparison. In Player Funnels, open your existing funnel and select the named test.

For the first test, publish `special_level_counter` as an integer and `level_order` as a string list in Development. Run a development build, activate the new version at the lobby, and verify both values. Check a disconnected restart and restore the preceding revision to verify the cache and rollback path.
