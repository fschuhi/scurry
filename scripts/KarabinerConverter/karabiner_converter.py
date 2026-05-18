#!/usr/bin/env python3
"""
Karabiner Elements JSON <-> Excel Converter
Converts between Karabiner JSON rules and Excel format for easier editing.

Enhancements:
- Support multiple emitted 'to' events per row by comma-separated to_value.
- Applies the same to_modifiers to each emitted 'to' event.
- json2xlsx collapses multiple 'to' events of the same type into comma-separated to_value.
- Support shell_command as to_type (to_modifiers is ignored for this type).
"""

import argparse
import json
import sys
from openpyxl import Workbook, load_workbook

# Column headers for Excel
COLUMNS = [
    'description',
    'from_key',
    'from_modifiers',
    'to_type',
    'to_value',              # can be comma-separated for multiple outputs; for shell_command, the full command string
    'to_modifiers',          # applied to each emitted 'to' event in that row (ignored for shell_command)
    'condition_type',
    'condition_bundle_ids'
]

DEFAULT_TITLE = "Capsmove Custom Rules"


def _normalize_list_cell(cell_value):
    if cell_value is None:
        return []
    if isinstance(cell_value, list):
        return [str(x).strip() for x in cell_value if str(x).strip()]
    # Split by comma
    return [s.strip() for s in str(cell_value).split(',') if s.strip()]


