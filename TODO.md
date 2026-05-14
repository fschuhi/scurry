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

- [ ] Define the hardcoded list of "own email addresses" (used to determine if an email is incoming or outgoing).
- [ ] Define the abbreviation dictionary (e.g., `foo.bar@bla.com` -> `FB`).
- [ ] Implement Outgoing logic: build the `(to AB, CD)` suffix (max 3 recipients, drop unknowns).
- [ ] Implement Incoming logic: build the `(AB)` suffix (drop the word 'to').
- [ ] Integrate the calculated suffix into the folder creation step from Milestone 1.

---

## Milestone 3: macOS Integration

**Goal:** Make the macro accessible friction-free without opening the Script Editor.

- [ ] Set up Automator Quick Action wrapping `osascript` execution of the compiled `.scpt`.
- [ ] Assign a global keyboard shortcut via System Settings → Keyboard → Keyboard Shortcuts → Services.
- [ ] Test the trigger inside Apple Mail.
- [ ] Write `docs/macOS_integration.md` detailing exactly how to set up, activate, and deactivate the macro for future reference.

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
