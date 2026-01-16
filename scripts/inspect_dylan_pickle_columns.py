import argparse
import pickle
from pathlib import Path


def iter_rows(pkl_path: Path, max_rows: int) -> list[object]:
    rows: list[object] = []
    with pkl_path.open("rb") as f:
        while len(rows) < max_rows:
            try:
                rows.append(pickle.load(f))
            except EOFError:
                break
    return rows


def summarize_columns_from_rows(rows: list[object]) -> dict:
    keys: set[object] = set()
    for obj in rows:
        if isinstance(obj, dict):
            keys.update(obj.keys())
        else:
            # Best-effort: if it's a sequence of pairs, try dict() coercion.
            try:
                keys.update(dict(obj).keys())
            except Exception:
                continue

    cols = list(keys)

    numeric_named = [c for c in cols if isinstance(c, (int, float))]
    string_cols = sorted([c for c in cols if isinstance(c, str)])

    prefix_buckets: dict[str, int] = {}
    for c in string_cols:
        prefix = c.split("_")[0] if "_" in c else c
        prefix_buckets[prefix] = prefix_buckets.get(prefix, 0) + 1

    top_prefixes = sorted(prefix_buckets.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_columns": len(cols),
        "string_columns": string_cols,
        "numeric_named_columns_count": len(numeric_named),
        "numeric_named_columns_preview": numeric_named[:10],
        "top_prefixes": top_prefixes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Dylan Tan line-by-line pickle columns")
    parser.add_argument("--path", required=True, help="Path to .pkl file")
    parser.add_argument("--max-rows", type=int, default=200, help="Max rows to sample")
    parser.add_argument("--max-cols-print", type=int, default=200, help="Max string columns to print fully")
    args = parser.parse_args()

    p = Path(args.path)
    rows = iter_rows(p, max_rows=args.max_rows)
    s = summarize_columns_from_rows(rows)

    print(f"=== {p.name} ===")
    print(f"Rows sampled: {len(rows)}")
    print(f"Total columns: {s['total_columns']}")
    print(f"Numeric-named columns (count): {s['numeric_named_columns_count']}")
    if s["numeric_named_columns_count"]:
        print(f"Numeric-named preview: {s['numeric_named_columns_preview']}")

    print("Top string-column prefixes (prefix,count):")
    for pref, cnt in s["top_prefixes"]:
        print(f"  {pref}: {cnt}")

    scols = s["string_columns"]
    if len(scols) <= args.max_cols_print:
        print("String columns:")
        for c in scols:
            print(f"  {c}")
    else:
        print(f"String columns: {len(scols)} total; first 80:")
        for c in scols[:80]:
            print(f"  {c}")
        print("...")
        for c in scols[-20:]:
            print(f"  {c}")


if __name__ == "__main__":
    main()
