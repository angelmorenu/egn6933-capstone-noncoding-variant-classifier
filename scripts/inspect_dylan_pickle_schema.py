# !/usr/bin/env python3
# Inspect Dylan Tan line-by-line pickle schema files.
import argparse
import math
import pickle
from collections import Counter
from pathlib import Path
from typing import Any

# Check if a value is NaN
def is_nan(value: Any) -> bool:
    try:
        return isinstance(value, float) and math.isnan(value)
    except Exception:
        return False

# Try to safely get the shape of an embedding-like object
def safe_shape(value: Any) -> str | None:
    # torch.Tensor / numpy arrays often have .shape
    shape = getattr(value, "shape", None)
    if shape is not None:
        try:
            return str(tuple(shape))
        except Exception:
            return str(shape)

    # torch.Tensor also has .size()
    size = getattr(value, "size", None)
    if callable(size):
        try:
            return str(tuple(size()))
        except Exception:
            return None

    return None

# Read up to max_rows objects from a pickle file
def read_rows(pkl_path: Path, max_rows: int) -> list[Any]:
    rows: list[Any] = []
    with pkl_path.open("rb") as f:
        while len(rows) < max_rows:
            try:
                rows.append(pickle.load(f))
            except EOFError:
                break
    return rows

# CLI tool that inspects the contents of a pickled dataset (presumably a list of rows) and prints schema-like statistics.
def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Dylan Tan line-by-line pickle schema")
    parser.add_argument("--path", required=True, help="Path to .pkl file")
    parser.add_argument("--max-rows", type=int, default=500, help="Max rows to sample")
    parser.add_argument("--id-samples", type=int, default=10, help="How many ID samples to print")
    parser.add_argument("--pathogenicity-samples", type=int, default=20, help="How many Pathogenicity samples to print")
    args = parser.parse_args()

    p = Path(args.path)
    rows = read_rows(p, max_rows=args.max_rows)

    key_union: set[Any] = set()
    row_types = Counter(type(r).__name__ for r in rows)

    # If rows are dict-like, gather keys + simple stats
    path_vals: list[Any] = []  # Pathogenicity values
    id_vals: list[Any] = []
    embedding_types = Counter()  
    embedding_keys = Counter()
    embedding_36_shapes = Counter()
    missing_counts = Counter()

    for r in rows:
        if isinstance(r, dict):   # Dict-like rows
            key_union.update(r.keys()) # Collect all keys

            if "Pathogenicity" in r:
                path_vals.append(r.get("Pathogenicity"))
            if "ID" in r:
                id_vals.append(r.get("ID"))

            if "Embedding" in r:
                emb = r.get("Embedding")
                embedding_types[type(emb).__name__] += 1
                if isinstance(emb, dict):
                    for k in emb.keys():
                        embedding_keys[str(k)] += 1
                    if "36" in emb:
                        embedding_36_shapes[safe_shape(emb["36"]) or "<no-shape>"] += 1

            for k, v in r.items():
                if v is None or is_nan(v):
                    missing_counts[str(k)] += 1
        else:
            # Not dict rows: we can still try to learn something from repr
            pass

    print(f"=== {p.name} ===")
    print(f"Rows sampled: {len(rows)}")
    print("Row python types (count):")
    for t, c in row_types.most_common():
        print(f"  {t}: {c}")

    if key_union:
        keys_sorted = sorted([str(k) for k in key_union])
        print(f"\nUnion of dict keys ({len(keys_sorted)}):")
        for k in keys_sorted:
            print(f"  {k}")

    if path_vals:
        uniq = Counter(str(v) for v in path_vals)  # Unique pathogenicity values
        types = Counter(type(v).__name__ for v in path_vals) # Types of pathogenicity values
        print("\nPathogenicity:")
        print("  Value types:")
        for t, c in types.most_common():
            print(f"    {t}: {c}")
        print("  Unique values (top 30):")
        for v, c in uniq.most_common(30):
            print(f"    {v}: {c}")
        print(f"  Samples (first {min(args.pathogenicity_samples, len(path_vals))}):")  # Print some samples
        for v in path_vals[: args.pathogenicity_samples]:
            print(f"    {v!r}")

    if id_vals:
        id_types = Counter(type(v).__name__ for v in id_vals)  # Types of ID values
        print("\nID:")
        print("  Value types:")
        for t, c in id_types.most_common():
            print(f"    {t}: {c}")
        print(f"  Samples (first {min(args.id_samples, len(id_vals))}):")
        for v in id_vals[: args.id_samples]:
            print(f"    {v!r}")

    if embedding_types:
        print("\nEmbedding:")
        print("  Container types:")
        for t, c in embedding_types.most_common():
            print(f"    {t}: {c}")
        if embedding_keys:
            print("  Dict keys (key,count):")
            for k, c in embedding_keys.most_common():
                print(f"    {k}: {c}")
        if embedding_36_shapes:
            print("  Shapes for Embedding['36']:")
            for s, c in embedding_36_shapes.most_common():
                print(f"    {s}: {c}")

    if missing_counts:
        print("\nMissing values (None/NaN) per key (top 30):")
        for k, c in missing_counts.most_common(30):
            print(f"  {k}: {c}")


if __name__ == "__main__":
    main()
