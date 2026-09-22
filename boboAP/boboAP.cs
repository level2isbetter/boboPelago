using BobosWorld;
using System;
using System.Reflection;
using System.Collections.Generic;
using System.Linq;
using System.Collections.Concurrent;
using Archipelago.MultiClient.Net;
using Archipelago.MultiClient.Net.Packets;
using Archipelago.MultiClient.Net.Enums;
using Archipelago.MultiClient.Net.Helpers;
using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityAtoms.BaseAtoms;

namespace BoboBayArchipelago
{
    [HarmonyPatch(typeof(CompetitionSO), "Unlocked")]
    public static class CompetitionUnlockPatch
    {

        [HarmonyPostfix]
        public static void Postfix(CompetitionSO __instance, ref bool __result)
        {
            if (__instance == null) return;

            // check if its a saga competition, then check saga lock status
            if (__instance.isSaga && __instance.saga != null)
            {
                __result = !__instance.saga.locked;
                return;
            }

            // check if its the goal competition, then check tickets
            if (__instance.name == ArchipelagoItemHandler.GoalAssetName)
            {
                __result = ArchipelagoItemHandler.BoboTicketsReceived >= ArchipelagoItemHandler.BoboTicketsRequired;
                return;
            }
            
            if (ArchipelagoItemHandler.CompetitionUnlockThresholds.TryGetValue(__instance.name, out int required))
            {
                __result = ArchipelagoItemHandler.ProgressiveCompetitionsReceived >= required;
                return;
            }
        }
    }

    [HarmonyPatch(typeof(CompetitionOrganizer), "SetTodaysCompetitions")]
    public static class CompetitionAvailabilityPatch
    {
        [HarmonyPrefix]
        public static void Prefix()
        {
            foreach (var competition in Resources.FindObjectsOfTypeAll<CompetitionSO>())
            {
                if (competition == null) continue;

                bool forceAvailable;

                if (competition.name == ArchipelagoItemHandler.GoalAssetName)
                {
                    forceAvailable = ArchipelagoItemHandler.BoboTicketsReceived >= ArchipelagoItemHandler.BoboTicketsRequired;
                }
                else
                if (competition.isSaga && competition.saga != null)
                {
                    forceAvailable = !competition.saga.locked;
                }
                else if (ArchipelagoItemHandler.CompetitionUnlockThresholds.TryGetValue(competition.name, out int required))
                {
                    forceAvailable = ArchipelagoItemHandler.ProgressiveCompetitionsReceived >= required;
                }

                competition.dayMonday = true;
                competition.dayTuesday = true;
                competition.dayWednesday = true;
                competition.dayThursday = true;
                competition.dayFriday = true;
                competition.daySaturday = true;
                competition.daySunday = true;
                competition.seasonSpring = true;
                competition.seasonSummer = true;
                competition.seasonFall = true;
                competition.seasonWinter = true;

                if (competition.days == null)
                    competition.days = new List<DaysByWeek>();
                foreach (DaysByWeek day in Enum.GetValues(typeof(DaysByWeek)))
                {
                    if (!competition.days.Contains(day))
                        competition.days.Add(day);
                }

                if (competition.seasons == null)
                    competition.seasons = new List<NFKUtilities.Season>();
                foreach (NFKUtilities.Season season in Enum.GetValues(typeof(NFKUtilities.Season)))
                {
                    if (!competition.seasons.Contains(season))
                        competition.seasons.Add(season);
                }
            }
        }
    }

    [HarmonyPatch(typeof(CompetitionOrganizer), "SetTodaysCompetitions")]
    public static class SagaAvailabilityPatch
    {
        [HarmonyPrefix]
        public static void Prefix()
        {
            foreach (var saga in Resources.FindObjectsOfTypeAll<CompetitionSeriesSO_Saga>())
            {
                if (saga == null) continue;

                if (!string.IsNullOrEmpty(ArchipelagoItemHandler.GoalSagaName) && saga.name == ArchipelagoItemHandler.GoalSagaName)
                {
                    saga.locked = ArchipelagoItemHandler.BoboTicketsReceived < ArchipelagoItemHandler.BoboTicketsRequired;
                    continue;
                }

                saga.locked = ArchipelagoItemHandler.SagaUnlockThresholds.TryGetValue(saga.name, out int required)
                    ? ArchipelagoItemHandler.ProgressiveSagasReceived < required
                    : true;
            }
        }
    }

