import os

FILE_PATH = 'docs/index.html'

def update_file():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"Read {len(content)} bytes from {FILE_PATH}")

    # 1. Update Localization Title
    # Search: settingsTitle: "Debug Panel"
    # Replace: settingsTitle: "Settings"
    target_1 = 'settingsTitle: "Debug Panel"'
    if target_1 not in content:
        print("Warning: Localization string not found.")
    else:
        content = content.replace(target_1, 'settingsTitle: "Settings"')
        print("Updated settingsTitle.")

    # 2. Inject DataManagementPanel Component
    # Search: const DebugPanel =
    # Replace: const DataManagementPanel = ... ; const DebugPanel =
    dm_panel_code = "const DataManagementPanel = () => { const panel = createEl('div', {className: 'card mb-3'}); panel.innerHTML = `<div class=\"card-header bg-light\"><span class=\"emoji-icon\">💾</span>Data Management</div><div class=\"card-body d-flex gap-2 flex-wrap\"><button class=\"btn btn-primary\" onclick=\"NoodleNudge.SettingsManager.exportData()\"><span class=\"emoji-icon\">📥</span>${NoodleNudge.L10N.get('exportData')}</button><button class=\"btn btn-outline-primary\" onclick=\"document.getElementById('import-file').click()\"><span class=\"emoji-icon\">📤</span>${NoodleNudge.L10N.get('importData')}</button><input type=\"file\" id=\"import-file\" style=\"display:none\" accept=\".json\" onchange=\"NoodleNudge.SettingsManager.importData(event)\"><button class=\"btn btn-outline-danger ms-auto\" onclick=\"NoodleNudge.SettingsManager.resetData()\"><span class=\"emoji-icon\">🗑️</span>${NoodleNudge.L10N.get('resetData')}</button></div>`; return panel; }; "

    target_2 = 'const DebugPanel ='
    if target_2 not in content:
         print("Error: const DebugPanel not found.")
         return
    else:
        content = content.replace(target_2, dm_panel_code + target_2)
        print("Injected DataManagementPanel.")

    # 3. Update SettingsView to use it and change icon
    # Search: appRoot.innerHTML = `<h2><span class="emoji-icon">🐞</span>${L.get('settingsTitle')}</h2>`;
    # Replace: appRoot.innerHTML = `<h2><span class="emoji-icon">⚙️</span>${L.get('settingsTitle')}</h2>`; appRoot.appendChild(DataManagementPanel());

    old_view = "appRoot.innerHTML = `<h2><span class=\"emoji-icon\">🐞</span>${L.get('settingsTitle')}</h2>`;"
    new_view = "appRoot.innerHTML = `<h2><span class=\"emoji-icon\">⚙️</span>${L.get('settingsTitle')}</h2>`; appRoot.appendChild(DataManagementPanel());"

    if old_view not in content:
        print("Error: SettingsView innerHTML line not found.")
        # Try finding partial matches if specific formatting differs
        if "appRoot.innerHTML" in content and "settingsTitle" in content:
            print("Context exists but exact match failed. Content dump around SettingsView:")
            idx = content.find("const SettingsView")
            print(content[idx:idx+300])
        return
    else:
        content = content.replace(old_view, new_view)
        print("Updated SettingsView.")

    # 4. Update Nav Icon
    # Search: <a href="#" data-nav="settings" class="nav-link">🐞</a>
    # Replace: <a href="#" data-nav="settings" class="nav-link">⚙️</a>
    target_4 = 'data-nav="settings" class="nav-link">🐞</a>'
    if target_4 in content:
         content = content.replace(target_4, 'data-nav="settings" class="nav-link">⚙️</a>')
         print("Updated Nav Icon.")
    else:
         print("Warning: Nav icon not found (might vary in attr order).")

    # 5. Remove Visibility Logic in App.init
    # Search: if (!MasterBlueprint.featureFlags.enableDebugPanel) { document.querySelectorAll('[data-nav="settings"]').forEach(el => el.closest('li').style.display = 'none'); }
    # Replace: /* Settings enabled */

    init_logic = "if (!MasterBlueprint.featureFlags.enableDebugPanel) { document.querySelectorAll('[data-nav=\"settings\"]').forEach(el => el.closest('li').style.display = 'none'); }"
    if init_logic in content:
        content = content.replace(init_logic, "/* Settings enabled */")
        print("Enabled Settings Navigation.")
    else:
        print("Warning: Init visibility logic not found.")

    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully updated docs/index.html")

if __name__ == "__main__":
    update_file()
