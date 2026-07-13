# History

(Note: "I" in the following paragraphs refer to the user, "you" to you as the AI model.)

- The resolved-work record: what was built and when (note date, or have the points in roughly reverse-chronological order).
- This is the trophy case -- kept in the repo, **out of the per-session filesdump** (so it no longer rides along every session).
- For *forward* work see `TODO.md`; for direction see `GOALS.md`; for the architecture as it stands see `README.md`.
- See "Workflow for the Whole Session (CRITICAL)" in `LLM_INSTRUCTIONS.md` for the interplay between `TODO.md` and this file. 

---

## [0.4.0] — 2026-05-18

### KarabinerConverter: Integration into Scurry — COMPLETE

Bidirectional converter between Karabiner Elements JSON and Excel, merged into Scurry as the second tool in the ecosystem.

**Implemented:**
- Integrated `karabiner_converter.py` into `scripts/KarabinerConverter/` — converts between Karabiner Elements JSON config and xlsx spreadsheet
- Supports all Karabiner rule types: key remaps, pointing_button, shell_command, per-app conditions (`frontmost_application_if`/`unless`), multiple from-modifiers, multiple to-values (key sequences), and multiple bundle identifiers
- Three Makefile targets: `karabiner-export` (xlsx → JSON), `karabiner-import` (JSON → xlsx from `complex_modifications`), `karabiner-deploy` (export + timestamped backup + copy to Karabiner + reminder)
- `bak/` directory for timestamped backups of deployed rules (gitignored)
- Example spreadsheet (`data/KarabinerConverter/rules.example.xlsx`) with 94 representative rules tracked in git
- Production `rules.xlsx` gitignored via `data/**/rules.xlsx` pattern

**Test suite:**
- 29 new pytest tests in `tests/KarabinerConverter/test_karabiner_converter.py`
- Purpose-built 10-row fixture (`tests/fixtures/KarabinerConverter/rules.xlsx`) exercising every code path: simple remap, conditions, modifiers, pointing_button, shell_command, multi-value output, multi-bundle conditions, edge cases
- Golden file (`tests/fixtures/KarabinerConverter/rules.json`) for regression testing
- Test groups: `_normalize_list_cell` helper (7), xlsx→JSON per-row verification (12), JSON→xlsx verification (5), roundtrip integrity (2), edge cases (3)
- Full roundtrip verified: xlsx → JSON → xlsx → JSON produces identical output

**Project updates:**
- README.md expanded with KarabinerConverter architecture, data flow diagram, schema docs, and usage
- Makefile reorganized with `KE_*` variables for KarabinerConverter paths
- `openpyxl` added to `requirements.txt`

---

## [0.3.0] — 2026-05-18

### Milestone 2: Routing & Naming Polish — COMPLETE

Directionality suffixes for exported email folders, powered by a Python helper script.

**Implemented:**
- Created `suffix_helper.py` — determines email direction (incoming vs outgoing) and generates folder name suffixes like `(to JD, FB)` or `(BH)`
- Abbreviation dictionary via semicolon-delimited CSV (`data/MailExporter/contacts.csv`) with comment and blank line support
- Own-address list via plain text file (`data/MailExporter/own_addresses.txt`) for directionality detection
- Case-insensitive matching on all email address lookups
- Outgoing: up to 3 To recipient abbreviations, unknowns silently dropped, duplicates removed, order preserved
- Incoming: single sender abbreviation, or no suffix if unknown
- Integrated into `export_mail.applescript` (v8) via `do shell script` call
- Refactored `stagingRoot` to derive from new `projectRoot` variable (single source of truth)
- Example config files tracked in git (`contacts.example.csv`, `own_addresses.example.txt`)

**Test suite:**
- 13 new pytest tests in `tests/MailExporter/test_suffix_helper.py`
- Covers: incoming/outgoing logic, case insensitivity, cap at 3, deduplication, order preservation, unknown handling, file loading, CLI integration
- Test fixtures in `tests/fixtures/MailExporter/`
- Mirrored test directory structure (`tests/MailExporter/`) to match `macros/MailExporter/`, preparing for multi-tool growth

