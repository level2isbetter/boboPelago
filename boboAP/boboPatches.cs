using BobosWorld;
using HarmonyLib;

namespace BoboBayArchipelago
{
    [HarmonyPatch(typeof(Bobo), "UpdateStatPoints")]
    public static class SnackStatMultiplierPatch
    {
        [HarmonyPrefix]
        public static void Prefix(ref float multiplier)
        {
            if (ArchipelagoItemHandler.CurrentSnackMultiplier > 1f)
            {
                multiplier *= ArchipelagoItemHandler.CurrentSnackMultiplier;
            }
        }
    }

    [HarmonyPatch(typeof(BoboData), "NewFullDay")]
    public static class UnlimitedSnacksPatch
    {
        [HarmonyPostfix]
        static void Postfix(BoboData __instance)
        {
            if (!ArchipelagoItemHandler.UnlimitedSnacksEnabled) return;
            __instance.FoodMod = 999;
        }
    }
}