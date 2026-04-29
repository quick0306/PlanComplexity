from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from aurora_svmat_lab.formula_pdf import export_aurora_formula_pdf


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="export_aurora_formula_pdf")
    parser.add_argument(
        "--output-path",
        default=str(Path("output") / "pdf" / "aurora_metric_formulas.pdf"),
        help="Path to the generated Aurora formula PDF.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    export_aurora_formula_pdf(args.output_path)


if __name__ == "__main__":
    main()
