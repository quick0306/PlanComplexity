from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from metric_definition_catalog import export_metric_definitions


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="export_metric_definitions")
    parser.add_argument(
        "--csv-path",
        default=str(Path("output") / "metric_definitions_all.csv"),
        help="Path to the exported CSV definition table.",
    )
    parser.add_argument(
        "--markdown-path",
        default=str(Path("docs") / "metric_definitions_all.md"),
        help="Path to the exported Markdown definition document.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    export_metric_definitions(csv_path=args.csv_path, markdown_path=args.markdown_path)


if __name__ == "__main__":
    main()
