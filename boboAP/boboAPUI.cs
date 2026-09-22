using System;
using System.Reflection;
using HarmonyLib;
using UnityEngine;
using UnityEngine.UI;

namespace BoboBayArchipelago
{
    /// Injects an "Archipelago" tab into BobosWorld.UISettings using live game clones.
    [HarmonyPatch(typeof(BobosWorld.UISettings), "OnEnable")]
    public static class ArchipelagoUI_OnEnable
    {
        [HarmonyPostfix]
        static void Postfix(BobosWorld.UISettings __instance)
            => ArchipelagoUI.ApplyPostfix(__instance);
    }

    [HarmonyPatch(typeof(BobosWorld.UISettings), "SetUI")]
    public static class ArchipelagoUI_SetUI
    {
        [HarmonyPostfix]
        static void Postfix(BobosWorld.UISettings __instance)
            => ArchipelagoUI.ApplyPostfix(__instance);
    }

    public static class ArchipelagoUI
    {
        private static readonly Assembly GameAsm = typeof(BobosWorld.UISettings).Assembly;

        public static void ApplyPostfix(BobosWorld.UISettings __instance)
        {
            try
            {
                var trav = Traverse.Create(__instance);
                RectTransform videoTab    = trav.Field("_videoTab").GetValue<RectTransform>();
                RectTransform audioTab    = trav.Field("_audioTab").GetValue<RectTransform>();
                RectTransform controlsTab = trav.Field("_controlsTab").GetValue<RectTransform>();
                Button audioButton        = trav.Field("_audioButton").GetValue<Button>();
                Button videoButton        = trav.Field("_videoButton").GetValue<Button>();
                Button controlsButton     = trav.Field("_controlsButton").GetValue<Button>();

                if (videoTab == null || audioButton == null) return;

                Transform tabParent = videoTab.parent;
                Transform navParent = audioButton.transform.parent;
                Transform apTabT   = tabParent != null ? tabParent.Find("ArchipelagoTab") : null;
                Transform apBtnT   = navParent != null ? navParent.Find("ArchipelagoButton") : null;

                if (apTabT == null || apBtnT == null)
                {
                    Build(videoTab, audioTab, controlsTab, audioButton, videoButton, controlsButton);
                    apTabT = tabParent != null ? tabParent.Find("ArchipelagoTab") : null;
                    apBtnT = navParent != null ? navParent.Find("ArchipelagoButton") : null;
                }

                if (apTabT != null) apTabT.gameObject.SetActive(false);
                if (apBtnT != null)
                {
                    var b = apBtnT.GetComponent<Button>();
                    if (b != null) b.interactable = true;
                }
            }
            catch (Exception ex)
            {
                Plugin.Log?.LogError("ArchipelagoUI: Failed to inject tab: " + ex);
            }
        }
        

