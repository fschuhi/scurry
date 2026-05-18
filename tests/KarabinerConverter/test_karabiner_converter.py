"""
Tests for karabiner_converter.py

Fixture: tests/fixtures/KarabinerConverter/rules.xlsx  (10 carefully chosen rows)
Golden:  tests/fixtures/KarabinerConverter/rules.json   (expected JSON output)

The fixture rows exercise every code path in the converter:
  Row 1:  Simple key remap (no from_mods, no to_mods, no conditions)
  Row 2:  No from_mods + condition_if
  Row 3:  Full featured (from_mods + to_mods + condition_if)
  Row 4:  condition_unless
  Row 5:  Multiple from_modifiers (comma-separated)
  Row 6:  No from_mods but has to_mods
  Row 7:  pointing_button type
  Row 8:  shell_command type
  Row 9:  Multi to_value (comma-separated key sequence)
  Row 10: Multi bundle_identifiers
"""

import json
import os
import sys
import tempfile

import pytest
from openpyxl import load_workbook

# ---------------------------------------------------------------------------
# Path setup (mirrors MailExporter test pattern)
# ---------------------------------------------------------------------------
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_ROOT = os.path.dirname(THIS_DIR)
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
FIXTURES_DIR = os.path.join(TESTS_ROOT, "fixtures", "KarabinerConverter")

