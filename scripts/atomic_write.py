#!/usr/bin/env python3
"""Crash-safe file replacement for the scripts that rewrite shipped content.

`Path.write_text` truncates the target and then writes. Interrupt it — Ctrl-C,
a laptop sleeping, an OOM kill — and the file is left half written. The
scripts that mutate `procedures.json`, `rescue_cards.json`, and `kits.json`
are rewriting the clinical corpus this app ships, so a torn write there is a
truncated procedure library rather than a lost convenience.

Writing to a sibling temp file and then `os.replace` makes the swap atomic on
POSIX and Windows alike: readers see either the old file or the new one, never
a partial one. The temp file is a sibling rather than in the system temp dir
so the rename stays on one filesystem, which is what makes it atomic.
"""

import os
import tempfile
from pathlib import Path


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Replace `path` with `text` atomically."""
    path = Path(path)
    directory = path.parent
    handle, temp_name = tempfile.mkstemp(
        dir=directory, prefix=f".{path.name}.", suffix=".tmp"
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(handle, "w", encoding=encoding, newline="") as stream:
            stream.write(text)
            # The rename is atomic, but it only guarantees that the *name*
            # points at complete bytes once those bytes have reached disk.
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise
