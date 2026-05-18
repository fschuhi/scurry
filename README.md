# Scurry

**A minimal macOS automation workbench for script-driven workflows.**

*Scurry* (noun) — "light, running steps": small, fast scripts that run in the background to handle the tedious parts of a workflow.

---

## Vision

Scurry exists to replicate and enhance a legacy Windows/Outlook/VBA macro workflow within the macOS ecosystem. It serves as a workbench for lightweight, highly specific automations — AppleScript macros, Python converters, and the glue that connects them — starting with a robust Apple Mail extraction tool and a Karabiner Elements rule manager.

**Core Philosophy:**

* **Hardcoded Reliability**: Configuration lives in code. Scripts should execute instantly without clunky dynamic UI prompts or "Choose Folder" dialogs.
* **Staging over Sorting**: Scurry extracts data to a predictable, hardcoded "staging" directory (mimicking a dedicated `D:` drive). It does not attempt to guess the final project folder. Final routing is performed manually using Total Commander (via Windows Parallels) for maximum speed and control.
* **Non-Destructive**: Scripts are read-only regarding the source application. The Mail extractor will never delete, move, or alter emails within Apple Mail or IMAP. Organization remains a manual, intentional user action.
* **Plain Text First**: Extracted data is stripped of formatting, HTML, and proprietary cruft, ensuring long-term readability and portability.

---

## Architecture

Scurry combines two categories of tools:

**Macros** (`macros/`) rely on AppleScript (and occasionally JavaScript for Automation / JXA) to interact directly with macOS application GUIs. This bypasses the need for complex, brittle API authentication (like IMAP App Passwords) by leveraging the applications that are already authenticated on the system. Python helper scripts handle logic that would be awkward in AppleScript — dictionary lookups, CSV parsing, string manipulation — and are called from AppleScript via `do shell script`.

**Scripts** (`scripts/`) are standalone Python tools that solve specific workflow problems. They don't interact with macOS GUIs but operate on data files (spreadsheets, JSON configs) that feed into the broader automation ecosystem.

### Data Flow: Mail Exporter

```mermaid
graph TB
    subgraph "macOS Environment"
        AM[Apple Mail]
        AS[Scurry AppleScript]
        PY[Python Helper<br/>suffix_helper.py]
        CFG[Config Files<br/>contacts.csv<br/>own_addresses.txt]
        ST[Local Staging Folder]
    end

    subgraph "Parallels (Windows)"
        TC[Total Commander]
        PR[Final Project Folders]
    end

    AM -->|User selects email| AS
    AS -->|sender, To recipients| PY
    CFG -->|abbreviations, own addresses| PY
    PY -->|suffix string| AS
    AS -->|Extracts text & attachments| ST
    ST -->|Manual F6 Move| TC
    TC -->|Routed| PR
```

### Data Flow: Karabiner Converter

```mermaid
graph LR
    subgraph "Scurry"
        XLSX[rules.xlsx<br/>in data/KarabinerConverter/]
        CONV[karabiner_converter.py]
        JSON[rules.json<br/>in build/KarabinerConverter/]
    end

    subgraph "macOS"
        KE_DIR[~/.config/karabiner/assets/<br/>complex_modifications/]
        KE[Karabiner Elements]
    end

    XLSX -->|make karabiner-export| CONV
    CONV --> JSON
    JSON -->|make karabiner-deploy| KE_DIR
    KE_DIR -->|load rules| KE
    KE_DIR -->|make karabiner-import| CONV
    CONV -->|bootstrap xlsx| XLSX
```

---

## The Mail Exporter

The primary macro extracts selected emails from Apple Mail into a structured local directory within the staging folder.

**Status:** Milestones 1–3 complete. Core extraction is fully functional and accessible via keyboard shortcut (CapsLock+D). Directionality suffixes are fully functional.