    [HarmonyPatch(typeof(CompetitionManager), "EndEvent")]
    public static class CompetitionPatch
    {
        [HarmonyPostfix]
        public static void Postfix(CompetitionManager __instance)
        {
            var trav = Traverse.Create(__instance);
            var currentCompSO = trav.Field("_currentCompetitionSO").GetValue();
            if (currentCompSO == null) { Plugin.Log?.LogInfo("[APDebug] _currentCompetitionSO is null"); return; }

            // calculate location ID based on competition SO
            // example: AP loc ID = 20000 + CompID
            var innerSO = Traverse.Create(__instance)
                .Field("_currentCompetitionSO")
                .Field("so")
                .GetValue();

            if (innerSO == null) return;
            
            Plugin.Log?.LogInfo($"[APDebug] Competition asset name: '{currentCompSO}'");
            Plugin.Log?.LogInfo($"[APDebug] Inner SO: '{innerSO}' (type: {innerSO.GetType().Name})");
            foreach (var f in innerSO.GetType().GetFields(
                BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.FlattenHierarchy))
            {
                try { Plugin.Log?.LogInfo($"[APDebug]   {f.Name} = {f.GetValue(innerSO)}"); }
                catch { }
            }

            string soName = (string)typeof(UnityEngine.Object)
                .GetProperty("name")
                .GetValue(innerSO);
            
            if (!CompetitionLocations.All.TryGetValue(soName, out long locationID))
            {
                Plugin.Log?.LogWarning($"[AP] No location ID mapped for competition: '{soName}'");
                return;
            }
            Plugin.Log?.LogInfo($"[AP] Competition '{soName}' -> location {locationID}");
            ArchipelagoManager.CheckLocation(locationID);

            if (soName == ArchipelagoItemHandler.GoalAssetName) // bigjam or powergary rn
            {
                ArchipelagoManager.SendGoalComplete();
            }
        }
    }

    [HarmonyPatch(typeof(UIPublicWorksPurchaseConfirmation), "Yes")]
    public static class PublicWorksPurchasePatch
    {
        [HarmonyPrefix]
        public static bool Prefix(UIPublicWorksPurchaseConfirmation __instance)
        {
            // get project being purchased
            var project = Traverse.Create(__instance).Field("_publicWorksProject").GetValue<PublicWorksProjectSO>();
            if (project == null) return true;
            
            // map project name to location in AP
            if (PublicWorksLocations.All.TryGetValue(project.name, out long locationID))
            {
                ArchipelagoManager.CheckLocation(locationID);
                Plugin.Log?.LogInfo($"[AP] Checked Public Works location: {project.name} ({locationID})");
            }

            // mark check so its hidden
            ArchipelagoItemHandler.MarkPWPCheckCompleted(project.name);

            // deduct public fund money
            var fundField = Traverse.Create(__instance).Field("_publicFund").GetValue<IntVariable>();
            int cost = project.cost != null ? project.cost.Value : Common.DEFAULT_PWPCOST;
            fundField?.Subtract(cost);

            // play sound and update ui
            Traverse.Create(__instance).Field("_purchaseSound").Method("Play2D").GetValue();
            var uiPWP = Traverse.Create(__instance).Field("_uiPublicWorks").GetValue<UIPublicWorksProjects>();
            uiPWP?.RemoveRecord(project);
            __instance.gameObject.SetActive(false);
            
            return false;
        }
    }

    [HarmonyPatch(typeof(SaveSystem), "LoadData")]
    public static class SaveSystemLoadDataPatch
    {
        [HarmonyPostfix]
        public static void Postfix()
        {
            ArchipelagoItemHandler.SyncItemsFromServer();
        }
    }
    
    [HarmonyPatch(typeof(GardenBoboAITree))]
    [BepInPlugin(PluginGuid, PluginName, PluginVersion)]
    public class Plugin : BaseUnityPlugin
    {
        public const string PluginGuid = "com.bobobay.archipelago";
        public const string PluginName = "BoboBay.Archipelago";
        public const string PluginVersion = "0.1.0";

        
        public static ManualLogSource Log { get; private set; }
        public static ConfigFile ConfigFile { get; private set; }


        public static ConfigEntry<string> ServerAddressEntry;
        public static ConfigEntry<string> SlotNameEntry;
        public static ConfigEntry<string> PasswordEntry;
        public static ConfigEntry<bool> AutoConnectEntry;
        public static ConfigEntry<int> BoboTicketsRequiredEntry;
        public static ConfigEntry<bool> DebugLoggingEnabled;

