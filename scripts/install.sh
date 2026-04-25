#!/usr/bin/env bash
# install.sh — one-line installer for the Project1 Claude Code workspace.
#
# Usage:
#   curl -fsSL https://cdn.jsdelivr.net/gh/pc1970/project1@main/scripts/install.sh | bash
#   curl -fsSL https://cdn.jsdelivr.net/gh/pc1970/project1@main/scripts/install.sh | bash -s -- --full
#
# Flags:
#   --full          Also install MCP servers and run post-install diagnostics.
#   --dir <path>    Install into <path> (default: $HOME/.project1).
#   --ref <ref>     Git ref/branch/tag to clone (default: main).
#   --no-clone      Skip cloning (run against the current working tree).
#   -h, --help      Show this help.

set -euo pipefail

REPO_URL="${PROJECT1_REPO_URL:-https://github.com/pc1970/project1.git}"
INSTALL_DIR="${PROJECT1_DIR:-$HOME/.project1}"
REF="${PROJECT1_REF:-main}"
FULL=false
NO_CLONE=false

log()  { printf '\033[1;34m[install]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; exit 1; }

usage() {
  awk '/^# install\.sh/{flag=1} flag{if(!/^#/)exit; sub(/^# ?/,""); print}' "$0"
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --full)     FULL=true; shift ;;
    --dir)      INSTALL_DIR="${2:?--dir requires a path}"; shift 2 ;;
    --ref)      REF="${2:?--ref requires a value}"; shift 2 ;;
    --no-clone) NO_CLONE=true; shift ;;
    -h|--help)  usage ;;
    *)          die "unknown option: $1 (try --help)" ;;
  esac
done

require() {
  command -v "$1" >/dev/null 2>&1 || die "missing required tool: $1"
}

require git
require python3

# ── 1. Clone or reuse the workspace ──────────────────────────────────────────
if "$NO_CLONE"; then
  if [[ ! -d .git ]]; then
    die "--no-clone passed but current directory is not a git repo"
  fi
  INSTALL_DIR="$(pwd)"
  log "Using existing workspace at $INSTALL_DIR"
else
  if [[ -d "$INSTALL_DIR/.git" ]]; then
    log "Updating existing checkout at $INSTALL_DIR"
    git -C "$INSTALL_DIR" fetch --quiet origin "$REF"
    git -C "$INSTALL_DIR" checkout --quiet "$REF"
    git -C "$INSTALL_DIR" pull --quiet --ff-only origin "$REF" || \
      warn "pull skipped (non-fast-forward); continuing with current state"
  else
    log "Cloning $REPO_URL@$REF into $INSTALL_DIR"
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone --quiet --branch "$REF" --depth 1 "$REPO_URL" "$INSTALL_DIR"
  fi
fi

cd "$INSTALL_DIR"

# ── 2. Python office-document libraries ──────────────────────────────────────
log "Installing Python office libraries"
PY_LIBS=(
  python-docx openpyxl python-pptx
  pymupdf pypdf pdfplumber
  pandas reportlab striprtf
)
if command -v pip3 >/dev/null 2>&1; then
  pip3 install --quiet --user --upgrade "${PY_LIBS[@]}" || \
    warn "pip3 install failed; you may need to install these manually"
else
  warn "pip3 not found; skipping Python library install"
fi

# ── 3. Make hooks executable ─────────────────────────────────────────────────
if [[ -d .claude/hooks ]]; then
  log "Marking .claude/hooks/* executable"
  find .claude/hooks -type f -name '*.sh' -exec chmod +x {} +
fi

# ── 4. Optional full setup: MCP servers + diagnostics ────────────────────────
if "$FULL"; then
  log "Full setup: configuring MCP servers"
  if command -v claude >/dev/null 2>&1; then
    # GitHub MCP (read-only by default; user can scope later)
    claude mcp add --scope user github -- npx -y @modelcontextprotocol/server-github \
      || warn "failed to register github MCP"
    # Filesystem MCP scoped to the install dir
    claude mcp add --scope user filesystem -- npx -y @modelcontextprotocol/server-filesystem "$INSTALL_DIR" \
      || warn "failed to register filesystem MCP"
  else
    warn "'claude' CLI not found on PATH; skipping MCP registration"
  fi

  log "Running diagnostics"
  printf '  • git:     %s\n' "$(git --version 2>/dev/null || echo missing)"
  printf '  • python3: %s\n' "$(python3 --version 2>/dev/null || echo missing)"
  printf '  • node:    %s\n' "$(node --version 2>/dev/null || echo missing)"
  printf '  • npx:     %s\n' "$(npx --version 2>/dev/null || echo missing)"
  printf '  • claude:  %s\n' "$(claude --version 2>/dev/null || echo missing)"

  # Quick import smoke-test for the office libs we just installed
  python3 - <<'PY' || warn "office library smoke-test failed"
import importlib, sys
mods = ["docx", "openpyxl", "pptx", "fitz", "pypdf", "pdfplumber", "pandas", "reportlab", "striprtf.striprtf"]
missing = [m for m in mods if importlib.util.find_spec(m) is None]
if missing:
    print(f"  • missing modules: {missing}", file=sys.stderr)
    sys.exit(1)
print("  • all office libraries importable")
PY
fi

log "Done. Workspace: $INSTALL_DIR"
log "Next: cd $INSTALL_DIR && claude"
