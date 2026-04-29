import argparse
from analysis_console import log_metric_summary, log_plan_summary
from analysis_logging import configure_logging
from ucomx_service import analyze_plan_file

def build_parser():
    parser = argparse.ArgumentParser(description="Analyze a single RT Plan DICOM file.")
    parser.add_argument("--input-file", required=True, help="Path to the RT Plan DICOM file.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    return parser


def main():
    args = build_parser().parse_args()
    logger = configure_logging(args.verbose)
    pfile = args.input_file

    try:
        result = analyze_plan_file(pfile)
    except Exception as exc:
        logger.exception("Failed to analyze RT Plan file %s: %s", pfile, exc)
        raise

    log_plan_summary(logger, result.metadata)
    log_metric_summary(logger, result.metrics)
    for warning in result.warnings:
        logger.warning(warning)


if __name__ == '__main__':
    main()
