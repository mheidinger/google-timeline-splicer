#!/usr/bin/env python3
"""
Google Timeline JSON Splicer

Filters a Google Timeline JSON export to only include segments
within a specified datetime range.
"""

import argparse
import json
import sys
from datetime import datetime, timezone


def parse_iso_datetime(dt_string: str) -> datetime:
    """Parse ISO 8601 datetime string to datetime object."""
    # Handle the format from Google Timeline: 2012-12-12T15:00:00.000+01:00
    # Python's fromisoformat handles this in 3.11+, but for compatibility:
    try:
        # Try standard fromisoformat first (Python 3.11+)
        return datetime.fromisoformat(dt_string)
    except ValueError:
        # Fallback for older Python versions - handle +HH:MM timezone format
        # Replace the timezone offset format if needed
        if dt_string.endswith("Z"):
            dt_string = dt_string[:-1] + "+00:00"

        # Handle milliseconds and timezone
        if "." in dt_string and ("+" in dt_string or "-" in dt_string[10:]):
            # Split off timezone
            if "+" in dt_string[10:]:
                main_part, tz_part = dt_string.rsplit("+", 1)
                tz_sign = "+"
            else:
                main_part, tz_part = dt_string.rsplit("-", 1)
                tz_sign = "-"

            # Parse the main datetime part
            dt = datetime.strptime(main_part, "%Y-%m-%dT%H:%M:%S.%f")

            # Parse timezone offset
            tz_hours, tz_mins = int(tz_part[:2]), int(tz_part[3:5])
            offset_minutes = tz_hours * 60 + tz_mins
            if tz_sign == "-":
                offset_minutes = -offset_minutes

            from datetime import timedelta

            tz = timezone(timedelta(minutes=offset_minutes))
            return dt.replace(tzinfo=tz)

        return datetime.fromisoformat(dt_string)


def segment_overlaps(segment: dict, start: datetime, end: datetime) -> bool:
    """Check if a segment overlaps with the given time range."""
    seg_start = parse_iso_datetime(segment["startTime"])
    seg_end = parse_iso_datetime(segment["endTime"])

    # Overlap exists if: segment starts before range ends AND segment ends after range starts
    return seg_start < end and seg_end > start


def splice_timeline(data: dict, start: datetime, end: datetime) -> dict:
    """Filter timeline data to only include segments overlapping with the range."""
    if "semanticSegments" not in data:
        raise ValueError("Invalid Google Timeline JSON: missing 'semanticSegments' key")

    filtered_segments = [
        segment
        for segment in data["semanticSegments"]
        if segment_overlaps(segment, start, end)
    ]

    return {"semanticSegments": filtered_segments}


def main():
    parser = argparse.ArgumentParser(
        description="Filter Google Timeline JSON to a specific datetime range.",
        epilog='Example: %(prog)s input.json output.json -s "2012-12-13T00:00:00+01:00" -e "2012-12-14T00:00:00+01:00"',
    )
    parser.add_argument("input", help="Input Google Timeline JSON file")
    parser.add_argument("output", help="Output JSON file")
    parser.add_argument(
        "-s",
        "--start",
        required=True,
        help="Start datetime (ISO 8601 format, e.g., 2012-12-13T00:00:00+01:00)",
    )
    parser.add_argument(
        "-e",
        "--end",
        required=True,
        help="End datetime (ISO 8601 format, e.g., 2012-12-14T00:00:00+01:00)",
    )

    args = parser.parse_args()

    # Parse datetime arguments
    try:
        start_dt = parse_iso_datetime(args.start)
        end_dt = parse_iso_datetime(args.end)
    except ValueError as e:
        print(f"Error parsing datetime: {e}", file=sys.stderr)
        print("Use ISO 8601 format, e.g., 2012-12-13T00:00:00+01:00", file=sys.stderr)
        sys.exit(1)

    if start_dt >= end_dt:
        print("Error: start datetime must be before end datetime", file=sys.stderr)
        sys.exit(1)

    # Load input JSON
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Filter data
    try:
        original_count = len(data.get("semanticSegments", []))
        filtered_data = splice_timeline(data, start_dt, end_dt)
        filtered_count = len(filtered_data["semanticSegments"])
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Write output
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(filtered_data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Filtered {original_count} segments to {filtered_count} segments")
    print(f"Output written to: {args.output}")


if __name__ == "__main__":
    main()
