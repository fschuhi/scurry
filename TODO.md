# Scurry TODOs

## Status Key
- `[ ]` To do
- `[~]` Partially done / workaround exists
- `[!]` Known issue, needs investigation
- `[x]` Completed

---

## Backlog

### Karabiner Elements Integration
- [ ] Merge the Karabiner Elements json↔xlsx converter project into Scurry as the 2nd tool in the ecosystem. The project converts between KE JSON config and an Excel spreadsheet for easier rule management. Currently a standalone Python project not in GitHub — a natural fit for Scurry since many macros will be triggered via Karabiner shortcuts.

### Backup Strategy for Gitignored Files
- [ ] Determine a macOS backup strategy for files that are gitignored but contain important data (e.g. `data/MailExporter/contacts.csv`, `own_addresses.txt`). This is a cross-project concern — many projects have similar gitignored-but-critical files. On Windows, SyncBackSE handled this; need a macOS equivalent.

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