        private static void Build(
            RectTransform videoTab, RectTransform audioTab, RectTransform controlsTab,
            Button audioButton, Button videoButton, Button controlsButton)
        {
            Plugin.Log?.LogInfo("ArchipelagoUI: Building Archipelago Tab...");

            GameObject apTab = UnityEngine.Object.Instantiate(videoTab.gameObject, videoTab.parent);
            apTab.name = "ArchipelagoTab";
            apTab.SetActive(false);

            var vlg = apTab.GetComponentInChildren<VerticalLayoutGroup>(true);
            Transform rowParent = vlg != null ? vlg.transform : apTab.transform;

            if (vlg != null)
            {
                vlg.childForceExpandHeight = false;
                vlg.childAlignment = TextAnchor.UpperLeft;
            }

            // Clear native copied template rows
            for (int i = rowParent.childCount - 1; i >= 0; i--)
                UnityEngine.Object.Destroy(rowParent.GetChild(i).gameObject);

            // Locate base templates for cloning UI components
            GameObject toggleTemplate     = FindRowTemplate<Toggle>(controlsTab) ?? FindRowTemplate<Toggle>(videoTab);
            GameObject inputFieldTemplate = FindInputFieldTemplate(controlsTab) ?? FindInputFieldTemplate(videoTab);

            // ── Section 1: Connection Settings ──────────────────────────────────────
            CloneHeader(toggleTemplate, rowParent, "AP_Header", "Archipelago Connection");

            // Server Address / Port Input
            BuildInputFieldRow("Server (Host:Port)", 
                Plugin.ServerAddressEntry?.Value ?? "archipelago.gg:38281", 
                inputFieldTemplate, 
                toggleTemplate, 
                rowParent, 
                val => {
                if(Plugin.ServerAddressEntry != null) Plugin.ServerAddressEntry.Value = val;
            });

            // Player / Slot Name Input
            BuildInputFieldRow("Slot Name", 
                Plugin.SlotNameEntry?.Value ?? "BoboPlayer", 
                inputFieldTemplate, 
                toggleTemplate, 
                rowParent, 
                val => {
                if(Plugin.SlotNameEntry != null) Plugin.SlotNameEntry.Value = val;
            });

            // Password Input
            BuildInputFieldRow("Password", 
                Plugin.PasswordEntry?.Value ?? "", 
                inputFieldTemplate, 
                toggleTemplate, 
                rowParent, 
                val => {
                if(Plugin.PasswordEntry != null) Plugin.PasswordEntry.Value = val;
            });

            // ── Section 2: Action & Status ──────────────────────────────────────────
            // Connect / Disconnect Action Button
            GameObject btnRow = CloneRow(toggleTemplate ?? audioButton.gameObject, rowParent, "AP_ConnectRow");
            Button actionBtn = btnRow.GetComponentInChildren<Button>(true);
            if (actionBtn == null) actionBtn = btnRow.AddComponent<Button>();

            var refresher = btnRow.AddComponent<ConnectButtonRefresher>();
            refresher.Row = btnRow;

            actionBtn.onClick.RemoveAllListeners();
            actionBtn.onClick.AddListener(() =>
            {
                if (ArchipelagoManager.IsConnected)
                    ArchipelagoManager.Disconnect();
                else
                    ArchipelagoManager.Connect();
            });

            // ── Section 3: Navigation Button Setup ─────────────────────────────────
            GameObject apButtonGo = UnityEngine.Object.Instantiate(audioButton.gameObject, audioButton.transform.parent);
            apButtonGo.name = "ArchipelagoButton";
            apButtonGo.SetActive(true);
            StripGameBinders(apButtonGo);

            Button apButton = apButtonGo.GetComponent<Button>();
            SetButtonLabel(apButtonGo, "Archipelago");

            if (apButton != null)
            {
                apButton.onClick.RemoveAllListeners();
                apButton.onClick.AddListener(() =>
                {
                    if (apTab != null) apTab.SetActive(true);
                    if (audioTab != null) audioTab.gameObject.SetActive(false);
                    if (videoTab != null) videoTab.gameObject.SetActive(false);
                    if (controlsTab != null) controlsTab.gameObject.SetActive(false);

                    apButton.interactable = false;
                    if (audioButton != null) audioButton.interactable = true;
                    if (videoButton != null) videoButton.interactable = true;
                    if (controlsButton != null) controlsButton.interactable = true;
                });
            }

            SetAutoNav(audioButton);
            SetAutoNav(videoButton);
            SetAutoNav(controlsButton);
            SetAutoNav(apButton);

            AddHideTab(audioButton, apTab, apButton);
            AddHideTab(videoButton, apTab, apButton);
            AddHideTab(controlsButton, apTab, apButton);
        }

        // ── Helper Methods ───────────────────────────────────────────────────────

        private static void BuildInputFieldRow(
            string labelText, string initialValue, GameObject inputTemplate,
            GameObject fallbackTemplate, Transform parent, Action<string> onValueChanged)
        {
            GameObject rowTemplate = inputTemplate ?? fallbackTemplate;
            if (rowTemplate == null) return;

            GameObject row = CloneRow(rowTemplate, parent, "Row_" + labelText);
            SetRowLabel(row, labelText);

            // Attempt to resolve regular uGUI InputField or TMPro TMP_InputField reflectively
            Component inputComp = row.GetComponentInChildren<InputField>(true) as Component;
            if (inputComp == null) inputComp = FindInputFieldComponent(row);

            if (inputComp != null)
            {
                SetTextOn(inputComp, initialValue);

                // Add listener dynamically based on available component reflection
                var onEndEditProp = inputComp.GetType().GetProperty("onEndEdit");
                if (onEndEditProp != null)
                {
                    var unityEvent = onEndEditProp.GetValue(inputComp, null);
                    var addListenerMethod = unityEvent.GetType().GetMethod("AddListener");
                    if (addListenerMethod != null)
                    {
                        UnityEngine.Events.UnityAction<string> action = new UnityEngine.Events.UnityAction<string>(onValueChanged);
                        addListenerMethod.Invoke(unityEvent, new object[] { action });
                    }
                }
            }
        }

        private class ConnectButtonRefresher : MonoBehaviour
        {
            public GameObject Row;
            private bool _lastConnected;
            private bool _initialized;

            void Update()
            {
                bool connected = ArchipelagoManager.IsConnected;
                if (!_initialized || connected != _lastConnected)
                {
                    _initialized = true;
                    _lastConnected = connected;
                    SetButtonLabel(Row, connected ? "Disconnect" : "Connect");
                }
            }
        }

