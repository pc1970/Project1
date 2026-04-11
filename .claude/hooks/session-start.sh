#!/bin/bash
# Session-start hook: install office document processing libraries
# Runs at the start of every Claude Code session (remote/web only).
set -euo pipefail

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo '{"async": true, "asyncTimeout": 300000}'

# ── Python office document libraries ─────────────────────────────────────────
REQUIRED_LIBS=(
  "python-docx"   # .docx  — Word documents
  "openpyxl"      # .xlsx  — Excel spreadsheets
  "python-pptx"   # .pptx  — PowerPoint presentations
  "pymupdf"       # .pdf   — PDF read/annotate/form-fill
  "pypdf"         # .pdf   — PDF merge/split/metadata
  "pdfplumber"    # .pdf   — PDF table extraction
  "pandas"        # .csv/.xlsx — data analysis and conversion
  "reportlab"     # .pdf   — PDF generation
  "striprtf"      # .rtf   — RTF text extraction
  "openpyxl"      # already listed, idempotent
)

# Deduplicate
UNIQUE_LIBS=($(printf '%s\n' "${REQUIRED_LIBS[@]}" | sort -u))

echo "[session-start] Checking office document libraries..."

MISSING=()
for lib in "${UNIQUE_LIBS[@]}"; do
  import_name="${lib//-/_}"      # python-docx → python_docx
  import_name="${import_name//python_docx/docx}"
  import_name="${import_name//python_pptx/pptx}"
  import_name="${import_name//pymupdf/fitz}"
  import_name="${import_name//striprtf/striprtf.striprtf}"
  import_name="${import_name//pdfplumber/pdfplumber}"

  if ! python3 -c "import ${import_name%.*}" 2>/dev/null; then
    MISSING+=("$lib")
  fi
done

if [ ${#MISSING[@]} -eq 0 ]; then
  echo "[session-start] All office libraries already installed."
  exit 0
fi

echo "[session-start] Installing missing libraries: ${MISSING[*]}"
pip3 install --quiet "${MISSING[@]}"
echo "[session-start] Office libraries ready."
