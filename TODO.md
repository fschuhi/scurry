# scurry -- TODO

(Note: "I" in the following paragraphs refer to the user, "you" to you as the AI model.)

## Charter 

- Forward-looking only -- concrete, startable work: tasks specified well enough that next-session-me can begin within ten minutes, plus investigation items, test specs, and scratchpad ideas awaiting promotion or deletion.
- Items are unordered within their theme sections; open questions are marked _Needs investigation_ in the bullet.
- When an item is completed, record its durable outcome in `HISTORY.md` during the same session while the evidence and rationale are fresh, then strike it through in `TODO.md` with a concise handover note.
- Retain struck-through items through the next session because `TODO.md` is included in the standard filesdump while `HISTORY.md` normally is not; at the end of that next session, remove the already-archived items from `TODO.md`. Strategic direction, ordering, and milestones live in `GOALS.md` -- anything that needs a strategy discussion before it is actionable goes there.
- Architecture, contract, and settled decisions live in `README.md`.

---
## Backlog

### Karabiner Elements Integration
- ~~Merge the Karabiner Elements json↔xlsx converter project into Scurry as the 2nd tool in the ecosystem. Converter lives in `scripts/KarabinerConverter/`, with Makefile targets for export, import, and deploy. 29 tests. (Completed 2026-05-18)~~

### KarabinerConverter Enhancements
- [ ] Add `--description` flag to `xlsx2json` for setting the rule group description in the JSON output (currently hardcoded as "Karabiner Rules"). This is separate from `--title` which sets the top-level title.
- [ ] Add a "comment" column to the xlsx schema — a free-text column for documenting *why* a rule exists. Ignored during JSON export, preserved during roundtrip. Useful for remembering the purpose of rules like the two Ctrl-Tab variants for Parallels.

### Backup Strategy for Gitignored Files
- [ ] Determine a macOS backup strategy for files that are gitignored but contain important data (e.g. `data/MailExporter/contacts.csv`, `own_addresses.txt`, `data/KarabinerConverter/rules.xlsx`). This is a cross-project concern — many projects have similar gitignored-but-critical files. On Windows, SyncBackSE handled this; need a macOS equivalent.

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
