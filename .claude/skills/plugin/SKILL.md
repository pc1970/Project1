---
name: plugin
description: >
  Superpowers Marketplace skill for Claude Code. Browse, search, install, and
  uninstall Claude Code skills from the project's skill catalog.
  TRIGGER when: user says "/plugin", "install a skill", "browse skills",
  "what skills are available", or "uninstall skill".
---

# Plugin Skill — Superpowers Marketplace

Browse and manage Claude Code skills from the marketplace catalog.

## Marketplace Location

The catalog is at:
```
superpowers-marketplace/.claude-plugin/marketplace.json
```

Skills are installed to:
```
~/.claude/skills/<name>/SKILL.md     ← user-level (available in all projects)
.claude/skills/<name>/SKILL.md       ← project-level (this project only)
```

## Workflow

Make a todo list for the tasks in this workflow and work through them one at a time.

---

### 1. Identify the Command

| User says | Action |
|---|---|
| `/plugin list` or "what skills are available" | List all skills in catalog |
| `/plugin search <query>` | Search by name, tag, or description |
| `/plugin info <name>` | Show full details for one skill |
| `/plugin install <name>` | Install a skill |
| `/plugin uninstall <name>` | Remove an installed skill |
| `/plugin installed` | List currently installed skills |

---

### 2. Load the Catalog

```python
import json, os

CATALOG_PATH = "superpowers-marketplace/.claude-plugin/marketplace.json"
SKILLS_DIR   = os.path.expanduser("~/.claude/skills")   # user-level
PROJECT_SKILLS_DIR = ".claude/skills"                    # project-level

def load_catalog() -> dict:
    with open(CATALOG_PATH) as f:
        return json.load(f)

def installed_skills() -> set[str]:
    """Return names of all currently installed skills (user + project level)."""
    installed = set()
    for base in [SKILLS_DIR, PROJECT_SKILLS_DIR]:
        if os.path.isdir(base):
            for name in os.listdir(base):
                if os.path.isfile(os.path.join(base, name, "SKILL.md")):
                    installed.add(name)
    return installed
```

---

### 3. List All Skills

```python
def list_skills() -> None:
    catalog = load_catalog()
    installed = installed_skills()

    print(f"\n{'Superpowers Marketplace':^60}")
    print(f"{'─' * 60}")
    print(f"{'Skill':<14} {'Category':<12} {'Installed':<10} Description")
    print(f"{'─' * 60}")

    for skill in catalog["skills"]:
        status = "✅" if skill["name"] in installed else "  "
        desc = skill["description"][:38] + "…" if len(skill["description"]) > 38 else skill["description"]
        print(f"{skill['name']:<14} {skill['category']:<12} {status:<10} {desc}")

    print(f"\n{len(catalog['skills'])} skill(s) in catalog  |  {len(installed)} installed")
    print("Use /plugin install <name> to install a skill.\n")
```

---

### 4. Search Skills

```python
def search_skills(query: str) -> None:
    catalog = load_catalog()
    installed = installed_skills()
    q = query.lower()

    matches = [
        s for s in catalog["skills"]
        if q in s["name"] or q in s["description"].lower()
        or any(q in tag for tag in s.get("tags", []))
    ]

    if not matches:
        print(f"No skills found matching '{query}'.")
        return

    print(f"\nSearch results for '{query}':")
    for s in matches:
        status = "✅ installed" if s["name"] in installed else "not installed"
        print(f"  {s['name']:14} — {s['description'][:50]}  [{status}]")
```

---

### 5. Show Skill Info

```python
def skill_info(name: str) -> None:
    catalog = load_catalog()
    installed = installed_skills()
    skill = next((s for s in catalog["skills"] if s["name"] == name), None)

    if not skill:
        print(f"Skill '{name}' not found in catalog. Use /plugin list to see all skills.")
        return

    status = "✅ Installed" if name in installed else "Not installed"
    print(f"""
Name        : {skill['name']}
Display     : {skill['display_name']}
Version     : {skill['version']}
Category    : {skill['category']}
Author      : {skill['author']}
Status      : {status}
Tags        : {', '.join(skill.get('tags', []))}
Requires    : {', '.join(skill.get('requires', []))}

Description :
  {skill['description']}
""")
```

---

### 6. Install a Skill

