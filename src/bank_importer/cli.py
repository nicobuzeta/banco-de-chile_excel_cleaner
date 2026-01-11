import argparse
import sys
from pathlib import Path

from . import importers  # noqa: F401 - triggers auto-registration
from .registry import ImporterRegistry
from .writer import write_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Bank statement importer")
    parser.add_argument("input_file", nargs="?", help="Input file path")
    parser.add_argument("-i", "--importer", help="Importer name (required)")
    parser.add_argument("-o", "--output", help="Output CSV path")
    parser.add_argument(
        "--list-importers", action="store_true", help="List available importers"
    )

    args = parser.parse_args()

    if args.list_importers:
        print("Available importers:")
        for imp in ImporterRegistry.list_all():
            exts = ", ".join(imp.supported_extensions)
            print(f"  {imp.name:<30} {imp.description} [{exts}]")
        return 0

    if not args.input_file:
        print("Error: input_file is required", file=sys.stderr)
        return 1

    if not args.importer:
        print("Error: --importer is required", file=sys.stderr)
        print("Use --list-importers to see available options", file=sys.stderr)
        return 1

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        return 1

    try:
        importer_class = ImporterRegistry.get(args.importer)
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    importer = importer_class()
    try:
        transactions = importer.parse(input_path)
    except ValueError as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else input_path.with_suffix(".csv")
    write_csv(transactions, output_path)

    print(f"Wrote {len(transactions)} transactions to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
