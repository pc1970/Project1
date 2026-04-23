---
name: write
description: Invoke only when explicitly asked to write, edit, or polish prose in Chinese or English. Strips AI writing patterns and rewrites to sound natural. Not for code comments, commit messages, or inline docs.
metadata:
  version: "3.10.1"
---

# Write: Cut the AI Taste

Prefix your first line with 🥷 inline, not as its own paragraph.


Strip AI patterns from prose and rewrite it to sound human. Do not improve vocabulary; remove the performance of improvement.

## Pre-flight

1. **Text present?** If the user gave only an instruction with no actual prose to edit, ask for the text in one sentence. Do not proceed.
2. **Audience locked?** If the intended audience is unclear and cannot be inferred from the text (blog reader vs RFC vs email), ask before editing. Junior engineer and senior architect prose should read completely different.
3. **Language detected from the text being edited**, not the user's command:
   - Contains Chinese characters → load `references/write-zh.md`
   - Otherwise → load `references/write-en.md`

Read the loaded reference file. Then edit. No summary, no commentary, no explanation of changes unless explicitly asked.

## Hard Rules

- **Meaning first, style second.** If removing an AI pattern would change the author's intended meaning, keep the original. A failed rewrite sounds better but says something different.
- **Preserve unless told to cut.** Keep every sentence and paragraph unless the user explicitly asks to remove or replace specific parts. Flag unnecessary sections; do not delete them silently.
- **No silent restructuring.** Do not reorganize headings, reorder paragraphs, or merge sections unless structural changes are explicitly requested. Edit in place.
- **Match naming conventions.** Before creating new content files, check existing patterns in the target directory and follow them.
- **Never guess the target text.** If the request refers to "the paragraph above" or "what you just said" without quoting it, ask which exact text to edit. Do not rewrite conversation history without explicit permission.
- **Stop after output.** Deliver the rewritten text. Then stop. Do not append a list of changes, a justification, or a "hope this helps" closer.
- **No emoji in edited text.** Remove any emoji from the output unless the user explicitly asks to keep them.

## Output

Return only the edited prose. If the text was truncated or if multiple versions were possible, note that in one sentence after the body. Otherwise, no wrapper, no preamble, no postscript.
