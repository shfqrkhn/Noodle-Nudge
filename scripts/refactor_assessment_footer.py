import os

FILE_PATH = 'docs/index.html'

def update_file():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Target String (from grep)
    # form.innerHTML += `<div class="mt-4 d-flex justify-content-between"><button type="button" class="btn btn-secondary" data-nav="assessments"><span class="emoji-icon">⬅️</span> ${NoodleNudge.L10N.get('backToList')}</button><button type="submit" class="btn btn-primary">${NoodleNudge.L10N.get('submitAnswers')} <span class="emoji-icon">✔️</span></button></div>`;

    target_str = "form.innerHTML += `<div class=\"mt-4 d-flex justify-content-between\"><button type=\"button\" class=\"btn btn-secondary\" data-nav=\"assessments\"><span class=\"emoji-icon\">⬅️</span> ${NoodleNudge.L10N.get('backToList')}</button><button type=\"submit\" class=\"btn btn-primary\">${NoodleNudge.L10N.get('submitAnswers')} <span class=\"emoji-icon\">✔️</span></button></div>`;"

    # Replacement Code
    # const footer = createEl('div', { className: 'mt-4 d-flex justify-content-between' });
    # footer.innerHTML = `<button type="button" class="btn btn-secondary" data-nav="assessments"><span class="emoji-icon">⬅️</span> ${NoodleNudge.L10N.get('backToList')}</button><button type="submit" class="btn btn-primary">${NoodleNudge.L10N.get('submitAnswers')} <span class="emoji-icon">✔️</span></button>`;
    # form.appendChild(footer);

    replacement_code = "const footer = createEl('div', { className: 'mt-4 d-flex justify-content-between' }); footer.innerHTML = `<button type=\"button\" class=\"btn btn-secondary\" data-nav=\"assessments\"><span class=\"emoji-icon\">⬅️</span> ${NoodleNudge.L10N.get('backToList')}</button><button type=\"submit\" class=\"btn btn-primary\">${NoodleNudge.L10N.get('submitAnswers')} <span class=\"emoji-icon\">✔️</span></button>`; form.appendChild(footer);"

    if target_str in content:
        content = content.replace(target_str, replacement_code)
        print("Target found and replaced.")
    else:
        print("Error: Target string not found.")
        # Debugging aid
        print("Search string:", target_str[:50], "...")
        return

    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Successfully updated docs/index.html")

if __name__ == "__main__":
    update_file()
