#!/usr/bin/env python3
"""Ship It Friday entry: write one commit message to /output/entry.txt.

The competition asks for the funniest one-line git commit message an AI
coding agent writes in the moment before it breaks production on a
Friday. This program writes exactly that one line, byte for byte, every
time it runs: no input, no network, no randomness, no clock. It runs on
Python 3.13 with the standard library only.

After writing, it reads the file back and compares the bytes on disk
with the line it meant to write. If they differ for any reason, it
fails loudly instead of exiting as if everything were fine.
"""

from __future__ import annotations

import hashlib
import os
import sys

LINE = "fix: production was down on a Friday, so I renamed it to staging \u2014 uptime is back to 100% and nobody has noticed yet"

OUTPUT_PATH = "/output/entry.txt"

# Pinned digest of the exact bytes this program must write: the 116-char
# line encoded as UTF-8 (118 bytes, the em dash takes three bytes).
EXPECTED_SHA256 = "1e4cd3fe693f23deb72d5d0322eabad6eb25fe39e6c315cfdb323614979ae289"
EXPECTED_BYTES = 118


def write_entry() -> bytes:
    """Write the line to /output/entry.txt and return its exact bytes."""
    data = LINE.encode("utf-8")
    if not 1 <= len(LINE) <= 159:
        raise ValueError(f"line is {len(LINE)} characters, gate needs 1-159")
    if not LINE.strip():
        raise ValueError("line must not be only white space")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "wb") as handle:
        handle.write(data)
    return data


def verify(expected: bytes) -> str:
    """Read the file back and fail unless it matches byte for byte.

    Checks the exact bytes, the exact length (118), and the pinned
    sha256 digest; returns the digest on success so main can confirm it.
    """
    with open(OUTPUT_PATH, "rb") as handle:
        actual = handle.read()
    if actual != expected:
        raise RuntimeError(
            f"read-back mismatch: wrote {len(expected)} bytes, "
            f"found {len(actual)} bytes on disk"
        )
    if len(actual) != EXPECTED_BYTES:
        raise RuntimeError(
            f"read-back length: found {len(actual)} bytes, "
            f"expected {EXPECTED_BYTES}"
        )
    digest = hashlib.sha256(actual).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(
            f"read-back sha256: found {digest}, expected {EXPECTED_SHA256}"
        )
    return digest


def main() -> int:
    try:
        expected = write_entry()
        digest = verify(expected)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"verified: {len(LINE)} chars, sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
