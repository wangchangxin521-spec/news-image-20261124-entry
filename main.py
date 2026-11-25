#!/usr/bin/env python3
"""Entry point for the news-image-20261124 competition.

Copies the pre-built entry.png (in this same directory) to
$MAKEFUN_OUTPUT_DIR/entry.png. Standard library only, no network.

The copy is done as an explicit binary read/write in fixed-size chunks,
and the written file is checked to have exactly the source's byte count,
so both graded runs produce byte-identical output.
"""

import os
import sys

CHUNK = 65536


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        sys.exit(1)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print("entry.png not found next to main.py", file=sys.stderr)
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    expected = os.path.getsize(src)
    written = 0
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            block = fin.read(CHUNK)
            if not block:
                break
            fout.write(block)
            written += len(block)
    if written != expected or os.path.getsize(dst) != expected:
        print("entry.png copy incomplete: wrote %d of %d bytes"
              % (written, expected), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