        private static bool _foodModPending = false;
        
        public static ConfigEntryBase[] BoboManagerSettings;

        private void Awake()
        {
            
            Log = Logger;
            ConfigFile = Config;

            // Bind configuration settings
            ServerAddressEntry = Config.Bind("Archipelago", "ServerAddress", "archipelago.gg:38281", "Host address and port for the Archipelago server.");
            SlotNameEntry = Config.Bind("Archipelago", "SlotName", "Player", "Slot name registered in the Archipelago multiworld.");
            PasswordEntry = Config.Bind("Archipelago", "Password", "", "Password for the room (if required).");
            AutoConnectEntry = Config.Bind("Archipelago", "AutoConnect", false, "Automatically attempt connection on startup.");
            DebugLoggingEnabled = Config.Bind("Archipelago", "DebugLogging", false,
                "Enable logging (competition/saga rosters, unlock checks). Off by default. I used this in development mainly, didn't want to get rid of it.");

            SceneManager.sceneLoaded += OnSceneLoaded;
            SceneManager.sceneUnloaded += OnSceneUnloaded;

            // Expose settings array for dynamic UI generation
            BoboManagerSettings = new ConfigEntryBase[]
            {
                ServerAddressEntry,
                SlotNameEntry,
                PasswordEntry,
                AutoConnectEntry
            };

            // Apply Harmony patches
            Harmony.CreateAndPatchAll(Assembly.GetExecutingAssembly(), PluginGuid);

            BoboTicketsRequiredEntry = Config.Bind("Archipelago", "BoboTicketsRequiredEntry", 3,
                "Internal: how many bobo tickets unlock the goal competition.");

            Log.LogInfo($"{PluginName} v{PluginVersion} initialized successfully.");
        }

        private void Update()
        {

            ArchipelagoManager.ProcessPendingSync();
            ArchipelagoManager.ProcessPendingItems();

            if (_foodModPending && ArchipelagoManager.IsInBay){
                if (ArchipelagoItemHandler.ApplyFoodModToCurrentGarden() > 0){
                    _foodModPending = false;
                }
            }
        }

        private static void OnSceneLoaded(Scene scene, LoadSceneMode mode)
        {
            Plugin.Log?.LogInfo($"[Archipelago] Scene loaded: '{scene.name}' (Mode: {mode}).");

            if (scene.name == "Bay")
            {
                ArchipelagoManager.IsInBay = true;
                if (ArchipelagoItemHandler.UnlimitedSnacksEnabled) _foodModPending = true;
            }

            // Example trigger: Auto-connect on the main menu or initial world load
            if (AutoConnectEntry.Value && !ArchipelagoManager.IsConnected)
            {
                ArchipelagoManager.Connect();
            }
        }

        private static void OnSceneUnloaded(Scene scene)
        {
            if (scene.name == "Bay")
            {
                ArchipelagoManager.IsInBay = false;
            } 
        }

    }

    public static class ArchipelagoItemHandler
    {
        public static long CurrentItemIndex { get; set; } = 0;
        public static int BoboTicketsReceived => ArchipelagoManager.CountReceived(BoboTicketId);
        public static int ProgressiveCompetitionsReceived => ArchipelagoManager.CountReceived(ProgressiveCompetitionsId);
        public static int ProgressiveSagasReceived => ArchipelagoManager.CountReceived(ProgressiveSagasId);

        public const long BoboTicketId = 20050000;
        public const long ProgressiveCompetitionsId = 20050001;
        public const long ProgressiveSagasId = 20050002;
        public static int BoboTicketsRequired => Plugin.BoboTicketsRequiredEntry?.Value ?? 3;
        public static float CurrentSnackMultiplier { get; private set; } = 1f;
        public static bool UnlimitedSnacksEnabled { get; private set; } = false;
        private static readonly int BaseMinStat = Common.DEFAULT_MINSTATUPDATE;
        private static readonly int BaseMaxStat = Common.DEFAULT_MAXSTATUPDATE;
        public static Dictionary<string, int> SagaUnlockThresholds = new Dictionary<string, int>();
        public static Dictionary<string, int> CompetitionUnlockThresholds = new Dictionary<string, int>();
        public static HashSet<string> CompletedPWPChecks { get; } = new HashSet<string>();
        public static HashSet<string> ReceivedPWPItems { get; } = new HashSet<string>();
        public static string GoalAssetName = "BigJam_Race_D";
        public static string GoalSagaName = "";