        private static GameObject FindInputFieldTemplate(RectTransform tab)
        {
            if (tab == null) return null;
            foreach (var comp in tab.GetComponentsInChildren<Component>(true))
            {
                if (comp == null) continue;
                Type t = comp.GetType();
                if (t == typeof(InputField) || t.Name == "TMP_InputField")
                {
                    Transform parent = comp.transform;
                    while (parent.parent != null && parent.parent.GetComponent<VerticalLayoutGroup>() == null)
                        parent = parent.parent;
                    return parent.gameObject;
                }
            }
            return null;
        }

        private static Component FindInputFieldComponent(GameObject root)
        {
            foreach (var comp in root.GetComponentsInChildren<Component>(true))
            {
                if (comp == null) continue;
                Type t = comp.GetType();
                if (t == typeof(InputField) || t.Name == "TMP_InputField") return comp;
            }
            return null;
        }

        private static GameObject FindRowTemplate<T>(RectTransform tab) where T : Component
        {
            if (tab == null) return null;
            foreach (var comp in tab.GetComponentsInChildren<T>(true))
            {
                if (comp == null) continue;
                Transform t = comp.transform;
                while (t.parent != null && t.parent.GetComponent<VerticalLayoutGroup>() == null)
                    t = t.parent;
                return t.gameObject;
            }
            return null;
        }

        private static GameObject CloneRow(GameObject template, Transform parent, string name)
        {
            GameObject row = UnityEngine.Object.Instantiate(template, parent);
            row.name = name;
            row.SetActive(true);
            StripGameBinders(row);
            return row;
        }

        private static GameObject CloneHeader(GameObject template, Transform parent, string name, string label)
        {
            if (template == null) return null;
            GameObject row = CloneRow(template, parent, name);
            foreach (var sel in row.GetComponentsInChildren<Selectable>(true))
            {
                if (sel.targetGraphic != null) sel.targetGraphic.enabled = false;
                UnityEngine.Object.Destroy(sel);
            }
            SetRowLabel(row, label);
            return row;
        }

        private static void StripGameBinders(GameObject root)
        {
            foreach (var comp in root.GetComponentsInChildren<Component>(true))
            {
                if (comp == null) continue;
                Type ct = comp.GetType();
                bool gameBinder = ct.Assembly == GameAsm;
                bool modular = ct.Namespace != null && ct.Namespace.StartsWith("ModularOptions");
                if (gameBinder || modular) UnityEngine.Object.Destroy(comp);
            }
        }

        private static void SetAutoNav(Button b)
        {
            if (b == null) return;
            var nav = b.navigation;
            nav.mode = Navigation.Mode.Automatic;
            b.navigation = nav;
        }

        private static void AddHideTab(Button b, GameObject apTab, Button apButton)
        {
            if (b == null) return;
            b.onClick.AddListener(() =>
            {
                if (apTab != null) apTab.SetActive(false);
                if (apButton != null) apButton.interactable = true;
            });
        }

        private static void SetRowLabel(GameObject row, string label)
        {
            Component node = FindTextNode(row, "label") ?? FindTextNode(row, "option");
            if (node != null) { SetTextOn(node, label); return; }
            if (SetTextOnAllMatches(row, label)) return;
        }

        private static void SetButtonLabel(GameObject button, string label) => SetTextOnAllMatches(button, label);

        private static Component FindTextNode(GameObject root, string nameSub)
        {
            foreach (var comp in root.GetComponentsInChildren<Component>(true))
            {
                if (comp == null) continue;
                Type t = comp.GetType();
                bool isText = typeof(Text).IsAssignableFrom(t) || IsTmpText(t);
                if (isText && comp.name.IndexOf(nameSub, StringComparison.OrdinalIgnoreCase) >= 0) return comp;
            }
            return null;
        }

        private static void SetTextOn(Component comp, string value)
        {
            if (comp == null) return;
            var prop = comp.GetType().GetProperty("text", BindingFlags.Public | BindingFlags.Instance);
            if (prop != null && prop.CanWrite && prop.PropertyType == typeof(string))
                prop.SetValue(comp, value, null);
        }

        private static bool SetTextOnAllMatches(GameObject root, string value)
        {
            bool any = false;
            foreach (var comp in root.GetComponentsInChildren<Component>(true))
            {
                if (comp == null) continue;
                Type t = comp.GetType();
                if (typeof(Text).IsAssignableFrom(t) || IsTmpText(t))
                {
                    SetTextOn(comp, value);
                    any = true;
                }
            }
            return any;
        }
        
        private static bool IsTmpText(Type t)
        {
            for (var cur = t; cur != null; cur = cur.BaseType)
            {
                if (cur.FullName == "TMPro.TMP_Text") return true;
            }
            return false;
        }
    }
}