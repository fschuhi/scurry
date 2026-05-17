#!/usr/bin/env python3
"""
Scurry Mail Exporter — Suffix Helper

Determines email directionality (incoming vs outgoing) and generates
a folder name suffix based on abbreviation lookups.

Usage:
    python3 suffix_helper.py --sender "addr" --contacts path --own-addresses path [--to "addr1,addr2"]

Output (stdout):
    "(to JD, FB)"   — outgoing with known recipients
    "(JD)"          — incoming with known sender
    ""              — no known matches (empty string, no newline)
"""

import argparse
import csv
import sys


def load_own_addresses(path):
    """Load own email addresses from a text file (one per line).

    Skips blank lines and lines starting with '#'.
    All addresses are lowercased for case-insensitive matching.
    """
    addresses = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            addresses.add(stripped.lower())
    return addresses


def load_contacts(path):
    """Load the abbreviation dictionary from a semicolon-delimited CSV.

    Expects a header row: address;abbreviation
    Skips blank lines and lines starting with '#'.
    Addresses are lowercased; abbreviations are preserved as-is.

    Returns a dict mapping lowercased email address to abbreviation.
    Note: if the same address appears multiple times, last entry wins.
    """
    contacts = {}
    with open(path, encoding="utf-8") as f:
        # Pre-filter: remove blank lines and comment lines before
        # handing to the CSV reader, so they don't confuse it.
        clean_lines = [
            line for line in f if line.strip() and not line.strip().startswith("#")
        ]

    reader = csv.DictReader(clean_lines, delimiter=";")
    for row in reader:
        address = row["address"].strip().lower()
        abbreviation = row["abbreviation"].strip()
        if address and abbreviation:
            contacts[address] = abbreviation

    return contacts


def determine_suffix(sender, to_list, own_addresses, contacts, max_recipients=3):
    """Build the directionality suffix for a folder name.

    Args:
        sender: Bare email address of the sender (str).
        to_list: List of bare To recipient email addresses (list[str]).
        own_addresses: Set of own email addresses (set[str]).
        contacts: Dict mapping email address to abbreviation (dict[str, str]).
        max_recipients: Maximum number of abbreviations in outgoing suffix.

    Returns:
        Suffix string, e.g. "(to JD, FB)" or "(JD)" or "".
    """
    sender_lower = sender.strip().lower()

    # Direction: if sender is one of our own addresses, it's outgoing
    is_outgoing = sender_lower in own_addresses

    if is_outgoing:
        # Look up each To recipient in order, deduplicate, cap at max
        seen = set()
        abbreviations = []
        for addr in to_list:
            addr_lower = addr.strip().lower()
            if addr_lower in seen:
                continue
            seen.add(addr_lower)
            abbrev = contacts.get(addr_lower)
            if abbrev:
                abbreviations.append(abbrev)
                if len(abbreviations) >= max_recipients:
                    break

        if not abbreviations:
            return ""
        return "(to " + ", ".join(abbreviations) + ")"

    else:
        # Incoming: look up the sender
        abbrev = contacts.get(sender_lower)
        if abbrev:
            return "(" + abbrev + ")"
        return ""


def main():
    parser = argparse.ArgumentParser(
        description="Generate folder name suffix for Scurry Mail Exporter."
    )
    parser.add_argument(
        "--sender", required=True, help="Bare email address of the sender."
    )
    parser.add_argument(
        "--to",
        default="",
        help="Comma-separated bare email addresses of To recipients.",
    )
    parser.add_argument(
        "--contacts", required=True, help="Path to contacts.csv (semicolon-delimited)."
    )
    parser.add_argument(
        "--own-addresses",
        required=True,
        help="Path to own_addresses.txt.",
    )

    args = parser.parse_args()

    own_addresses = load_own_addresses(args.own_addresses)
    contacts = load_contacts(args.contacts)

    # Parse the --to argument into a list, handling empty string
    if args.to.strip():
        to_list = [addr.strip() for addr in args.to.split(",")]
    else:
        to_list = []

    suffix = determine_suffix(args.sender, to_list, own_addresses, contacts)

    # Print without trailing newline — AppleScript captures this directly
    sys.stdout.write(suffix)


if __name__ == "__main__":
    main()
