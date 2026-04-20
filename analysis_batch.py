import csv
import os
from concurrent.futures import ThreadPoolExecutor

from analysis_console import log_batch_plan_summary
from ucomx_models import AnalysisMode
from ucomx_service import analyze_plan_file


def process_batch(
    *,
    logger,
    filepaths,
    output_csv,
    header,
    build_row,
    metadata_filter,
    precheck=None,
    requested_mode=AnalysisMode.AUTO,
):
    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(header)

        max_workers = min(4, max(1, os.cpu_count() or 1))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for row in executor.map(
                lambda pfile: _process_batch_file(
                    logger=logger,
                    pfile=pfile,
                    build_row=build_row,
                    metadata_filter=metadata_filter,
                    precheck=precheck,
                    requested_mode=requested_mode,
                ),
                filepaths,
            ):
                if row is not None:
                    writer.writerow(row)


def _process_batch_file(*, logger, pfile, build_row, metadata_filter, precheck, requested_mode):
    logger.info("Processing file: %s", pfile)

    if precheck is not None:
        try:
            should_continue = precheck(logger, pfile)
        except Exception as exc:
            logger.exception("Skipping file due to precheck failure %s: %s", pfile, exc)
            return None
        if not should_continue:
            return None

    try:
        result = analyze_plan_file(pfile, requested_mode=requested_mode)
        metadata = result.metadata
    except Exception as exc:
        logger.exception("Skipping file due to parse failure %s: %s", pfile, exc)
        return None

    log_batch_plan_summary(logger, metadata)

    if not result.supported:
        logger.warning("Skipping file %s: %s", pfile, " | ".join(result.warnings) or "unsupported plan")
        return None

    keep_reason = metadata_filter(metadata)
    if keep_reason is not None:
        logger.warning("Skipping file %s: %s", pfile, keep_reason)
        return None

    try:
        row = build_row(metadata, result.metrics)
    except Exception as exc:
        logger.exception("Skipping file due to metric/export failure %s: %s", pfile, exc)
        return None

    logger.debug("CSV row for %s: %s", pfile, row)
    return row

