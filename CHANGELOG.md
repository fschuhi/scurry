# Changelog

All notable changes to the Scurry project will be documented in this file.

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