        public static void MarkPWPCheckCompleted(string pwpAssetName)
        {
            CompletedPWPChecks.Add(pwpAssetName);
            Plugin.Log?.LogInfo($"[Archipelago] Public Works check completed: {pwpAssetName}");
        }

        
        public static bool IsPWPCheckCompleted(string pwpAssetName)
        {
            if (CompletedPWPChecks.Contains(pwpAssetName)) return true;
            // Also check if the server already marked this location as checked
            if (PublicWorksLocations.All.TryGetValue(pwpAssetName, out long locId))
            {
                return ArchipelagoManager.IsLocationChecked(locId);
            }
            return false;
        }

        public static void ResetAndSyncPublicWorks()
        {
            var collections = Resources.FindObjectsOfTypeAll<PublicWorksProjectCollectionSO>();
            var purchasedCol = collections.FirstOrDefault(c => c.name == "Public Works Projects Purchased");
            if (purchasedCol == null || purchasedCol.collection == null) return;

            // re-lock all pubworks stuff
            var keys = purchasedCol.collection.Keys.ToList();
            foreach (var key in keys)
            {
                purchasedCol.collection[key] = false;
            }

            // clear vanilla purchases
            var toPurchaseLists = Resources.FindObjectsOfTypeAll<UnityAtoms.BobosWorld.PublicWorksProjectSOValueList>();
            var toPurchase = toPurchaseLists.FirstOrDefault(l => l.name == "Public Works Projects TOPurchase");
            toPurchase?.Clear();

            // re-enable only the ones given by archipelago
            foreach (var pwpName in ReceivedPWPItems)
            {
                var project = keys.FirstOrDefault(k => k.name == pwpName);
                if (project != null)
                {
                    purchasedCol.collection[project] = true;
                }
            }
            Plugin.Log?.LogInfo($"[Archipelago] Re-locked save's public works. Synced {ReceivedPWPItems.Count} AP-unlocked project(s).");
        }

        public static void SyncItemsFromServer()
        {
            if (!ArchipelagoManager.IsConnected || ArchipelagoManager.Session == null) return;
            var allItems = ArchipelagoManager.Session.Items.AllItemsReceived;

            ReceivedPWPItems.Clear();
            foreach (var item in allItems)
            {
                if (PublicWorksItems.All.TryGetValue(item.ItemId, out string pwpAssetName))
                {
                    ReceivedPWPItems.Add(pwpAssetName);
                }
            }
            
            ResetAndSyncPublicWorks();
            ForceRefreshCompetitions();
            Plugin.Log?.LogInfo($"[Archipelago] Full Sync Complete: Comps={ProgressiveCompetitionsReceived}, Sagas={ProgressiveSagasReceived}, Tickets={BoboTicketsReceived}, PWPs={ReceivedPWPItems.Count}");
        }

        public static void GrantProgressiveCompetitions()
        {
            // want to convert from unlocking competitions by rank
            // to unlocking sets of competitions to stagger the progression
            // ignore previous comments i did it yay
            Plugin.Log?.LogInfo($"[Archipelago] Progressive Competitions received ({ProgressiveCompetitionsReceived}).");
            ForceRefreshCompetitions();
        }

        public static void GrantBoboTicket()
        {
            Plugin.Log?.LogInfo($"[Archipelago] Bobo Ticket received ({BoboTicketsReceived}/{BoboTicketsRequired}).");
        }

        public static void SetBoboTicketsRequired(int required)
        {
            if (Plugin.BoboTicketsRequiredEntry != null)
                Plugin.BoboTicketsRequiredEntry.Value = required;
        }

        public static void ForceRefreshCompetitions()
        {
            var organizer = UnityEngine.Object.FindObjectOfType(typeof(CompetitionOrganizer)) as CompetitionOrganizer;
            if (organizer == null) return; // not in-game yet 

            var garden = Garden.Current;
            if (garden == null) return;

            var flags = BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance;
            var dateTimeSOField = typeof(Garden).GetField("_curDateTime", flags);
            object dateTimeSO = dateTimeSOField?.GetValue(garden);
            var valueProp = dateTimeSO?.GetType().GetProperty("Value", flags);
            object currentDate = valueProp?.GetValue(dateTimeSO);
            if (currentDate == null) return;

            var method = typeof(CompetitionOrganizer).GetMethod("SetTodaysCompetitions", flags);
            method?.Invoke(organizer, new object[] { currentDate });
            Plugin.Log?.LogInfo("[Archipelago] Forced competition/saga refresh after loading thresholds.");
        }
        
