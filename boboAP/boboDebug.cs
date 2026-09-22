using BobosWorld;
using System;
using System.Collections.Generic;
using System.Reflection;
using System.Linq;
using HarmonyLib;
using UnityEngine;

namespace BoboBayArchipelago
{
    public static class BoboDebug
    {
        public static void DumpItemSpawnMembers()
        {
            if (!Plugin.DebugLoggingEnabled.Value) return;

            var flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static;

            void Dump(Type type, string nameFilter)
            {
                foreach (var method in type.GetMethods(flags))
                {
                    if (method.Name.IndexOf(nameFilter, StringComparison.OrdinalIgnoreCase) < 0) continue;
                    if (method.IsSpecialName) continue;
                    var parameters = string.Join(", ", Array.ConvertAll(method.GetParameters(),
                        parameter => parameter.ParameterType.Name + " " + parameter.Name));
                    Plugin.Log?.LogInfo($"METHOD  {type.Name}.{method.Name}({parameters}) -> {method.ReturnType.Name}");
                }
            }

            Dump(typeof(Item), "Spawn");
            Dump(typeof(Item), "Despawn");
            Dump(typeof(Garden), "ItemInGarden");
        }
    }

    [HarmonyPatch(typeof(GardenManager), "Awake")]
    public static class NormalCompetitionDumpPatch
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            if (!Plugin.DebugLoggingEnabled.Value) return;

            try
            {
                var all = Resources.FindObjectsOfTypeAll<CompetitionSO>();
                var standalone = all.Where(c => c != null && !c.isSaga).ToList();

                Plugin.Log?.LogInfo($"[APDebug] Found {all.Length} total CompetitionSO, {standalone.Count} standalone (non-saga).");

                foreach (var comp in standalone.OrderBy(c => c.rank).ThenBy(c => c.name))
                {
                    string title = Traverse.Create(comp).Field("title").GetValue<string>();
                    bool known = CompetitionLocations.All.ContainsKey(comp.name);
                    string status = known ? $"OK -> {CompetitionLocations.All[comp.name]}" : "MISSING";

                    Plugin.Log?.LogInfo($"[APDebug] comp: {comp.name} (rank={comp.rank}, type={comp.type}, title='{title}') [{status}]");
                }

                // Flag anything in the dictionary that no longer matches a real competition
                // (stale entries, or the duplicate-key situation from before)
                var realNames = standalone.Select(c => c.name).ToHashSet();
                foreach (var key in CompetitionLocations.All.Keys)
                {
                    if (!realNames.Contains(key))
                        Plugin.Log?.LogWarning($"[APDebug] Dictionary entry '{key}' does not match any live standalone competition.");
                }
            }
            catch (Exception ex)
            {
                Plugin.Log?.LogError($"[APDebug] NormalCompetitionDumpPatch threw: {ex}");
            }
        }
    }

    [HarmonyPatch(typeof(GardenManager), "Awake")]
    public static class PublicWorksDumpPatch
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            if (!Plugin.DebugLoggingEnabled.Value) return;

            try
            {
                var collections = Resources.FindObjectsOfTypeAll<PublicWorksProjectCollectionSO>();
                Plugin.Log?.LogInfo($"[APDebug] Found {collections.Length} PublicWorksProjectCollectionSO asset(s).");

                foreach (var col in collections)
                {
                    Plugin.Log?.LogInfo($"=== Collection: {col.name} (Count: {col.collection?.Count ?? 0}) ===");
                    if (col.collection == null) continue;

                    foreach (var kvp in col.collection)
                    {
                        PublicWorksProjectSO pwp = kvp.Key;
                        bool isUnlockedOrPurchased = kvp.Value;

                        if (pwp == null) continue;

                        string assetName = pwp.name;
                        string titleKey = pwp.titleKey;
                        int cost = pwp.cost != null ? pwp.cost.Value : 0;
                        PWPTypes type = pwp.type;

                        Plugin.Log?.LogInfo($"  [{assetName}] titleKey='{titleKey}', cost={cost}, type={type} => bool={isUnlockedOrPurchased}");
                    }
                }
            }
            catch (Exception ex)
            {
                Plugin.Log?.LogError($"[APDebug] PublicWorksDumpPatch failed: {ex}");
            }
        }
    }

    [HarmonyPatch(typeof(GardenManager), "Awake")]
    public static class SagaRosterDumpPatch
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            if (!Plugin.DebugLoggingEnabled.Value) return;

            try
            {
                var sagas = Resources.FindObjectsOfTypeAll<CompetitionSeriesSO_Saga>();
                Plugin.Log?.LogInfo($"[APDebug] Found {sagas.Length} CompetitionSeriesSO_Saga instance(s).");

                foreach (var saga in sagas)
                {
                    if (saga == null) continue;
                    string title = Traverse.Create(saga).Field("title").GetValue<string>();
                    Plugin.Log?.LogInfo($"[APDebug] SAGA '{saga.name}' (title='{title}', locked={saga.locked})");

                    foreach (var comp in saga.competitions ?? new List<CompetitionSO>())
                    {
                        string compTitle = Traverse.Create(comp).Field("title").GetValue<string>();
                        Plugin.Log?.LogInfo($"[APDebug]   comp: {comp.name} (rank={comp.rank}, title='{compTitle}')");
                    }
                }
            }
            catch (Exception ex)
            {
                Plugin.Log?.LogError($"[APDebug] SagaRosterDumpPatch threw: {ex}");
            }
        }
    }

    [HarmonyPatch(typeof(CompetitionSO), "Unlocked")]
    public static class SagaUnlockDiagnosticPatch
    {
        [HarmonyPostfix]
        public static void Postfix(CompetitionSO __instance, ref bool __result)
        {
            if (!Plugin.DebugLoggingEnabled.Value) return;
            if (__instance == null || !__instance.isSaga) return;
            Plugin.Log?.LogInfo($"[APDebug] Saga comp '{__instance.name}': saga='{__instance.saga?.name}', saga.locked={__instance.saga?.locked}, Unlocked()={__result}");
        }
    }
}