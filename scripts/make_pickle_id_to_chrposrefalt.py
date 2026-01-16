import argparse
import csv
import gzip
import pickle
from pathlib import Path

# Check if allele is a single-nucleotide variant (A, C, G, T)
def _is_snv_allele(allele: str) -> bool:
    a = (allele or "").strip().upper()
    return len(a) == 1 and a in {"A", "C", "G", "T"}

# Check if a value is missing (empty, NA, NaN, None)
def _is_missing(value: str) -> bool:
    v = (value or "").strip().lower()
    return v in {"", "na", "n/a", "nan", "none"}

"""
Parse command-line arguments for the script.

This function sets up an ArgumentParser to handle inputs for mapping Dylan pickle numeric IDs
to chr_pos_ref_alt using ClinVar data. It defines arguments for the pickle file path,
ClinVar file path, output file path, and maximum number of IDs to process.

Returns:
    argparse.Namespace: Parsed command-line arguments.
"""

"""
Main function to create a mapping from pickle IDs to chr_pos_ref_alt.

This function reads unique IDs from the specified pickle file (up to max-ids), then matches
them against VariationIDs in the ClinVar variant_summary.txt.gz file to generate a TSV
mapping with columns: pickle_ID, Chromosome, PositionVCF, ReferenceAlleleVCF,
AlternateAlleleVCF, and chr_pos_ref_alt.

Note: If you want a “full coverage” mapping (all IDs in the pickle, not just 50k), run with:
python scripts/make_pickle_id_to_chrposrefalt.py --max-ids 100000000
"""

# Parse command-line arguments
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Map Dylan pickle numeric IDs to chr_pos_ref_alt using ClinVar variant_summary.txt.gz. "
            "Assumes pickle rows have an 'ID' field containing an int that matches ClinVar 'VariationID'."
        )
    )
    parser.add_argument(
        "--pickle",
        default="data/Dylan Tan/esm2_selected_features.pkl",
        help="Path to Dylan .pkl (line-by-line pickle)",
    )
    parser.add_argument(
        "--clinvar",
        default="data/clinvar/variant_summary.txt.gz",
        help="Path to ClinVar variant_summary.txt.gz",
    )
    parser.add_argument(
        "--out",
        default="data/processed/pickle_id_to_chrposrefalt.tsv",
        help="Output TSV path",
    )
    parser.add_argument(
        "--ambiguous-out",
        default="data/processed/pickle_id_to_chrposrefalt_ambiguous.tsv",
        help="Output TSV for IDs with >1 possible mapping",
    )
    parser.add_argument(
        "--assembly",
        default="GRCh38",
        help="ClinVar Assembly to keep (GRCh38 or GRCh37). Use '' to disable filtering.", # Default: GRCh38
    )
    parser.add_argument(
        "--max-ids",
        type=int,
        default=50000,
        help="Max IDs to read from the pickle (increase if needed)",
    )
    return parser.parse_args()

# Main function to create mapping from pickle IDs to chr_pos_ref_alt
def main() -> None:
    args = parse_args()

    pkl_path = Path(args.pickle)
    clinvar_path = Path(args.clinvar)
    out_path = Path(args.out)
    ambiguous_out_path = Path(args.ambiguous_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ambiguous_out_path.parent.mkdir(parents=True, exist_ok=True)

    ids: set[int] = set()
    with pkl_path.open("rb") as f:
        while len(ids) < args.max_ids:
            try:
                obj = pickle.load(f)
            except EOFError:
                break
            if isinstance(obj, dict) and "ID" in obj:
                try:
                    ids.add(int(obj["ID"]))
                except Exception:
                    continue

    print(f"Collected {len(ids)} unique IDs from {pkl_path}")

    # Collect candidate mappings per VariationID first, then enforce one-to-one.
    candidates: dict[int, dict[str, tuple[str, str, str, str]]] = {}
    seen_rows = 0
    kept_rows = 0

    with gzip.open(clinvar_path, "rt", newline="") as gz:
        reader = csv.DictReader(gz, delimiter="\t")
        for row in reader:
            seen_rows += 1
            try:
                variation_id = int(row["VariationID"])
            except Exception:
                continue
            if variation_id not in ids:
                continue

            assembly = (row.get("Assembly") or "").strip()
            if args.assembly and assembly and assembly != args.assembly:
                continue

            chrom = (row.get("Chromosome") or "").strip()
            pos = (row.get("PositionVCF") or "").strip()
            ref = (row.get("ReferenceAlleleVCF") or "").strip()
            alt = (row.get("AlternateAlleleVCF") or "").strip()

            if _is_missing(chrom) or _is_missing(pos) or _is_missing(ref) or _is_missing(alt):
                continue
            if not pos.isdigit():
                continue
            if not (_is_snv_allele(ref) and _is_snv_allele(alt)):
                continue

            key = f"{chrom}_{pos}_{ref.upper()}_{alt.upper()}"
            candidates.setdefault(variation_id, {})[key] = (chrom, pos, ref.upper(), alt.upper())
            kept_rows += 1

    unique_written = 0
    ambiguous_written = 0

    with out_path.open("w", newline="") as out, ambiguous_out_path.open("w", newline="") as amb:
        writer = csv.writer(out, delimiter="\t")
        amb_writer = csv.writer(amb, delimiter="\t")

        header = [
            "pickle_ID",
            "Chromosome",
            "PositionVCF",
            "ReferenceAlleleVCF",
            "AlternateAlleleVCF",
            "chr_pos_ref_alt",
        ]
        writer.writerow(header)
        amb_writer.writerow(header + ["n_candidates"])
        
        # Write unique and ambiguous mappings separately 

        for variation_id, key_map in sorted(candidates.items()):
            if len(key_map) == 1:
                (only_key, (chrom, pos, ref, alt)) = next(iter(key_map.items()))
                writer.writerow([variation_id, chrom, pos, ref, alt, only_key])
                unique_written += 1
            else:
                for key, (chrom, pos, ref, alt) in sorted(key_map.items()):
                    amb_writer.writerow([variation_id, chrom, pos, ref, alt, key, len(key_map)])
                    ambiguous_written += 1

    print(f"ClinVar rows scanned: {seen_rows}")
    print(f"ClinVar rows kept after filters: {kept_rows}")
    print(f"Unique mappings written: {unique_written} -> {out_path}")
    print(f"Ambiguous rows written: {ambiguous_written} -> {ambiguous_out_path}")


if __name__ == "__main__":
    main()
