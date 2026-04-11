# Superpowers Marketplace

A catalog of Claude Code skills and plugins that extend Claude's capabilities for this project.

## What Is This?

The Superpowers Marketplace is a curated registry of installable skills for Claude Code. Each entry in the catalog describes a skill: what it does, how to install it, and what commands it exposes.

## Directory Structure

```
superpowers-marketplace/
├── .claude-plugin/
│   └── marketplace.json   # Plugin catalog (source of truth)
└── README.md              # This file
```

## How to Browse

The full catalog lives in `.claude-plugin/marketplace.json`. Each skill entry includes:

- **id** – unique identifier
- **name** – human-readable name
- **description** – what the skill does
- **version** – current release
- **category** – functional grouping
- **commands** – slash commands the skill exposes
- **installation** – how to add it to your Claude Code session

## How to Install a Skill

1. Copy the skill's `installation.source` URL.
2. In your Claude Code session run:
   ```
   /install <source-url>
   ```
3. The new slash commands listed under `commands` will be available immediately.

## Categories

| Category | Description |
|---|---|
| `productivity` | Automate repetitive development tasks |
| `testing` | Generate, run, and analyse tests |
| `documentation` | Create and maintain docs and diagrams |
| `data` | Parse, transform, and process data files |
| `devops` | CI/CD, deployment, and infrastructure helpers |

## Contributing

To add a new skill to the marketplace, open a pull request that adds an entry to `.claude-plugin/marketplace.json` following the existing schema.