        public static void ApplySnackMultiplier(float multiplier)
        {
            if (multiplier <= 0f) multiplier = 1f;
            CurrentSnackMultiplier = multiplier;
            Common.DEFAULT_MINSTATUPDATE = (int)(BaseMinStat * multiplier);
            Common.DEFAULT_MAXSTATUPDATE = (int)(BaseMaxStat * multiplier);
            Plugin.Log?.LogInfo($"[Archipelago] Applied Snack Multiplier {multiplier}x: Min={Common.DEFAULT_MINSTATUPDATE}, Max={Common.DEFAULT_MAXSTATUPDATE}");
        }

        public static void SetUnlimitedSnacks(bool enabled)
        {
            UnlimitedSnacksEnabled = enabled;
            Plugin.Log?.LogInfo($"[Archipelago] Unlimited Snacks set to {enabled}");
        }

        public static void SpawnItemByAsset(string assetName)
        {
            var itemSO = UnityEngine.Resources.FindObjectsOfTypeAll<ItemScriptableObject>()
                .FirstOrDefault(i => i.name == assetName);

            if (itemSO == null)
            {
                Plugin.Log?.LogWarning($"[Archipelago] Could not find ItemScriptableObject for: '{assetName}'");
                return;
            }

            var garden = BobosWorld.Garden.Current;
            if (garden == null)
            {
                Plugin.Log?.LogWarning($"[Archipelago] Garden.Current is null; couldn't queue item '{assetName}'.");
                return;
            }

            var flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance;

            var itemInGardenType = typeof(BobosWorld.Garden).Assembly.GetTypes()
                .FirstOrDefault(t => t.Name == "ItemInGarden");
            if (itemInGardenType == null)
            {
                Plugin.Log?.LogWarning("[Archipelago] Could not find type ItemInGarden.");
                return;
            }

            var ctor = itemInGardenType.GetConstructor(flags, null,
                new[] { typeof(ItemScriptableObject), typeof(Vector4), typeof(int) }, null);
            if (ctor == null)
            {
                Plugin.Log?.LogWarning("[Archipelago] Could not find ItemInGarden(ItemScriptableObject, Vector4, int) constructor.");
                return;
            }

            object itemInGarden = ctor.Invoke(new object[] { itemSO, Vector4.zero, 0 });

            var queueField = typeof(Garden).GetField("_itemsToSpawnOnPlayer", flags);
            object queue = queueField?.GetValue(garden);
            if (queue == null)
            {
                Plugin.Log?.LogWarning("[Archipelago] Could not find _itemsToSpawnOnPlayer on Garden.Current.");
                return;
            }

            var addMethod = queue.GetType().GetMethod("Add", flags, null, new[] { itemInGardenType }, null);
            if (addMethod == null)
            {
                Plugin.Log?.LogWarning("[Archipelago] Could not find Add(ItemInGarden) on _itemsToSpawnOnPlayer.");
                return;
            }

            addMethod.Invoke(queue, new object[] { itemInGarden });

            var spawnItemsMethod = typeof(Garden).GetMethod("SpawnItems", flags);
            var spawnItemsRoutine = spawnItemsMethod?.Invoke(garden, null) as System.Collections.IEnumerator;
            if (spawnItemsRoutine != null)
                garden.StartCoroutine(spawnItemsRoutine);

            Plugin.Log?.LogInfo($"[Archipelago] Queued item to spawn on player: '{itemSO.name}' ({itemSO.LocalizedName})");
        }

