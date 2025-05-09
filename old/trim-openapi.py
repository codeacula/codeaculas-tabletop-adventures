#!/usr/bin/env python3
"""
bundle_and_split_openapi.py – bundle refs and split into ≤N operations.
"""

import argparse
from copy import deepcopy
from pathlib import Path

from prance import ResolvingParser
from ruamel.yaml import YAML

def bundle_spec(src: Path) -> dict:
    parser = ResolvingParser(str(src), lazy=True, strict=False)
    parser.parse()
    return parser.specification

def split_spec(spec: dict, out_prefix: str, max_ops: int) -> None:
    yaml = YAML()
    yaml.preserve_quotes = True

    paths = spec.get("paths", {})
    chunk, ops, idx = {}, 0, 1

    def write_chunk(c: dict, i: int):
        if not c:
            return
        out_file = Path(f"{out_prefix}_part{i:02}.yaml")
        doc = deepcopy(spec)
        doc["paths"] = c
        with out_file.open("w") as fh:
            yaml.dump(doc, fh)
        print(f"✅  Wrote {out_file.name} ({sum(len(m) for m in c.values())} ops)")

    for path, methods in paths.items():
        for verb, operation in methods.items():
            if ops >= max_ops:
                write_chunk(chunk, idx)
                idx += 1
                chunk, ops = {}, 0
            chunk.setdefault(path, {})[verb] = operation
            ops += 1

    write_chunk(chunk, idx)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path, help="Your original YAML spec")
    p.add_argument("-p", "--prefix", default="spec", help="Output prefix")
    p.add_argument("-n", "--max-actions", type=int, default=30, help="Max ops per file")
    args = p.parse_args()

    bundled = bundle_spec(args.input)
    split_spec(bundled, args.prefix, args.max_actions)

if __name__ == "__main__":
    main()
