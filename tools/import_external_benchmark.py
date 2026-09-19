"""Read local UCoMX artifacts and write a numeric-only historical capture."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.external_benchmarks import (
    CAPTURE_DIR, import_ucomx_halcyon_historical, load_external_capture,
)


def _stable_content(capture):
    return {key: value for key, value in capture.items() if key not in {"captured_at", "capture_sha256"}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path)
    parser.add_argument("--output", type=Path, default=CAPTURE_DIR / "ucomx_halcyon_historical.json")
    parser.add_argument("--check", action="store_true", help="Verify reproducibility without writing files.")
    args = parser.parse_args(argv)
    try:
        if args.output.resolve().is_relative_to(args.source_root.resolve()):
            raise ValueError("Capture output must be outside the read-only external source tree.")
        capture = import_ucomx_halcyon_historical(args.source_root, reference_root=args.reference_root)
        if args.check:
            previous = load_external_capture(args.output)
            if _stable_content(previous) != _stable_content(capture):
                raise ValueError("Capture no longer reproduces from the pinned sources.")
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(capture, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    except (ValueError, OSError, KeyError, StopIteration):
        # Avoid displaying private source paths or workbook identity cells.
        print("External capture failed: source provenance or capture reproducibility could not be verified.")
        return 1
    verb = "Verified" if args.check else "Captured"
    print(f"{verb} {capture['benchmark_id']}: {len(capture['samples'])} numeric samples; historical execution unverified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
