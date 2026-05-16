#!/usr/bin/env python3
from pathlib import Path
import sys


def read_text_with_fallback(filepath: Path) -> str:
    """Read a text file, trying UTF-8 first, then Mac Roman.

    AppleScript files saved by Script Editor typically use Mac Roman
    encoding (ISO-8859 family) rather than UTF-8.  Characters like
    the « » chevrons in four-character codes (e.g. «class isot»)
    and em dashes are not valid UTF-8.

    Returns the file content as a string.
    Raises OSError if the file cannot be read at all.
    """
    raw = filepath.read_bytes()

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        pass

    # Mac Roman is the native encoding for Script Editor files
    # and correctly handles «, », em dashes, and other Mac-specific
    # characters that Latin-1 would map to wrong code points.
    return raw.decode("mac_roman")


def concat(list_file: Path, out):
    if not list_file.exists():
        out.write(f"Error: Cannot read file '{list_file}'\n")
        return 1

    try:
        # utf-8-sig handles potential BOMs
        lines = list_file.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeDecodeError) as e:
        out.write(f"Error: Cannot read file '{list_file}': {e}\n")
        return 1

    # Write the opening root tag
    out.write("<documents>\n")

    for raw in lines:
        name = raw.strip()

        # Skip empty lines and comments
        if not name or name.startswith("#"):
            continue

        p = Path(name)
        if p.exists() and p.is_file():
            try:
                content = read_text_with_fallback(p)
                # Build the document block via concatenation instead of
                # str.format() — file content may contain curly braces
                # (e.g. AppleScript's `set myList to {}`) which .format()
                # interprets as placeholder tokens.
                out.write(f'\n<document path="{name}">\n')
                out.write(content)
                out.write("\n</document>\n")
            except (OSError, UnicodeDecodeError) as e:
                sys.stderr.write(f"Error: Cannot read file '{name}': {e}\n")
                out.write(f"\n")
        else:
            sys.stderr.write(f"Error: Cannot find file '{name}'\n")
            out.write(f"\n")

    # Write the closing root tag
    out.write("</documents>\n")
    return 0


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 1 or argv[0] in {"-h", "--help"}:
        sys.stderr.write("Usage: python tools/concat_files.py <filelist>\n")
        return 2

    list_file = Path(argv[0])
    return concat(list_file, sys.stdout)


if __name__ == "__main__":
    sys.exit(main())