        public static int ApplyFoodModToCurrentGarden()
        {
            var garden = Garden.Current;
            if (garden == null) return 0;

            var flags = BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance;
            var controllerListField = typeof(Garden).GetField("_controllerList", flags);
            var controllerList = controllerListField?.GetValue(garden) as System.Collections.IEnumerable;
            if (controllerList == null) return 0;
            
            int count = 0;
            foreach (var controller in controllerList)
            {
                count++;
                if (controller == null) { Plugin.Log?.LogWarning("[APDebug] FoodMod: null controller in list."); continue; }

                Plugin.Log?.LogInfo($"[APDebug] FoodMod: controller type = {controller.GetType().FullName}");

                var boboMember = controller.GetType().GetProperty("Bobo", flags) as MemberInfo
                            ?? controller.GetType().GetField("Bobo", flags);
                object bobo = boboMember == null ? null
                    : (boboMember is PropertyInfo bp ? bp.GetValue(controller) : ((FieldInfo)boboMember).GetValue(controller));

                if (bobo == null) { Plugin.Log?.LogWarning($"[APDebug] FoodMod: no 'Bobo' member found on {controller.GetType().Name}, or its value was null."); continue; }
                Plugin.Log?.LogInfo($"[APDebug] FoodMod: bobo type = {bobo.GetType().FullName}");

                var dataMember = bobo.GetType().GetProperty("Data", flags) as MemberInfo
                            ?? bobo.GetType().GetField("Data", flags);
                object data = dataMember == null ? null
                    : (dataMember is PropertyInfo dp ? dp.GetValue(bobo) : ((FieldInfo)dataMember).GetValue(bobo));

                if (data == null) { Plugin.Log?.LogWarning($"[APDebug] FoodMod: no 'Data' member found on {bobo.GetType().Name}, or its value was null."); continue; }
                Plugin.Log?.LogInfo($"[APDebug] FoodMod: data type = {data.GetType().FullName}");

                var foodModProp = data.GetType().GetProperty("FoodMod", flags);
                if (foodModProp == null) { Plugin.Log?.LogWarning($"[APDebug] FoodMod: no 'FoodMod' property on {data.GetType().Name}."); continue; }

                int before = (int)foodModProp.GetValue(data);
                foodModProp.SetValue(data, 999);
                int after = (int)foodModProp.GetValue(data);
                Plugin.Log?.LogInfo($"[APDebug] FoodMod: set on {bobo.GetType().Name} — before={before}, after={after}");
            }

            if (count > 0) Plugin.Log?.LogInfo($"[APDebug] FoodMod: applied to {count} controller(s).");
            return count;
        }

        private static void GrantMoney(int amount)
        {
            var save = SaveSystem.Instance;
            if (save == null)
            {
                Plugin.Log?.LogWarning("Archipelago: SaveSystem.Instance not ready yet, can't grant money.");
                return;
            }

            var moneyField = typeof(SaveSystem).GetField("_money", BindingFlags.NonPublic | BindingFlags.Instance);
            object moneyVar = moneyField?.GetValue(save);
            if (moneyVar == null)
            {
                Plugin.Log?.LogError("Archipelago: couldn't find _money field on SaveSystem.");
                return;
            }

            var addMethod = moneyVar.GetType().GetMethod("Add", new[] { typeof(int) });
            if (addMethod != null)
            {
                addMethod.Invoke(moneyVar, new object[] { amount });
            }
            else
            {
                var valueProp = moneyVar.GetType().GetProperty("Value");
                int current = (int)valueProp.GetValue(moneyVar);
                valueProp.SetValue(moneyVar, current + amount);
            }

            save.SaveMoney();
            Plugin.Log?.LogInfo($"[Archipelago] Granted {amount} bobo bucks.");
        }

        public static void GrantProgressiveSagas()
        {
            Plugin.Log?.LogInfo($"[Archipelago] Progressive Sagas received ({ProgressiveSagasReceived}).");
            ForceRefreshCompetitions();
        }

        public static void GrantReceivedItem(long itemID)
        {
            if(PublicWorksItems.All.TryGetValue(itemID, out string pwpAssetName))
            {
                GrantPublicWorksProject(pwpAssetName);
                return;
            }

            if (ItemAssets.All.TryGetValue(itemID, out string assetName))
            {
                SpawnItemByAsset(assetName);
                return;
            }

            switch (itemID)
            {
                case ProgressiveCompetitionsId:
                    GrantProgressiveCompetitions();
                    Plugin.Log?.LogInfo($"[Archipelago] Progressive Competitions received ({ProgressiveCompetitionsReceived}).");
                    break;
                case ProgressiveSagasId:
                    GrantProgressiveSagas();
                    Plugin.Log?.LogInfo($"[Archipelago] Progressive Sagas received ({ProgressiveSagasReceived}).");
                    break;
                case BoboTicketId:
                    GrantBoboTicket();
                    Plugin.Log?.LogInfo($"[Archipelago] Bobo Ticket received ({BoboTicketsReceived}/{BoboTicketsRequired}).");
                    break;
                case 20050090:
                    GrantMoney(300);
                    break;
                case 20050099:
                    Plugin.Log?.LogInfo("[Archipelago] VICTORY item received! Congratulations!");
                    break;
                default:
                    Plugin.Log?.LogWarning($"[Archipelago] Received unmapped item ID: {itemID}");
                    break;
            }
        }