**Design decisions:**
- Python helper over AppleScript-native: avoids AppleScript's lack of dictionaries, awkward string handling, and Mac Roman encoding constraints
- CSV over JSON/TOML for config: extensible (future columns for namespaces, on/off toggles), comfortable for Excel round-tripping (semicolon-delimited for German locale)
- Separate own-addresses file: directionality detection and abbreviation lookup are independent concerns
- CLI argument interface (no central config TOML): keeps things simple; AppleScript passes paths directly
- Only To recipients considered (not Cc/Bcc)

---

## [0.2.0] — 2026-05-16

### Milestone 3: macOS Integration — COMPLETE

Keyboard shortcut integration via Karabiner Elements, plus a tooling bugfix discovered during the session.

**Implemented:**
- Bound CapsLock+D to run the compiled `export_mail.scpt` via Karabiner Elements `shell_command`
- Scoped the shortcut to Apple Mail only (`^com\.apple\.mail$` via `condition_bundle_ids`)
- Granted Accessibility permission on first run; subsequent invocations require no user interaction

**Integration decision:**
- Chose Karabiner Elements over Automator Quick Action, Shortcuts, or Keyboard Maestro. The Karabiner approach leverages an existing, proven setup (CapsLock-as-Hyper key layer) already in use for clip-tools and 90+ other key mappings. Per-app scoping via `condition_bundle_ids` avoids accidental triggers. No additional software required.

**Tooling bugfix: `tools/concat_files.py`**
- Fixed silent omission of `export_mail.applescript` from the filesdump, caused by two independent bugs:
  1. **Encoding mismatch:** Script Editor saves `.applescript` files in Mac Roman encoding (ISO-8859). The script's `read_text(encoding='utf-8')` raised `UnicodeDecodeError` on characters like em dashes and `«class isot»` chevrons. Fix: new `read_text_with_fallback()` function tries UTF-8 first, then falls back to `mac_roman`.
  2. **Curly brace collision:** AppleScript's empty list literal `{}` was interpreted as a Python `str.format()` positional placeholder, causing `IndexError`. Fix: replaced `FILE_TEMPLATE.format(...)` with direct string concatenation using f-strings for the XML tags only.
- The error handler now writes diagnostics to stderr (previously swallowed silently)

---

## [0.1.0] — 2026-05-15

### Milestone 1: Core Extraction Engine — COMPLETE

First working version of the Mail Exporter. Extracts a selected email from Apple Mail and saves it to a local staging folder.

**Implemented:**
- Read the currently selected message in Apple Mail via AppleScript
- Extract metadata: sender (normalized to bare email), To, Cc, Bcc recipients, subject, datetime
- Extract plain text body (HTML/rich formatting stripped by Mail)
- Sanitize subject line for safe use in folder names (strip `: / \ * ? " < > |`, collapse whitespace)
- Format datetime as `YYMMDD vHHMM` for folder naming and `YYYY-MM-DD HH:MM` for email.txt header
- Create named folder in hardcoded staging directory (`~/Projects/scurry/tmp/`)
- Save `email.txt` with metadata headers, blank line separator, and body text
- Download and save all attachments (including inline/pasted images) into the folder
- Compile plain-text `.applescript` to `.scpt` via `make build` (`osacompile`)
- Verified `osascript` execution of compiled script from Terminal

**Technical decisions:**
- Date formatting via `do shell script` + Unix `date` command (avoids locale-dependent AppleScript date handling)
- ISO 8601 intermediate format via `«class isot»` for reliable date conversion
- Subject sanitization via `sed` pipeline in shell
- Heredoc pattern (`<<'SCURRY_EOF'`) for writing email.txt to prevent shell interpolation issues
- `quoted form of` used consistently for shell argument escaping

**Known quirks:**
- `display dialog` OK button does not respond to mouse clicks in Script Editor; use Enter/Return to dismiss
- Multi-message selection order from `selected messages of message viewer 1` is not guaranteed by Apple Mail

**Integration decision (for Milestone 3):**
- Automator Quick Action selected as the mechanism for keyboard shortcut binding
