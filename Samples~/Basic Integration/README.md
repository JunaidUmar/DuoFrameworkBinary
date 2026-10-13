# Basic Integration Sample

Import this sample from Package Manager after completing **Tools > DuoLabz > Monetization > Create or Repair Setup**.

`MonetizationGameplayExample` demonstrates the public game-facing API. Attach it to a screen controller only as a reference; the persistent managers are created by the `DuoMonetization` bootstrap prefab and must not be added to individual scenes.

Replace the example reward and navigation methods with your game's real implementations. Never grant a rewarded item unless the callback value is `true`.
