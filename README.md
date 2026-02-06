# Google Timeline Splicer

Filter Google Timeline JSON exports to a specific datetime range.

## Usage

```bash
python splice_timeline.py <input.json> <output.json> -s <start> -e <end>
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input`  | Input Google Timeline JSON file |
| `output` | Output JSON file |
| `-s/--start` | Start datetime (ISO 8601) |
| `-e/--end` | End datetime (ISO 8601) |

### Example

```bash
# Extract data for December 13, 2012
python splice_timeline.py Timeline.json dec13.json \
  -s "2012-12-13T00:00:00+01:00" \
  -e "2012-12-14T00:00:00+01:00"
```

## Notes

- Segments that **overlap** with the specified range are included (partial matches count)
- Requires Python 3.7+
- No external dependencies

## Disclosure

This has been one-shot generated via Claude Opus 4.5.
