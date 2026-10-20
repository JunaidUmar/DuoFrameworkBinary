using DuoLabz.Monetization;
using UnityEngine;

public sealed class MonetizationGameplayExample : MonoBehaviour
{
    private const string StoreModalReason = "store-purchase";

    // Enable progression in Duo settings. Call this only after the game's analytics privacy decision.
    public void ApplyAnalyticsPermission(bool allowed) => DuoProgression.SetCollectionAllowed(allowed);

    public void OnLevelStarted(string stableLevelName) => DuoProgression.Start(stableLevelName);
    public void OnLevelCompleted(string stableLevelName) => DuoProgression.Complete(stableLevelName);
    public void OnLevelFailed(string stableLevelName) => DuoProgression.Fail(stableLevelName, reason: "gameplay_failure");

    private void OnEnable()
    {
        DuoMonetization.StateChanged += HandleMonetizationStateChanged;
    }

    private void OnDisable()
    {
        DuoMonetization.StateChanged -= HandleMonetizationStateChanged;
    }

    public void OnMenuOpened()
    {
        DuoMonetization.ShowBanner();
        DuoAnalytics.LogEvent("menu_opened");
    }

    public void OnMenuClosed()
    {
        DuoMonetization.HideBanner();
    }

    public void ContinueAfterLevelWithOptionalInterstitial()
    {
        DuoMonetization.ShowInterstitial(LoadNextLevel);
    }

    public void OfferRewardedCoins()
    {
        DuoMonetization.ShowRewarded(rewardEarned =>
        {
            if (rewardEarned)
            {
                GrantCoins();
                DuoAnalytics.LogEvent("rewarded_coins_granted", "amount", 100L);
            }
        });
    }

    public void OnLoadingScreenShown()
    {
        DuoMonetization.SetStartupLoadingScreenVisible(true);
    }

    public void OnMainContentReady()
    {
        DuoMonetization.MarkMainContentInteractive();
    }

    public void OnPurchaseStarted()
    {
        DuoMonetization.BeginBlockingModal(StoreModalReason);
    }

    public void OnPurchaseFinishedOrCancelled()
    {
        DuoMonetization.EndBlockingModal(StoreModalReason);
    }

    public void OpenPrivacyChoices()
    {
        DuoMonetization.ShowPrivacyOptions();
    }

    private static void HandleMonetizationStateChanged(MonetizationState state)
    {
        Debug.Log($"Monetization state: {state}");
    }

    private static void LoadNextLevel()
    {
        Debug.Log("Continue the game flow here.");
    }

    private static void GrantCoins()
    {
        Debug.Log("Grant the earned reward here.");
    }
}