def json_to_xlsx(json_path, xlsx_path):
    """Convert Karabiner JSON to Excel format."""
    print(f"Reading JSON from: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Karabiner Rules"

    # Write headers
    for col_num, header in enumerate(COLUMNS, start=1):
        ws.cell(row=1, column=col_num, value=header)

    # Process all rules from all rule groups
    row_num = 2
    for rule_group in data.get('rules', []):
        for manipulator in rule_group.get('manipulators', []):
            # Extract data
            description = manipulator.get('description', '')

            # FROM section
            from_block = manipulator.get('from', {}) or {}
            from_key = from_block.get('key_code', '') or ''
            from_mods = []
            mods_block = from_block.get('modifiers', {}) or {}
            if isinstance(mods_block, dict):
                from_mods = mods_block.get('mandatory', []) or []
            elif isinstance(mods_block, list):
                # Karabiner also allows a list here (treated as mandatory)
                from_mods = mods_block
            from_modifiers = ','.join(from_mods) if from_mods else ''

            # TO section: collapse multiple 'to' entries if same type
            to_list = manipulator.get('to', []) or []
            to_type = ''
            to_values = []
            to_modifiers = ''

            if to_list:
                # Determine primary type based on first entry
                first = to_list[0]
                if 'key_code' in first:
                    to_type = 'key'
                elif 'pointing_button' in first:
                    to_type = 'pointing_button'
                elif 'shell_command' in first:
                    to_type = 'shell_command'
                else:
                    to_type = ''

                # Collect values of the same type
                mixed_type_warning = False
                collected_mods = None
                for idx, to_item in enumerate(to_list):
                    if to_type == 'key' and 'key_code' in to_item:
                        to_values.append(to_item.get('key_code', ''))
                    elif to_type == 'pointing_button' and 'pointing_button' in to_item:
                        to_values.append(to_item.get('pointing_button', ''))
                    elif to_type == 'shell_command' and 'shell_command' in to_item:
                        to_values.append(to_item.get('shell_command', ''))
                    else:
                        mixed_type_warning = True

                    # If all entries share same modifiers list, keep them; otherwise leave empty
                    # (shell_command entries never have modifiers, so collected_mods stays None)
                    mods = to_item.get('modifiers', None)
                    if mods is not None:
                        # normalize to list of strings
                        if isinstance(mods, list):
                            mods_norm = [str(m).strip() for m in mods if str(m).strip()]
                        else:
                            mods_norm = [str(mods).strip()]
                    else:
                        mods_norm = None

                    if idx == 0:
                        collected_mods = mods_norm
                    else:
                        if collected_mods != mods_norm:
                            collected_mods = None  # inconsistent; drop

                if mixed_type_warning:
                    print("WARNING: Mixed 'to' types in a single manipulator; only the first type is exported to Excel.")
                if collected_mods:
                    to_modifiers = ','.join(collected_mods)

            # CONDITIONS section
            conditions = manipulator.get('conditions', []) or []
            if conditions:
                condition = conditions[0]  # Only first condition exported
                condition_type = condition.get('type', '') or ''
                bundle_ids = condition.get('bundle_identifiers', []) or []
                condition_bundle_ids = ','.join(bundle_ids) if bundle_ids else ''
            else:
                condition_type = ''
                condition_bundle_ids = ''

            # Write row
            ws.cell(row=row_num, column=1, value=description)
            ws.cell(row=row_num, column=2, value=from_key)
            ws.cell(row=row_num, column=3, value=from_modifiers)
            ws.cell(row=row_num, column=4, value=to_type)
            ws.cell(row=row_num, column=5, value=','.join([v for v in to_values if v]))  # comma-separated
            ws.cell(row=row_num, column=6, value=to_modifiers)
            ws.cell(row=row_num, column=7, value=condition_type)
            ws.cell(row=row_num, column=8, value=condition_bundle_ids)

            row_num += 1

    # Save workbook
    wb.save(xlsx_path)
    print(f"Excel file created: {xlsx_path}")
    print(f"Total rows exported: {row_num - 2}")


def xlsx_to_json(xlsx_path, json_path, sheet_name=None, title=DEFAULT_TITLE):
    """Convert Excel format to Karabiner JSON."""
    print(f"Reading Excel from: {xlsx_path}")

    wb = load_workbook(xlsx_path)

    # Use specified sheet or first sheet
    if sheet_name:
        ws = wb[sheet_name]
    else:
        ws = wb.active
        print(f"Using sheet: {ws.title}")

    # Read and validate headers
    headers = [cell.value for cell in ws[1]]

    # Check for required columns
    missing = set(COLUMNS) - set(headers)
    if missing:
        print(f"ERROR: Missing required columns: {', '.join(missing)}")
        sys.exit(1)

    # Build column index map
    col_idx = {header: idx for idx, header in enumerate(headers)}

    # Process rows
    manipulators = []
    for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        # Skip empty rows
        if not any(row):
            continue

        description = row[col_idx['description']] or ''
        from_key = row[col_idx['from_key']] or ''
        if not from_key:
            print(f"WARNING: Row {row_num} has empty from_key; skipping.")
            continue

        manipulator = {
            "description": description,
            "type": "basic",
            "from": {
                "key_code": from_key
            }
        }

        # Add from_modifiers if present
        from_mods_raw = row[col_idx['from_modifiers']]
        from_mods = _normalize_list_cell(from_mods_raw)
        if from_mods:
            manipulator['from']['modifiers'] = {
                "mandatory": from_mods
            }

        # Build TO section supporting multiple values
        to_type = (row[col_idx['to_type']] or '').strip()
        to_values_raw = row[col_idx['to_value']]
        to_mods_raw = row[col_idx['to_modifiers']]
        to_mods = _normalize_list_cell(to_mods_raw)

        to_list = []
        if to_type == 'shell_command':
            # shell_command: to_value is the full command string (not comma-split)
            # We treat the raw cell value as a single string, not a list.
            command = str(to_values_raw).strip() if to_values_raw else ''
            if command:
                to_list.append({'shell_command': command})
            else:
                print(f"WARNING: Row {row_num} has to_type 'shell_command' but empty to_value; skipping.")
        else:
            to_values = _normalize_list_cell(to_values_raw)
            if to_type and to_values:
                for val in to_values:
                    to_item = {}
                    if to_type == 'key':
                        to_item['key_code'] = val
                    elif to_type == 'pointing_button':
                        to_item['pointing_button'] = val
                    else:
                        print(f"WARNING: Row {row_num} has unsupported to_type '{to_type}'; skipping this to_value '{val}'.")
                        continue

                    if to_mods:
                        to_item['modifiers'] = to_mods
                    to_list.append(to_item)

        manipulator['to'] = to_list

        # Add conditions if present
        condition_type = row[col_idx['condition_type']]
        if condition_type:
            bundle_ids_raw = row[col_idx['condition_bundle_ids']]
            bundle_list = _normalize_list_cell(bundle_ids_raw)
            manipulator['conditions'] = [{
                "type": condition_type,
                "bundle_identifiers": bundle_list
            }]

        manipulators.append(manipulator)

    # Build final JSON structure
    output = {
        "title": title,
        "rules": [
            {
                "description": "Karabiner Rules",
                "manipulators": manipulators
            }
        ]
    }

    # Write JSON file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"JSON file created: {json_path}")
    print(f"Total rules converted: {len(manipulators)}")


def main():
    parser = argparse.ArgumentParser(
        description="Karabiner Elements JSON <-> Excel Converter"
    )
    subparsers = parser.add_subparsers(dest='mode', required=True)

    # json2xlsx subcommand
    json2xlsx_parser = subparsers.add_parser(
        'json2xlsx', help='Convert Karabiner JSON to Excel format'
    )
    json2xlsx_parser.add_argument('input_json', help='Path to input JSON file')
    json2xlsx_parser.add_argument('output_xlsx', help='Path to output Excel file')

    # xlsx2json subcommand
    xlsx2json_parser = subparsers.add_parser(
        'xlsx2json', help='Convert Excel format to Karabiner JSON'
    )
    xlsx2json_parser.add_argument('input_xlsx', help='Path to input Excel file')
    xlsx2json_parser.add_argument('output_json', help='Path to output JSON file')
    xlsx2json_parser.add_argument('sheet_name', nargs='?', default=None,
                                  help='Sheet name to use (default: active sheet)')
    xlsx2json_parser.add_argument('--title', default=DEFAULT_TITLE,
                                  help=f'Title for the Karabiner rule set (default: "{DEFAULT_TITLE}")')

    args = parser.parse_args()

    if args.mode == 'json2xlsx':
        json_to_xlsx(args.input_json, args.output_xlsx)
    elif args.mode == 'xlsx2json':
        xlsx_to_json(args.input_xlsx, args.output_json, args.sheet_name, args.title)


if __name__ == '__main__':
    main()
