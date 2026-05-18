# Scurry TODOs

## Status Key
- `[ ]` To do
- `[~]` Partially done / workaround exists
- `[!]` Known issue, needs investigation
- `[x]` Completed

---

## Backlog

### Karabiner Elements Integration
- [x] Merge the Karabiner Elements json↔xlsx converter project into Scurry as the 2nd tool in the ecosystem. Converter lives in `scripts/KarabinerConverter/`, with Makefile targets for export, import, and deploy. 29 tests. (Completed 2026-05-18)

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