        public static void GrantPublicWorksProject(string pwpAssetName)
        {
            ReceivedPWPItems.Add(pwpAssetName);

            var collections = Resources.FindObjectsOfTypeAll<PublicWorksProjectCollectionSO>();
            var purchasedCol = collections.FirstOrDefault(c => c.name == "Public Works Projects Purchased");
            
            if (purchasedCol == null) return;
            var project = purchasedCol.collection.Keys.FirstOrDefault(p => p.name == pwpAssetName);
            
            if (project != null)
            {
                purchasedCol.collection[project] = true;
                Plugin.Log?.LogInfo($"[Archipelago] Activated Public Works: {project.titleKey}");
            }
        }
    }
    public static class ArchipelagoManager
    {
        private static ArchipelagoSession _session;
        private static readonly ConcurrentQueue<long> PendingItems = new ConcurrentQueue<long>();
        private static volatile bool _pendingSync;
        public static ArchipelagoSession Session => _session;
        public static bool IsInBay { get;set; }

        public static int CountReceived(long itemId)
        {
            return _session?.Items.AllItemsReceived.Count(i => i.ItemId == itemId) ?? 0;
        }

        private static void OnItemReceived(ReceivedItemsHelper helper)
        {
            _pendingSync = true;

            while (helper.AllItemsReceived.Count > ArchipelagoItemHandler.CurrentItemIndex)
            {
                var item = helper.AllItemsReceived[(int)ArchipelagoItemHandler.CurrentItemIndex];
                
                Plugin.Log?.LogInfo($"[Archipelago] Processing item ID {item.ItemId} at index {ArchipelagoItemHandler.CurrentItemIndex}");
                PendingItems.Enqueue(item.ItemId);

                // Increment local index and save back to Archipelago server storage
                ArchipelagoItemHandler.CurrentItemIndex++;
                _session.DataStorage[Scope.Slot, "new_item_index"] = ArchipelagoItemHandler.CurrentItemIndex;
            }
        }

        public static void RequestSync()
        {
            _pendingSync = true;
        }

        public static void ProcessPendingSync()
        {
            if (!_pendingSync) return;

            _pendingSync = false;
            ArchipelagoItemHandler.SyncItemsFromServer();
        }

        public static void ProcessPendingItems()
        {
            if (!IsInBay) return;

            while (PendingItems.TryDequeue(out long itemId))
            {
                ArchipelagoItemHandler.GrantReceivedItem(itemId);
            }
        }

        public static bool IsLocationChecked(long locationId)
        {
            return _session?.Locations?.AllLocationsChecked?.Contains(locationId) ?? false;
        }

        public static void SendGoalComplete()
        {
            if (_session == null || !IsConnected)
            {
                Plugin.Log?.LogWarning("[Archipelago] Tried to send goal completion while disconnected.");
                return;
            }

            var packet = new StatusUpdatePacket { Status = ArchipelagoClientState.ClientGoal };
            _session.Socket.SendPacket(packet);
            Plugin.Log?.LogInfo("[Archipelago] Sent goal completion (ClientGoal) to server.");
        }

        private static Dictionary<string, int> ParseThresholds(object raw)
        {
            var result = new Dictionary<string, int>();
            if (raw == null) return result;

            Plugin.Log?.LogInfo($"[APDebug] competition_unlock_thresholds runtime type: {raw.GetType().FullName}");

            if (raw is Newtonsoft.Json.Linq.JObject jObj)
            {
                foreach (var prop in jObj.Properties())
                    result[prop.Name] = prop.Value.ToObject<int>();
                return result;
            }

            if (raw is System.Collections.IDictionary dict)
            {
                foreach (System.Collections.DictionaryEntry entry in dict)
                    result[entry.Key.ToString()] = Convert.ToInt32(entry.Value);
                return result;
            }

            Plugin.Log?.LogWarning($"[Archipelago] Unrecognized threshold payload type: {raw.GetType().FullName}");
            return result;
        }

        public static bool IsConnected { get; private set; } = false;
        public static string StatusMessage { get; private set; } = "Disconnected";

