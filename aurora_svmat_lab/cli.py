from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .export import export_beam_rows, export_plan_rows, export_trajectory_rows, write_metric_rows_to_csv
from .service import analyze_directory, analyze_plan_file


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aurora_svmat_cli")
    parser.add_argument("--input-file", type=str, default="")
    parser.add_argument("--input-dir", type=str, default="")
    parser.add_argument("--output-csv", type=str, default="")
    parser.add_argument("--beam-output-csv", type=str, default="")
    parser.add_argument("--trajectory-output-csv", type=str, default="")
    parser.add_argument("--verbose", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else [])

    if not args.input_file and not args.input_dir:
        return None

    if args.input_file:
        results = [analyze_plan_file(args.input_file)]
    else:
        results = analyze_directory(args.input_dir)

    if args.verbose:
        for result in results:
            print(f"{result.status}: {result.metadata.plan_name or result.metadata.plan_label} ({result.metadata.manufacturer_model_name})")
            if result.reason:
                print(f"  Reason: {result.reason}")
            for metric_name, metric_value in result.plan_metrics.items():
                print(f"  {metric_name}: {metric_value}")

    if args.output_csv:
        write_metric_rows_to_csv(Path(args.output_csv), export_plan_rows(results))
    if args.beam_output_csv:
        write_metric_rows_to_csv(Path(args.beam_output_csv), export_beam_rows(results))
    if args.trajectory_output_csv:
        write_metric_rows_to_csv(Path(args.trajectory_output_csv), export_trajectory_rows(results))

    return None