# Import the module under test
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts", "KarabinerConverter"))
from karabiner_converter import (
    _normalize_list_cell,
    json_to_xlsx,
    xlsx_to_json,
    COLUMNS,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
FIXTURE_XLSX = os.path.join(FIXTURES_DIR, "rules.xlsx")
GOLDEN_JSON = os.path.join(FIXTURES_DIR, "rules.json")


def _load_golden():
    """Load and return the golden JSON data."""
    with open(GOLDEN_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def _convert_fixture_to_json(tmp_path):
    """Convert the fixture xlsx to JSON in a temp directory, return parsed data."""
    out_json = os.path.join(tmp_path, "output.json")
    xlsx_to_json(FIXTURE_XLSX, out_json)
    with open(out_json, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_manipulators(data):
    """Extract the manipulators list from a Karabiner JSON structure."""
    return data["rules"][0]["manipulators"]


# ---------------------------------------------------------------------------
# TestNormalizeListCell — unit tests for the helper function
# ---------------------------------------------------------------------------
class TestNormalizeListCell:
    """Tests for _normalize_list_cell(), the comma-separated cell parser."""

    def test_none_returns_empty_list(self):
        assert _normalize_list_cell(None) == []

    def test_empty_string_returns_empty_list(self):
        assert _normalize_list_cell("") == []

    def test_single_value(self):
        assert _normalize_list_cell("right_control") == ["right_control"]

    def test_comma_separated(self):
        assert _normalize_list_cell("right_control,left_command") == [
            "right_control",
            "left_command",
        ]

    def test_comma_separated_with_spaces(self):
        assert _normalize_list_cell(" a , b , c ") == ["a", "b", "c"]

    def test_already_a_list(self):
        assert _normalize_list_cell(["a", "b"]) == ["a", "b"]

    def test_list_with_empty_strings_filtered(self):
        assert _normalize_list_cell(["a", "", "  ", "b"]) == ["a", "b"]


# ---------------------------------------------------------------------------
# TestXlsxToJson — convert fixture xlsx → JSON, verify each manipulator
# ---------------------------------------------------------------------------
class TestXlsxToJson:
    """Tests for xlsx_to_json() against the fixture spreadsheet."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Convert fixture once, share across all tests in this class."""
        self.data = _convert_fixture_to_json(str(tmp_path))
        self.manipulators = _get_manipulators(self.data)

    def test_total_manipulator_count(self):
        assert len(self.manipulators) == 10

    def test_title(self):
        assert self.data["title"] == "Capsmove Custom Rules"

    def test_row1_simple_key_remap(self):
        """Row 1: CapsLock -> Right Control. No modifiers, no conditions."""
        m = self.manipulators[0]
        assert m["description"] == "CapsLock -> Hyper (Right Control)"
        assert m["from"]["key_code"] == "caps_lock"
        assert "modifiers" not in m["from"]
        assert len(m["to"]) == 1
        assert m["to"][0] == {"key_code": "right_control"}
        assert "conditions" not in m

    def test_row2_condition_if_no_from_mods(self):
        """Row 2: F1 -> F2, scoped to Parallels. No from_modifiers."""
        m = self.manipulators[1]
        assert m["from"]["key_code"] == "f1"
        assert "modifiers" not in m["from"]
        assert m["to"][0]["key_code"] == "f2"
        assert m["conditions"][0]["type"] == "frontmost_application_if"
        assert r"^com\.parallels\.desktop\.console$" in m["conditions"][0]["bundle_identifiers"]

    def test_row3_full_featured(self):
        """Row 3: from_mods + to_mods + condition_if."""
        m = self.manipulators[2]
        assert m["from"]["key_code"] == "c"
        assert m["from"]["modifiers"]["mandatory"] == ["right_control"]
        assert m["to"][0]["key_code"] == "c"
        assert m["to"][0]["modifiers"] == ["left_control"]
        assert m["conditions"][0]["type"] == "frontmost_application_if"

    def test_row4_condition_unless(self):
        """Row 4: Same key combo but condition_unless (macOS side)."""
        m = self.manipulators[3]
        assert m["conditions"][0]["type"] == "frontmost_application_unless"
        assert m["to"][0]["modifiers"] == ["left_command"]

    def test_row5_multiple_from_modifiers(self):
        """Row 5: Two from_modifiers (right_control + left_command)."""
        m = self.manipulators[4]
        mandatory = m["from"]["modifiers"]["mandatory"]
        assert "right_control" in mandatory
        assert "left_command" in mandatory
        assert len(mandatory) == 2

    def test_row6_no_from_mods_with_to_mods(self):
        """Row 6: fn10 -> Ctrl+F2. No from_mods, but to_mods present."""
        m = self.manipulators[5]
        assert m["from"]["key_code"] == "f10"
        assert "modifiers" not in m["from"]
        assert m["to"][0]["key_code"] == "f2"
        assert m["to"][0]["modifiers"] == ["left_control"]

    def test_row7_pointing_button(self):
        """Row 7: CapsLock + P -> button2 (right click)."""
        m = self.manipulators[6]
        assert len(m["to"]) == 1
        assert m["to"][0] == {"pointing_button": "button2"}

    def test_row8_shell_command(self):
        """Row 8: shell_command — no comma splitting, no modifiers on to item."""
        m = self.manipulators[7]
        assert len(m["to"]) == 1
        assert m["to"][0] == {"shell_command": "echo test"}

    def test_row9_multi_to_value(self):
        """Row 9: Comma-separated to_value expands to 3 separate key_code entries."""
        m = self.manipulators[8]
        assert len(m["to"]) == 3
        assert m["to"][0] == {"key_code": "a"}
        assert m["to"][1] == {"key_code": "b"}
        assert m["to"][2] == {"key_code": "c"}

    def test_row10_multi_bundle_identifiers(self):
        """Row 10: Two bundle_identifiers in one condition."""
        m = self.manipulators[9]
        bundles = m["conditions"][0]["bundle_identifiers"]
        assert len(bundles) == 2
        assert r"^com\.apple\.Terminal$" in bundles
        assert r"^com\.googlecode\.iterm2$" in bundles


# ---------------------------------------------------------------------------
# TestJsonToXlsx — convert golden JSON → xlsx, verify cell values
# ---------------------------------------------------------------------------
class TestJsonToXlsx:
    """Tests for json_to_xlsx() against the golden JSON."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Convert golden JSON to xlsx once, load the workbook."""
        self.out_xlsx = os.path.join(str(tmp_path), "output.xlsx")
        json_to_xlsx(GOLDEN_JSON, self.out_xlsx)
        wb = load_workbook(self.out_xlsx)
        self.ws = wb.active
        # Build a list of row dicts for easier access
        headers = [cell.value for cell in self.ws[1]]
        self.rows = []
        for row in self.ws.iter_rows(min_row=2, values_only=True):
            if any(row):
                self.rows.append(dict(zip(headers, row)))

    def test_row_count(self):
        assert len(self.rows) == 10

    def test_headers_match(self):
        headers = [cell.value for cell in self.ws[1]]
        assert headers == COLUMNS

    def test_shell_command_preserved(self):
        """shell_command row: to_value is the full command, not comma-split."""
        row = self.rows[7]  # Row 8 (0-indexed)
        assert row["to_type"] == "shell_command"
        assert row["to_value"] == "echo test"

    def test_multi_to_value_collapsed(self):
        """Multi to_value: JSON array collapsed back to comma-separated string."""
        row = self.rows[8]  # Row 9 (0-indexed)
        assert row["to_value"] == "a,b,c"

    def test_pointing_button_type(self):
        """pointing_button type preserved in roundtrip."""
        row = self.rows[6]  # Row 7 (0-indexed)
        assert row["to_type"] == "pointing_button"
        assert row["to_value"] == "button2"


# ---------------------------------------------------------------------------
# TestRoundtrip — the ultimate integrity check
# ---------------------------------------------------------------------------
class TestRoundtrip:
    """Roundtrip: xlsx → json → xlsx → json must produce identical JSON."""

    def test_full_roundtrip(self, tmp_path):
        tmp = str(tmp_path)

        # Step 1: fixture xlsx → JSON (pass 1)
        json_pass1 = os.path.join(tmp, "pass1.json")
        xlsx_to_json(FIXTURE_XLSX, json_pass1)

        # Step 2: JSON (pass 1) → xlsx
        xlsx_pass2 = os.path.join(tmp, "pass2.xlsx")
        json_to_xlsx(json_pass1, xlsx_pass2)

        # Step 3: xlsx (pass 2) → JSON (pass 2)
        json_pass2 = os.path.join(tmp, "pass2.json")
        xlsx_to_json(xlsx_pass2, json_pass2)

        # Compare pass 1 and pass 2
        with open(json_pass1, "r", encoding="utf-8") as f:
            data1 = json.load(f)
        with open(json_pass2, "r", encoding="utf-8") as f:
            data2 = json.load(f)

        assert data1 == data2, "Roundtrip produced different JSON"

    def test_matches_golden(self, tmp_path):
        """Freshly converted output must match the golden file exactly."""
        data = _convert_fixture_to_json(str(tmp_path))
        golden = _load_golden()
        assert data == golden


# ---------------------------------------------------------------------------
# TestEdgeCases — error handling and warnings
# ---------------------------------------------------------------------------
class TestEdgeCases:
    """Tests for edge cases: empty rows, missing from_key, missing columns."""

    def test_empty_rows_skipped(self, tmp_path):
        """Rows where all cells are None should be silently skipped."""
        from openpyxl import Workbook

        # Create xlsx with one valid row and one empty row
        wb = Workbook()
        ws = wb.active
        for col_num, header in enumerate(COLUMNS, start=1):
            ws.cell(row=1, column=col_num, value=header)
        # Row 2: empty
        # Row 3: valid
        ws.cell(row=3, column=1, value="Test rule")
        ws.cell(row=3, column=2, value="a")
        ws.cell(row=3, column=4, value="key")
        ws.cell(row=3, column=5, value="b")

        xlsx_path = os.path.join(str(tmp_path), "sparse.xlsx")
        wb.save(xlsx_path)

        json_path = os.path.join(str(tmp_path), "sparse.json")
        xlsx_to_json(xlsx_path, json_path)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(_get_manipulators(data)) == 1

    def test_missing_from_key_skipped(self, tmp_path, capsys):
        """Rows with empty from_key should be skipped with a warning."""
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        for col_num, header in enumerate(COLUMNS, start=1):
            ws.cell(row=1, column=col_num, value=header)
        # Row 2: has description but no from_key
        ws.cell(row=2, column=1, value="Broken rule")
        # Row 3: valid
        ws.cell(row=3, column=1, value="Good rule")
        ws.cell(row=3, column=2, value="a")
        ws.cell(row=3, column=4, value="key")
        ws.cell(row=3, column=5, value="b")

        xlsx_path = os.path.join(str(tmp_path), "no_from_key.xlsx")
        wb.save(xlsx_path)

        json_path = os.path.join(str(tmp_path), "no_from_key.json")
        xlsx_to_json(xlsx_path, json_path)

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Only the valid row should be converted
        assert len(_get_manipulators(data)) == 1
        assert _get_manipulators(data)[0]["description"] == "Good rule"

        # Warning should have been printed
        captured = capsys.readouterr()
        assert "empty from_key" in captured.out

    def test_missing_columns_exits(self, tmp_path):
        """xlsx with missing required columns should cause sys.exit(1)."""
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        # Only write two of the required columns
        ws.cell(row=1, column=1, value="description")
        ws.cell(row=1, column=2, value="from_key")

        xlsx_path = os.path.join(str(tmp_path), "bad_headers.xlsx")
        wb.save(xlsx_path)

        json_path = os.path.join(str(tmp_path), "bad_headers.json")
        with pytest.raises(SystemExit) as exc_info:
            xlsx_to_json(xlsx_path, json_path)
        assert exc_info.value.code == 1
