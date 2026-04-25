# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is a **Claude Code workspace**, not an application. It is a curated
collection of skills, a local plugin marketplace, session hooks, and an
installer — all intended to be consumed by the `claude` CLI (local or web).

There is no build step, no test suite, and no compiled artifact. "Working on
this repo" means editing skill definitions, marketplace metadata, hook
scripts, or the installer.

## Layout that matters

- `.claude/settings.json` — project-scoped Claude Code config. Registers the
  `SessionStart` hook, allow-lists the office `Skill(...)` invocations, and
  pre-enables plugins from two external marketplaces:
  `wshobson/agents` (as `claude-code-workflows`) and `major7apps/pensyve`.
  When adding skills or plugins that should ship with the workspace, wire
  them in here.
- `.claude/hooks/session-start.sh` — runs on session start. **Only executes
  when `CLAUDE_CODE_REMOTE=true`** (Claude Code on the web); local sessions
  exit immediately. It installs the Python libraries the office skills
  depend on. The first line of real stdout must stay as
  `{"async": true, "asyncTimeout": 300000}` — the harness parses it.
- `.claude/skills/` — 60+ skill directories. Each is a self-contained
  `SKILL.md` + supporting files, consumed by Claude via the `Skill` tool.
- `superpowers-marketplace/` — a local marketplace the workspace itself
  exposes. `.claude-plugin/marketplace.json` is the catalog; entries point at
  skill dirs under `.claude/skills/` or at the bundled
  `plugins/office-tools/` plugin (agent + slash command + skills).
- `skills-lock.json` — lockfile recording `source`, `sourceType`, and
  `computedHash` per installed skill. Edit this whenever a skill is added,
  removed, or refreshed so the recorded hash matches on-disk content.
- `scripts/install.sh` — the `curl | bash` installer. See below.
- `ethical-hacking-agent-prompt.md` — standalone system-prompt document
  (RedCell). Reference material only; not wired into any skill or agent.

## The installer (`scripts/install.sh`)

One-line entry point for setting up this workspace on a new machine:

```bash
# default: clone + install Python office libs + chmod hooks
curl -fsSL https://cdn.jsdelivr.net/gh/pc1970/project1@main/scripts/install.sh | bash

# full: also register GitHub + filesystem MCP servers and run diagnostics
curl -fsSL .../install.sh | bash -s -- --full

# run against the current checkout (no clone)
./scripts/install.sh --no-clone
```

Flags: `--full`, `--dir <path>`, `--ref <ref>`, `--no-clone`, `-h/--help`.
Env overrides: `PROJECT1_REPO_URL`, `PROJECT1_DIR`, `PROJECT1_REF`.

If you change the installer, verify with:

```bash
bash -n scripts/install.sh          # syntax
./scripts/install.sh --help         # help block renders
./scripts/install.sh --no-clone     # end-to-end against current tree
```

The `--help` output is extracted from the leading `# install.sh …` comment
block by an `awk` script — keep that block contiguous and `#`-prefixed.

## Invariants to preserve

- **Session hook output contract**: the first stdout line from
  `session-start.sh` must remain the JSON control line. Any logging must come
  after.
- **Remote-only hook**: don't remove the `CLAUDE_CODE_REMOTE` guard in the
  session hook; it prevents local sessions from spending time on pip.
- **Lockfile consistency**: any change to a skill directory under
  `.claude/skills/<name>/` must be reflected in `skills-lock.json`
  (`computedHash`). Changes to one without the other is a drift bug.
- **Marketplace source paths**: entries in
  `superpowers-marketplace/.claude-plugin/marketplace.json` point at real
  paths. When renaming or removing a skill, update the catalog in the same
  commit.
- **GitHub scope**: MCP GitHub tools in this workspace are restricted to
  `pc1970/project1`. Do not attempt cross-repo calls.

## Branching and PRs

- Feature branches follow `claude/<slug>-<suffix>` (e.g.
  `claude/add-install-script-T3OEp`). Develop on the branch the task
  specifies; never push elsewhere without explicit permission.
- Commit messages in history are short, imperative, and describe the skill
  or component being installed/updated (e.g. `Install <skill> skill`,
  `Add scripts/install.sh one-line installer`). Match that style.
- Open PRs as **draft** by default.
