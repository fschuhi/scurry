# Scurry TODOs

## Status Key
- `[ ]` To do
- `[~]` Partially done / workaround exists
- `[!]` Known issue, needs investigation
- `[x]` Completed

---

## Milestone 1: The Core Extraction Engine (Apple Mail)

**Goal:** Extract an email and save it to the staging area with a basic name. Defer complex abbreviation and routing logic.

**Status: COMPLETE (2026-05-15)**

- [x] Setup `macros/MailExporter/export_mail.applescript`.
- [x] Read the currently selected message(s) in Apple Mail.
- [x] Extract metadata: sender, recipients (To/Cc/Bcc), subject, and datetime.
- [x] Extract the plain text body (stripped of HTML and rich formatting).
- [x] Sanitize the subject (strip reserved path characters like `:`, `/`, etc.).
- [x] Format the datetime as `YYMMDD vHHMM`.
- [x] Create a local save directory in the hardcoded staging path (`YYMMDD vHHMM Sanitized_Subject`).
- [x] Format and save `email.txt` (must include metadata headers, the plain text body, and a list of attached filenames at the bottom).
- [x] Download and save the actual attachments into the newly created folder.

---

## Milestone 2: Routing & Naming Polish

**Goal:** Implement the directionality logic and the abbreviation dictionary for the folder suffix.

**Implementation approach:** A Python helper script called from AppleScript via `do shell script`. This keeps the AppleScript lean and avoids its awkward string handling and encoding limitations (Mac Roman, no proper dictionaries, no dynamic key lookup). The helper receives sender and recipient addresses as arguments and returns the formatted suffix. The abbreviation mapping and own-address list live in a configuration file (format TBD: JSON or simple text) managed outside the AppleScript.

- [ ] Create the Python helper script for abbreviation lookup and suffix generation.
- [ ] Define the configuration file format and location for the abbreviation dictionary and own-address list.
- [ ] Implement Outgoing logic: build the `(to AB, CD)` suffix (max 3 recipients, drop unknowns).
- [ ] Implement Incoming logic: build the `(AB)` suffix (drop the word 'to').
- [ ] Integrate the `do shell script` call into `export_mail.applescript` to invoke the helper.
- [ ] Integrate the returned suffix into the folder creation step from Milestone 1.

---

## Milestone 3: macOS Integration

**Goal:** Make the macro accessible friction-free without opening the Script Editor.

**Status: COMPLETE (2026-05-16)**

- [x] Bound CapsLock+D via Karabiner Elements `shell_command` to run `osascript .../export_mail.scpt`.
- [x] Scoped the shortcut to Apple Mail only via `condition_bundle_ids` (`^com\.apple\.mail$`).
- [x] Granted Accessibility permission on first run; works silently thereafter.
- [x] Karabiner was chosen over Automator Quick Action, Shortcuts, and Keyboard Maestro — it leverages an existing setup already managing 90+ key mappings.

**Note:** The Karabiner rule lives in the Karabiner rules spreadsheet (`rules.xlsx`), not in the scurry repo. Run `make build` after any AppleScript changes to ensure the compiled `.scpt` is current before using the shortcut.

---

## Milestone 4: Nice to Have (Backlog)

### Inline Pictures
- [ ] Consider renaming inline/pasted images (currently saved as `image001.png` etc.) to a sequential scheme like `pic1.png`, `pic2.png` for clarity. (Note: inline images are already saved by the attachment loop — this is cosmetic.)

### Testing
- [ ] Designate a stable IMAP folder with known emails as a "test fixture" for repeatable testing.
- [ ] Explore scripting automated test runs (e.g., AppleScript that selects a specific email in the fixture folder, runs the export, and verifies output).

### Staging Management
- [ ] Add an AppleScript/macro to assist in bulk clearing or archiving the staging folders once Total Commander routing is done.

### Expanded Workbench
- [ ] Safari: Extract current URL and page title to markdown link format.
- [ ] Generic Text: Clipboard sanitization macros (e.g., strip all formatting from current clipboard).
