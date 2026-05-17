"""
Tests for Scurry Mail Exporter — suffix_helper.py

Covers:
- determine_suffix() pure logic (directionality, abbreviation lookup, capping, dedup)
- File loading functions (comments, blank lines, case normalisation)
- CLI integration smoke test
"""

import os
import subprocess
import sys

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

# Locate project paths relative to this test file:
#   tests/MailExporter/test_suffix_helper.py  →  project root is three levels up
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_ROOT = os.path.dirname(TEST_DIR)
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
FIXTURES_DIR = os.path.join(TESTS_ROOT, "fixtures", "MailExporter")
SCRIPT_PATH = os.path.join(PROJECT_ROOT, "macros", "MailExporter", "suffix_helper.py")

# Import the module under test
sys.path.insert(0, os.path.join(PROJECT_ROOT, "macros", "MailExporter"))
from suffix_helper import determine_suffix, load_contacts, load_own_addresses


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

# A simple contacts dictionary and own-addresses set for pure logic tests.
# These mirror the fixture files but are defined inline so pure logic tests
# don't depend on the filesystem.

CONTACTS = {
    "john.doe@gmail.com": "JD",
    "foo.bar@yahoo.de": "FB",
    "bla.heul@seier.nl": "BH",
    "reier-seier@blubber.de": "RS",
}

OWN_ADDRESSES = {"fschuhi@yahoo.com"}


# ===========================================================================
# Incoming email tests
# ===========================================================================


class TestIncoming:
    """Tests for incoming emails (sender is NOT in own_addresses)."""

    def test_known_sender(self):
        """Incoming from a known contact produces (ABBREV)."""
        result = determine_suffix(
            sender="john.doe@gmail.com",
            to_list=["fschuhi@yahoo.com"],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == "(JD)"

    def test_unknown_sender(self):
        """Incoming from an unknown contact produces empty string."""
        result = determine_suffix(
            sender="stranger@unknown.org",
            to_list=["fschuhi@yahoo.com"],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == ""

    def test_case_insensitive_sender(self):
        """Sender lookup is case-insensitive."""
        result = determine_suffix(
            sender="John.Doe@Gmail.COM",
            to_list=["fschuhi@yahoo.com"],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == "(JD)"


# ===========================================================================
# Outgoing email tests
# ===========================================================================


class TestOutgoing:
    """Tests for outgoing emails (sender IS in own_addresses)."""

    def test_single_known_recipient(self):
        result = determine_suffix(
            sender="fschuhi@yahoo.com",
            to_list=["john.doe@gmail.com"],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == "(to JD)"

    def test_two_known_recipients(self):
        result = determine_suffix(
            sender="fschuhi@yahoo.com",
            to_list=["john.doe@gmail.com", "foo.bar@yahoo.de"],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == "(to JD, FB)"

    def test_three_known_recipients(self):
        result = determine_suffix(
            sender="fschuhi@yahoo.com",
            to_list=[
                "john.doe@gmail.com",
                "foo.bar@yahoo.de",
                "bla.heul@seier.nl",
            ],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == "(to JD, FB, BH)"

    def test_four_recipients_capped_at_three(self):
        """More than 3 known recipients → only first 3 abbreviations."""
        result = determine_suffix(
            sender="fschuhi@yahoo.com",
            to_list=[
                "john.doe@gmail.com",
                "foo.bar@yahoo.de",
                "bla.heul@seier.nl",
                "reier-seier@blubber.de",
            ],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == "(to JD, FB, BH)"

    def test_mixed_known_and_unknown(self):
        """Unknown recipients are silently skipped."""
        result = determine_suffix(
            sender="fschuhi@yahoo.com",
            to_list=[
                "stranger@unknown.org",
                "john.doe@gmail.com",
                "another@mystery.net",
                "foo.bar@yahoo.de",
            ],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == "(to JD, FB)"

    def test_all_unknown_recipients(self):
        """All recipients unknown → empty string, no empty parens."""
        result = determine_suffix(
            sender="fschuhi@yahoo.com",
            to_list=["stranger@unknown.org", "another@mystery.net"],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == ""

    def test_no_recipients(self):
        """Empty to_list → empty string."""
        result = determine_suffix(
            sender="fschuhi@yahoo.com",
            to_list=[],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == ""

    def test_duplicate_recipient_deduplication(self):
        """Same recipient listed twice → abbreviation appears only once."""
        result = determine_suffix(
            sender="fschuhi@yahoo.com",
            to_list=["john.doe@gmail.com", "john.doe@gmail.com"],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == "(to JD)"

    def test_order_preserved(self):
        """Abbreviations appear in the order of the To recipient list."""
        result = determine_suffix(
            sender="fschuhi@yahoo.com",
            to_list=["bla.heul@seier.nl", "john.doe@gmail.com"],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == "(to BH, JD)"

    def test_case_insensitive_recipients(self):
        """Recipient lookup is case-insensitive."""
        result = determine_suffix(
            sender="fschuhi@yahoo.com",
            to_list=["FOO.BAR@Yahoo.DE"],
            own_addresses=OWN_ADDRESSES,
            contacts=CONTACTS,
        )
        assert result == "(to FB)"


# ===========================================================================
# File loading tests (using fixtures)
# ===========================================================================


class TestFileLoading:
    """Tests for load_own_addresses() and load_contacts() against fixture files."""

    def test_load_own_addresses(self):
        """Reads addresses, skips comments/blanks, lowercases."""
        path = os.path.join(FIXTURES_DIR, "own_addresses.txt")
        result = load_own_addresses(path)
        assert isinstance(result, set)
        assert "fschuhi@yahoo.com" in result
        # All entries should be lowercase
        for addr in result:
            assert addr == addr.lower()

    def test_load_contacts(self):
        """Reads CSV, skips comments/blanks, lowercases keys, preserves abbreviation case."""
        path = os.path.join(FIXTURES_DIR, "contacts.csv")
        result = load_contacts(path)
        assert isinstance(result, dict)
        # Check a known mapping
        assert result["john.doe@gmail.com"] == "JD"
        assert result["foo.bar@yahoo.de"] == "FB"
        # All keys should be lowercase
        for key in result:
            assert key == key.lower()
        # Comment and blank lines should not produce entries
        assert len(result) == 4


# ===========================================================================
# CLI integration smoke test
# ===========================================================================


class TestCLI:
    """Smoke test calling suffix_helper.py as a subprocess."""

    def test_cli_outgoing(self):
        """CLI produces correct suffix for an outgoing email."""
        result = subprocess.run(
            [
                sys.executable,
                SCRIPT_PATH,
                "--sender", "fschuhi@yahoo.com",
                "--to", "john.doe@gmail.com,foo.bar@yahoo.de",
                "--contacts", os.path.join(FIXTURES_DIR, "contacts.csv"),
                "--own-addresses", os.path.join(FIXTURES_DIR, "own_addresses.txt"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout == "(to JD, FB)"

    def test_cli_incoming(self):
        """CLI produces correct suffix for an incoming email."""
        result = subprocess.run(
            [
                sys.executable,
                SCRIPT_PATH,
                "--sender", "bla.heul@seier.nl",
                "--contacts", os.path.join(FIXTURES_DIR, "contacts.csv"),
                "--own-addresses", os.path.join(FIXTURES_DIR, "own_addresses.txt"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert result.stdout == "(BH)"
