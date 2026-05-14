# Scurry TODOs

## Status Key
- `[ ]` To do
- `[~]` Partially done / workaround exists
- `[!]` Known issue, needs investigation
- `[x]` Completed

---

## Milestone 1: The Core Extraction Engine (Apple Mail)

**Goal:** Extract an email and save it to the staging area with a basic name. Defer complex abbreviation and routing logic.

- [ ] Setup `macros/MailExporter/export_mail.applescript`.
- [ ] Read the currently selected message(s) in Apple Mail.
- [ ] Extract metadata: sender, recipients (To/Cc), subject, and datetime.
- [ ] Extract the plain text body (stripped of HTML and rich formatting).
- [ ] Sanitize the subject (strip reserved path characters like `:`, `/`, etc.).
- [ ] Format the datetime as `YYMMDD vHHMM`.
- [ ] Create a local save directory in the hardcoded staging path (`YYMMDD vHHMM Sanitized_Subject`).
- [ ] Format and save `email.txt` (must include metadata headers, the plain text body, and a list of attached filenames at the bottom).
- [ ] Download and save the actual attachments into the newly created folder.

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

- [ ] Select the best method to bind the AppleScript to a global keyboard shortcut (e.g., macOS Shortcuts app, Automator Quick Action, or FastScripts).
- [ ] Test the trigger inside Apple Mail.
- [ ] Write `docs/macOS_integration.md` detailing exactly how to set up, activate, and deactivate the macro for future reference.

---

## Milestone 4: Nice to Have (Backlog)

### Staging Management
- [ ] Add an AppleScript/macro to assist in bulk clearing or archiving the staging folders once Total Commander routing is done.

### Expanded Workbench
- [ ] Safari: Extract current URL and page title to markdown link format.
- [ ] Generic Text: Clipboard sanitization macros (e.g., strip all formatting from current clipboard).
