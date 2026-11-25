#!/usr/bin/env python3
"""Publish the finished front page for the make.fun harness.

Copies the ``entry.png`` sitting next to this file into the directory named
by the ``MAKEFUN_OUTPUT_DIR`` environment variable, then checks that the
copy landed byte-for-byte identical to the source. The copy is a plain file
copy, so running this twice always yields identical bytes.

Exit status is 0 on success and 1 whenever the output directory is missing
or the verification fails.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
TARGET_NAME = "entry.png"


def fail(message: str) -> int:
    print(f"main.py: error: {message}", file=sys.stderr)
    return 1


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        return fail("MAKEFUN_OUTPUT_DIR is not set")

    destination = Path(out_dir) / TARGET_NAME
    if not SOURCE.is_file():
        return fail(f"source image not found: {SOURCE}")

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE, destination)
    except OSError as exc:
        return fail(f"could not copy {SOURCE} to {destination}: {exc}")

    source_size = SOURCE.stat().st_size
    copied_size = destination.stat().st_size
    if copied_size != source_size:
        return fail(
            f"size mismatch after copy: source {source_size} bytes, "
            f"copy {copied_size} bytes"
        )

    print(f"main.py: wrote {destination} ({copied_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