```python
import shutil, subprocess

def install_skill(name: str, scope: str = "user") -> None:
    """
    Install a skill from the marketplace.
    scope: "user"    → ~/.claude/skills/ (available everywhere)
           "project" → .claude/skills/   (this project only)
    """
    catalog = load_catalog()
    skill = next((s for s in catalog["skills"] if s["name"] == name), None)

    if not skill:
        print(f"Skill '{name}' not found in catalog.")
        return

    # Source SKILL.md from the project's own skills directory
    src = os.path.join(PROJECT_SKILLS_DIR, name, "SKILL.md")
    if not os.path.isfile(src):
        src = skill["source"]  # fallback to catalog path

    if not os.path.isfile(src):
        print(f"Source SKILL.md not found at: {src}")
        return

    # Destination
    dest_dir = os.path.join(SKILLS_DIR if scope == "user" else PROJECT_SKILLS_DIR, name)
    dest = os.path.join(dest_dir, "SKILL.md")

    if os.path.isfile(dest):
        print(f"Skill '{name}' is already installed at {dest}.")
        return

    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(src, dest)
    print(f"✅ Installed '{name}' → {dest}")

    # Install required Python libraries
    requires = skill.get("requires", [])
    if requires:
        print(f"   Installing dependencies: {', '.join(requires)}")
        subprocess.run(["pip3", "install", "--quiet"] + requires, check=True)
        print(f"   Dependencies installed.")
```

---

### 7. Uninstall a Skill

```python
def uninstall_skill(name: str) -> None:
    """Remove a skill from user-level and/or project-level skills directories."""
    removed = []
    for base in [SKILLS_DIR, PROJECT_SKILLS_DIR]:
        skill_dir = os.path.join(base, name)
        skill_file = os.path.join(skill_dir, "SKILL.md")
        if os.path.isfile(skill_file):
            os.remove(skill_file)
            # Remove directory if now empty
            if not os.listdir(skill_dir):
                os.rmdir(skill_dir)
            removed.append(base)

    if removed:
        for loc in removed:
            print(f"🗑️  Removed '{name}' from {loc}")
    else:
        print(f"Skill '{name}' is not installed.")
```

---

### 8. Full CLI Dispatcher

```python
import sys

def main(args: list[str]) -> None:
    if not args:
        list_skills()
        return

    command = args[0].lower()

    if command == "list":
        list_skills()
    elif command == "installed":
        names = installed_skills()
        print(f"\nInstalled skills ({len(names)}):")
        for n in sorted(names):
            print(f"  /{n}")
    elif command == "search" and len(args) > 1:
        search_skills(" ".join(args[1:]))
    elif command == "info" and len(args) > 1:
        skill_info(args[1])
    elif command == "install" and len(args) > 1:
        scope = "project" if "--project" in args else "user"
        install_skill(args[1], scope=scope)
    elif command == "uninstall" and len(args) > 1:
        uninstall_skill(args[1])
    else:
        print("""
Usage:
  /plugin list                  — browse all available skills
  /plugin search <query>        — search by name, tag, or description
  /plugin info <name>           — show full details for a skill
  /plugin install <name>        — install to ~/.claude/skills/ (user-level)
  /plugin install <name> --project  — install to .claude/skills/ (project-level)
  /plugin uninstall <name>      — remove an installed skill
  /plugin installed             — list currently installed skills
""")

# Example invocations:
# main(["list"])
# main(["search", "excel"])
# main(["install", "xlsx"])
# main(["info", "office"])
```

---

## Adding Skills to the Catalog

To register a new skill in the marketplace, add an entry to
`superpowers-marketplace/.claude-plugin/marketplace.json`:

```json
{
  "name": "my-skill",
  "display_name": "My Skill",
  "version": "1.0.0",
  "description": "What this skill does.",
  "author": "your-name",
  "category": "category-name",
  "tags": ["tag1", "tag2"],
  "source": ".claude/skills/my-skill/SKILL.md",
  "requires": ["some-pip-package"]
}
```

Then place the `SKILL.md` at the path specified in `source`.

---

## Wrap Up

After each command, report back:

```
Command : /plugin install xlsx
Result  : ✅ Installed 'xlsx' → /root/.claude/skills/xlsx/SKILL.md
Deps    : openpyxl, pandas, xlrd — already satisfied
```
