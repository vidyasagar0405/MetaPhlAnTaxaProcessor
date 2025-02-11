#!/usr/bin/env python3
import os
import argparse
from metaphlantaxaprocessor.utils import check_and_create_dir, combine_csv_to_xlsx, process_all_ranks

def main():
    parser = argparse.ArgumentParser( description="Process taxonomy TSV file into CSVs and optionally combine them into an XLSX workbook.")
    parser.add_argument("infile", help="Input TSV file")
    parser.add_argument( "--outdir", default=None, help="Output directory (default: '<prefix>-taxa')")
    parser.add_argument( "--combine", action="store_true", help="Combine CSV files into a single XLSX workbook")
    args = parser.parse_args()

    infile = args.infile
    if not os.path.isfile(infile):
        print(f"Error: Input file '{infile}' not found.")
        exit(1)

    prefix = os.path.splitext(infile)[0]
    outdir = args.outdir if args.outdir else f"{prefix}-taxa"

    check_and_create_dir(outdir)

    # Define the taxonomic levels.
    levels = [
        ("Kingdom", "k__", "p__"),
        ("Phyla", "p__", "c__"),
        ("Class", "c__", "o__"),
        ("Order", "o__", "f__"),
        ("Family", "f__", "g__"),
        ("Genus", "g__", "s__"),
        ("Species", "s__", "t__"),
        ("Species_with_strain", "t__", None, "s__"),
    ]

    process_all_ranks(infile, outdir, levels)

    if args.combine:
        combine_csv_to_xlsx(outdir, prefix, levels)


if __name__ == "__main__":
    main()