For detailed documentation on folder naming conventions, email text format, attachments, configuration, and technical notes, see the [MailExporter section](#mail-exporter-details) below.

---

## The Karabiner Converter

A bidirectional converter between Karabiner Elements JSON configuration and an Excel spreadsheet for easier rule management.

**Status:** Integrated into Scurry. Export, import, and deploy workflows functional via Makefile targets.

### Why It Exists

Karabiner Elements stores keyboard rules in deeply nested JSON — powerful but tedious to edit by hand. The converter lets you manage 100+ rules in a spreadsheet (with columns for description, from-key, modifiers, conditions, etc.) and generate valid Karabiner JSON from it. This is especially valuable for the CapsLock-as-Hyper-key setup that drives Scurry's keyboard shortcuts and 90+ other key mappings.

### Spreadsheet Schema

| Column | Description |
|--------|-------------|
| `description` | Human-readable rule name |
| `from_key` | The trigger key code (e.g., `caps_lock`, `c`, `f1`) |
| `from_modifiers` | Comma-separated mandatory modifiers (e.g., `right_control,left_command`) |
| `to_type` | Output type: `key`, `pointing_button`, or `shell_command` |
| `to_value` | Output value(s) — comma-separated for multi-key sequences; full command string for `shell_command` |
| `to_modifiers` | Comma-separated modifiers applied to each output (ignored for `shell_command`) |
| `condition_type` | `frontmost_application_if` or `frontmost_application_unless` |
| `condition_bundle_ids` | Comma-separated bundle ID regex patterns (e.g., `^com\.parallels\.desktop\.console$`) |

### Makefile Targets

```bash
make karabiner-export   # Convert rules.xlsx → rules.json (in build/)
make karabiner-import   # Import rules.json from complex_modifications → rules.xlsx
make karabiner-deploy   # Export + backup existing + copy to Karabiner + reminder
```

**Deploy workflow:** `make karabiner-deploy` generates the JSON, backs up any existing `rules.json` in Karabiner's `complex_modifications` folder (timestamped copy in `bak/`), copies the new file, and prints a reminder to remove and re-enable the ruleset in Karabiner Elements.

---

## Project Structure

```text
scurry/
├── macros/                              ← GUI automation scripts
│   └── MailExporter/
│       ├── export_mail.applescript       ← Core email extraction logic (plain text)
│       └── suffix_helper.py             ← Python helper for directionality suffixes
├── scripts/                             ← Standalone Python tools
│   └── KarabinerConverter/
│       └── karabiner_converter.py       ← JSON ↔ xlsx bidirectional converter
├── data/                                ← Runtime configuration (gitignored production files)
│   ├── KarabinerConverter/
│   │   ├── rules.xlsx                   ← Karabiner rules spreadsheet (gitignored)
│   │   └── rules.example.xlsx           ← Example with 94 representative rules (tracked)
│   └── MailExporter/
│       ├── contacts.csv                 ← Abbreviation dictionary (gitignored)
│       ├── contacts.example.csv         ← Example with dummy data (tracked)
│       ├── own_addresses.txt            ← Own email addresses (gitignored)
│       └── own_addresses.example.txt    ← Example (tracked)
├── build/                               ← Generated output (gitignored)
│   ├── KarabinerConverter/
│   │   └── rules.json                   ← Generated Karabiner JSON
│   └── MailExporter/
│       └── export_mail.scpt             ← Compiled AppleScript
├── tests/                               ← Test suite (mirrored structure)
│   ├── KarabinerConverter/
│   │   └── test_karabiner_converter.py  ← 29 tests for converter logic and roundtrip
│   ├── MailExporter/
│   │   └── test_suffix_helper.py        ← 13 tests for suffix logic, file loading, CLI
│   └── fixtures/
│       ├── KarabinerConverter/
│       │   ├── rules.xlsx               ← 10-row purpose-built test fixture
│       │   └── rules.json               ← Golden file (expected converter output)
│       └── MailExporter/
│           ├── contacts.csv             ← Test fixture with known mappings
│           └── own_addresses.txt        ← Test fixture with known addresses
├── tools/
│   └── concat_files.py                  ← Filesdump generator for LLM sessions
├── bak/                                 ← Timestamped backups from deploy targets (gitignored)
├── tmp/                                 ← Staging folder for exported emails (gitignored)
├── CHANGELOG.md                         ← Release history
├── CRITICAL_RULES.md                    ← Non-negotiable LLM collaboration rules
├── LLM-instructions.md                  ← AI session context and conventions
├── README.md                            ← You are here
├── TODO.md                              ← Backlog and future directions
├── first-prompt.md                      ← Entry point for new LLM sessions
├── manifest.lst                         ← File list for filesdump generation
├── Makefile                             ← Build and utility targets
└── requirements.txt                     ← Python dependencies (openpyxl, black, pytest)
```

---

## Testing

Scurry uses pytest for automated testing. The test directory mirrors the project structure to keep tests close to the code they verify.

### Running Tests

```bash
make test           # Quiet mode
make test-verbose   # Verbose with stdout
```

### Test Coverage

**`tests/KarabinerConverter/test_karabiner_converter.py`** (29 tests):
* **`_normalize_list_cell` helper:** None, empty string, single value, comma-separated, whitespace handling, list input, empty-string filtering
* **xlsx → JSON conversion:** all 10 fixture rows verified individually — simple remap, conditions (if/unless), from/to modifiers, multiple from-modifiers, pointing_button, shell_command, multi-value output, multi-bundle-identifier conditions
* **JSON → xlsx conversion:** row count, headers, shell_command preservation, multi-value collapse, pointing_button roundtrip
* **Roundtrip integrity:** xlsx → JSON → xlsx → JSON produces identical output; freshly converted output matches golden file
* **Edge cases:** empty rows skipped, missing `from_key` warning, missing columns cause `sys.exit(1)`

**`tests/MailExporter/test_suffix_helper.py`** (13 tests):
* **Incoming email logic:** known sender, unknown sender, case insensitivity
* **Outgoing email logic:** 1/2/3/4+ recipients, mixed known/unknown, all unknown, no recipients, deduplication, order preservation, case insensitivity
* **File loading:** comment and blank line handling, case normalisation, CSV parsing
* **CLI integration:** end-to-end smoke tests calling the script as a subprocess

### Test Fixtures

Test fixtures live in `tests/fixtures/<Component>/` and contain deterministic data (tracked in git). They serve as stable test inputs that won't change when the user updates their real configuration.

The KarabinerConverter fixture is a purpose-built 10-row spreadsheet covering every code path in the converter, paired with a golden JSON file representing the expected output. See the test file's docstring for a row-by-row map of what each row exercises.

---

## Integration & Usage

### Daily Use: Keyboard Shortcut (CapsLock+D)

The primary way to use the Mail Exporter is via a Karabiner Elements keyboard shortcut:

1. Select an email in Apple Mail
2. Press **CapsLock+D** (D for "download")
3. The export runs silently and shows a confirmation dialog with the folder name and attachment count

**Prerequisites:**
- The compiled `.scpt` must be current: run `make build` after any changes to the AppleScript source
- Accessibility permission must have been granted on first run
- `data/MailExporter/contacts.csv` and `own_addresses.txt` must exist (copy from the example files and populate with real data)

**How it works:** A Karabiner Elements `shell_command` rule calls `osascript` on the compiled `.scpt`. The rule is scoped to Apple Mail only via `condition_bundle_ids` (`^com\.apple\.mail$`), so it won't fire in other apps. The rule lives in the Karabiner rules spreadsheet (`data/KarabinerConverter/rules.xlsx`), managed by the converter and deployed via `make karabiner-deploy`.

### Karabiner Rules Management

```bash
# Edit rules in Excel, then deploy:
make karabiner-deploy

# Bootstrap xlsx from an existing Karabiner config:
make karabiner-import
```

### Running from Script Editor (Development)

Open `macros/MailExporter/export_mail.applescript` in Script Editor, select an email in Apple Mail, and press ▶️ Run. Use Enter/Return to dismiss the confirmation dialog (the OK button may not respond to mouse clicks — this is a known Script Editor quirk).

### Running from Terminal

Compile and run the script directly:

```bash
make build
osascript build/MailExporter/export_mail.scpt
```

Or run the plain-text source directly (useful for debugging — errors print to stderr):

```bash
osascript macros/MailExporter/export_mail.applescript
```

---

## Mail Exporter Details

### Folder Naming Convention

The script analyzes the selected email and formats the folder name as: `YYMMDD vHHMM Sanitized_Subject [Suffix]`.

* **Timestamp:** Formatted as `YYMMDD vHHMM` (e.g., `2026-05-09 15:33` becomes `260509 v1533`). Date formatting is performed via `do shell script` using the Unix `date` command to avoid locale-dependent AppleScript date handling. The intermediate conversion uses ISO 8601 format via `«class isot»`.
* **Reserved Characters:** Characters invalid in macOS/Windows paths (`: / \ * ? " < > |`) are stripped from the subject. Multiple spaces are collapsed and leading/trailing whitespace is trimmed. Sanitization is performed via a `sed` pipeline in the shell.
* **Directionality Suffix:** A Python helper script (`suffix_helper.py`) is called from AppleScript via `do shell script`. It determines whether the email is incoming or outgoing by checking the sender against a list of own addresses, then looks up abbreviations from a contacts CSV.
    * **Outgoing (Sent):** Appends `(to AB, CD)` based on the abbreviation dictionary. Maximum of 3 To recipients. Unknown recipients are silently dropped. Duplicates are removed. Order is preserved.
    * **Incoming (Inbox):** Appends `(AB)`. The word "to" is omitted. If the sender is unknown, no suffix is added.

**Examples:**
* Outgoing: `260509 v1533 RE This subject it is (to FB)`
* Outgoing, multiple: `260509 v1015 Project Alpha Update (to FB, JD)`
* Incoming: `260509 v1015 Project Alpha Update (FB)`
* Unknown sender/recipients: `260509 v1015 Project Alpha Update`

### Email Text Format (`email.txt`)

The body of the email is saved strictly as plain text. The script prepends metadata headers and appends a list of any downloaded attachments.

**Example Output:**
```text
From: frank.schuhardt@gmail.com
To: foo.bar@bla.com
Cc: rup.rap@bla.com
Bcc:
Subject: RE: This subject it is
Datetime: 2026-05-09 15:33

Hi Foo! Let's go! (please see attachment)

(attached: blubb.xlsx)
(attached: budget_v2.pdf)
```

The file is written using a shell heredoc pattern (`<<'SCURRY_EOF'`) to prevent shell interpolation of email content.

### Attachments

Attachments are downloaded automatically and saved directly into the generated folder alongside the `email.txt` file. This includes inline/pasted images, which Apple Mail exposes as `mail attachments` with auto-generated names (e.g., `image001.png`).

### Configuration

**Project root** is defined at the top of the AppleScript, and the staging directory derives from it:

```applescript
set projectRoot to (POSIX path of (path to home folder)) & "Projects/scurry/"
set stagingRoot to projectRoot & "tmp/"
```

**Abbreviation dictionary** (`data/MailExporter/contacts.csv`): A semicolon-delimited CSV mapping email addresses to short abbreviations. Supports comment lines (starting with `#`) and blank lines. Header row: `address;abbreviation`. Example files are tracked in git as `contacts.example.csv`.

**Own-address list** (`data/MailExporter/own_addresses.txt`): One email address per line. Used to determine directionality — if the sender is in this list, the email is outgoing. Supports comment lines and blank lines. Example file tracked as `own_addresses.example.txt`.

Both config files are gitignored (they contain real email addresses). The example files document the expected format.

All email address matching is case-insensitive.

---

## Technical Notes & Gotchas

* **HFS vs. POSIX Paths:** AppleScript natively uses colon-separated HFS paths (`Macintosh HD:Users:name:Desktop:`). Interacting with the Unix shell or standard file systems requires explicit coercion to POSIX paths (`/Users/name/Desktop/`). The `save` command for attachments requires `POSIX file` coercion. Scurry scripts clearly document path coercions to prevent runtime errors.
* **AppleScript Date Parsing:** AppleScript's native date handling is localized and fragile. Scurry converts dates to ISO 8601 via `«class isot»` (a four-character OSType code) and then reformats via `do shell script "date ..."` to ensure consistent output regardless of macOS system region settings.
* **AppleScript File Encoding:** Script Editor saves `.applescript` files in Mac Roman encoding (not UTF-8). Characters like em dashes and the `« »` chevrons in four-character codes are not valid UTF-8. The filesdump generator (`tools/concat_files.py`) handles this with a UTF-8 → Mac Roman fallback. Keep this in mind when processing AppleScript files with other tools.
* **Shell Argument Safety:** All user-controlled data (email subjects, body text) is passed to `do shell script` using `quoted form of` to prevent shell injection. The email.txt heredoc uses single-quoted delimiters (`<<'SCURRY_EOF'`) to prevent variable interpolation.
* **Sender Normalization:** The `sender` property in Apple Mail returns raw RFC 2822 format, which may be `"Name <email>"` or just `"email"`. The script extracts the bare email address by parsing angle brackets when present.
* **Display Dialog Quirk:** In Script Editor, `display dialog` buttons may not respond to mouse clicks. This is a known macOS/Script Editor issue. Use Enter/Return to dismiss (the default button is always set). This is a development-only issue — it does not affect Karabiner-triggered execution.
* **CSV Config Encoding:** The contacts CSV and own-addresses file are read as UTF-8. If editing in German Excel and saving as CSV, ensure UTF-8 encoding is selected (Excel's default "CSV UTF-8" option works). The CSV uses semicolons as delimiters for German Excel compatibility.
