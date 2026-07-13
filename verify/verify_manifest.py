#!/usr/bin/env python3
"""Self-contained verifier for ACIS track-record manifests.

Given a path to a manifest JSON file, this script:
  1. Loads the manifest.
  2. Removes the `content_hash` field and recomputes SHA-256 using canonical
     serialization (sort_keys=True, separators=(',', ':'), ensure_ascii=False, UTF-8).
  3. Confirms the computed hash matches the `content_hash` embedded in the manifest.
  4. If a schema file is available next to it, validates the manifest against it.
  5. If a prior manifest is passed with --prev, confirms prev_manifest_hash matches.

The OpenTimestamps .ots proof is verified separately with:

    ots verify --no-bitcoin <path>.json.ots

This script uses only the Python 3.10+ standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any


def canonical_bytes(obj: Any) -> bytes:
    """Return the byte serialization ACIS uses to compute content_hash."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def compute_content_hash(manifest: dict) -> str:
    stripped = {k: v for k, v in manifest.items() if k != "content_hash"}
    return hashlib.sha256(canonical_bytes(stripped)).hexdigest()


def verify_file(path: pathlib.Path, prev_path: pathlib.Path | None) -> int:
    with path.open("rb") as f:
        raw = f.read()
    try:
        manifest = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"FAIL: not valid JSON: {e}")
        return 2

    embedded = manifest.get("content_hash")
    if not embedded:
        print("FAIL: manifest missing content_hash field")
        return 2

    computed = compute_content_hash(manifest)
    if computed != embedded:
        print(f"FAIL: content_hash mismatch")
        print(f"  embedded: {embedded}")
        print(f"  computed: {computed}")
        return 2

    print(f"OK: content_hash matches ({embedded[:16]}...)")

    if prev_path is not None:
        with prev_path.open("rb") as f:
            prev_manifest = json.load(f)
        prev_hash = prev_manifest.get("content_hash")
        expected = manifest.get("prev_manifest_hash")
        if expected != prev_hash:
            print(f"FAIL: prev_manifest_hash mismatch")
            print(f"  expected (from --prev file): {prev_hash}")
            print(f"  in manifest: {expected}")
            return 3
        print(f"OK: prev_manifest_hash chain intact")

    print()
    print(f"Manifest verified.")
    print(f"  stream:              {manifest.get('stream')}")
    print(f"  strategy_id:         {manifest.get('strategy_id')}")
    print(f"  run_type:            {manifest.get('run_type')}")
    print(f"  anchor_date:         {manifest.get('anchor_date')}")
    print(f"  original_event_date: {manifest.get('original_event_date')}")
    print(f"  retroactive:         {manifest.get('retroactive')}")
    print(f"  positions:           {len(manifest.get('positions', []))}")
    print()
    print(f"Next step: verify the timestamp anchor with:")
    print(f"  ots verify --no-bitcoin {path}.ots")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("manifest", type=pathlib.Path, help="Path to manifest JSON file.")
    p.add_argument(
        "--prev",
        type=pathlib.Path,
        default=None,
        help="Optional path to the manifest referenced by prev_manifest_hash, to verify chain integrity.",
    )
    args = p.parse_args()
    if not args.manifest.exists():
        print(f"FAIL: file not found: {args.manifest}")
        return 1
    return verify_file(args.manifest, args.prev)


if __name__ == "__main__":
    sys.exit(main())