        public static void Connect()
        {
            string host = Plugin.ServerAddressEntry?.Value ?? "localhost:38281";
            string slot = Plugin.SlotNameEntry?.Value ?? "Player";
            string pass = Plugin.PasswordEntry?.Value ?? "";

            UpdateStatus($"Connecting to {host} as {slot}...");
            
            System.Threading.Tasks.Task.Run(() =>
            {
                try
                {
                    _session = ArchipelagoSessionFactory.CreateSession(host);
                    var result = _session.TryConnectAndLogin(
                        "Bobo Bay",                     // must match your apworld's game name
                        slot,
                        ItemsHandlingFlags.AllItems,
                        version: new Version(0, 6, 7),
                        password: string.IsNullOrEmpty(pass) ? null : pass);

                    if (result.Successful)
                    {
                        var success = (LoginSuccessful)result;
                        IsConnected = true;
                        UpdateStatus($"Connected to {host}");

                        try
                        {
                            ArchipelagoItemHandler.CurrentItemIndex =
                                _session.DataStorage[Scope.Slot, "new_item_index"].To<long>();
                        }
                        catch (ArgumentException)
                        {
                            ArchipelagoItemHandler.CurrentItemIndex = 0;
                            _session.DataStorage[Scope.Slot, "new_item_index"] = 0L;
                            Plugin.Log?.LogInfo("[Archipelago] No stored item index found; starting at index 0.");
                        }

                        if (success.SlotData.TryGetValue("goal_asset_name", out object goalObj))
                        {
                            ArchipelagoItemHandler.GoalAssetName = goalObj.ToString() ?? "BigJam_Race_D";
                            Plugin.Log?.LogInfo($"[Archipelago] Goal for this seed: {ArchipelagoItemHandler.GoalAssetName}");
                        }
                        if (success.SlotData.TryGetValue("goal_saga_name", out object goalSagaObj))
                        {
                            ArchipelagoItemHandler.GoalSagaName = goalSagaObj?.ToString() ?? "";
                        }
                        if (success.SlotData.TryGetValue("bobo_tickets_required", out object ticketsObj))
                        {
                            ArchipelagoItemHandler.SetBoboTicketsRequired(Convert.ToInt32(ticketsObj));
                        }
                        if (success.SlotData.TryGetValue("snack_multiplier", out object multObj))
                        {
                            float mult = Convert.ToSingle(multObj);
                            ArchipelagoItemHandler.ApplySnackMultiplier(mult);
                        }
                        if (success.SlotData.TryGetValue("unlimited_snacks", out object unlimitedObj))
                        {
                            bool unlimited = Convert.ToBoolean(unlimitedObj);
                            ArchipelagoItemHandler.SetUnlimitedSnacks(unlimited);
                        }
                        if (success.SlotData.TryGetValue("competition_unlock_thresholds", out object thresholdsObj))
                        {
                            ArchipelagoItemHandler.CompetitionUnlockThresholds = ParseThresholds(thresholdsObj);
                            Plugin.Log?.LogInfo($"[Archipelago] Loaded {ArchipelagoItemHandler.CompetitionUnlockThresholds.Count} competition unlock threshold(s).");
                        }
                        if (success.SlotData.TryGetValue("saga_unlock_thresholds", out object sagaThresholdsObj))
                        {
                            ArchipelagoItemHandler.SagaUnlockThresholds = ParseThresholds(sagaThresholdsObj);
                            Plugin.Log?.LogInfo($"[Archipelago] Loaded {ArchipelagoItemHandler.SagaUnlockThresholds.Count} saga unlock threshold(s).");
                        }

                        _session.Items.ItemReceived += OnItemReceived;

                        RequestSync();
                    }
                    else
                    {
                        var failure = (LoginFailure)result;
                        IsConnected = false;
                        UpdateStatus($"[Archipelago] Connection Failed: " + string.Join(", ", failure.Errors));
                    }
                }
                catch (Exception ex)
                {
                    IsConnected = false;
                    UpdateStatus($"[Archipelago] Connection Failed: {ex.Message}");
                    Plugin.Log?.LogError($"[Archipelago] Archipelago connection exception: {ex}");
                }
            });
        }

        public static void Disconnect()
        {
            _session?.Socket.DisconnectAsync();
            IsConnected = false;
            UpdateStatus("Disconnected");
        }

        public static void CheckLocation(long locationId)
        {
            if (!IsConnected) { Plugin.Log?.LogWarning($"Location {locationId} checked while offline."); return; }
            _session.Locations.CompleteLocationChecks(locationId);
        }

        private static void UpdateStatus(string message)
        {
            StatusMessage = message;
            Plugin.Log?.LogInfo($"[Archipelago] Archipelago Status: {message}");
        }
    }
}