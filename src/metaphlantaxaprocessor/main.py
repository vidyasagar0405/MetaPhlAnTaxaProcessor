#!/usr/bin/env python3
import os
import csv
import re
import argparse
import pandas as pd


def check_and_create_dir(outdir):
    """
    Check if the output directory exists, and create it if necessary.
    """
    if not os.path.exists(outdir):
        try:
            os.makedirs(outdir)
        except OSError:
            print(f"Error: Could not create output directory '{outdir}'.")
            exit(1)


def process_rank(infile, outdir, rank, include, exclude=None, remove_pattern=None):
    """
    Process the input TSV file for a given taxonomic level and write out a CSV.

    Parameters:
      infile        : Path to the input TSV file.
      outdir        : Output directory to write the CSV.
      rank          : Taxonomic rank name (e.g., "Kingdom").
      include       : String to include (e.g., "k__").
      exclude       : String to exclude (e.g., "p__"); if None, no exclusion is done.
      remove_pattern: Pattern to remove from the combined fields. If None, defaults to include.
    """
    if remove_pattern is None:
        remove_pattern = include

    header = [rank, "Relative_abundance", "OUT"]
    rows = []

    with open(infile, "r", encoding="utf-8") as fin:
        for line in fin:
            # Only process lines that contain the include pattern.
            if include not in line:
                continue
            # If an exclusion is defined, skip lines containing it.
            if exclude is not None and exclude in line:
                continue
            # Split the line on tab.
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 3:
                print(f"Warning: Skipping line with insufficient columns: {line}")
                continue
            # Mimic: cut -f1,3 | tr '\t' ','
            # Join field 1 and field 3 with a comma.
            combined = f"{fields[0]},{fields[2]}"
            # Remove everything up to and including the remove_pattern.
            processed = re.sub(r".*" + re.escape(remove_pattern), "", combined)
            # The processed result is expected to be two comma-separated values:
            # e.g. if fields[0] was "k__Bacteria" and fields[2] was "0.35",
            # then combined is "k__Bacteria,0.35" and after substitution we get "Bacteria,0.35".
            parts = processed.split(",", 1)
            if len(parts) != 2:
                continue
            taxon, rel_abund = parts
            # For the right-hand side of paste we use the first field.
            out_field = fields[0]
            rows.append([taxon, rel_abund, out_field])

    # Write the CSV file.
    outfile = os.path.join(outdir, f"{rank.lower()}.csv")
    with open(outfile, "w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Written {outfile} with {len(rows)} rows.")


def combine_csv_to_xlsx(outdir, prefix, levels):
    """
    Combine the generated CSV files (one per taxonomic rank) into a single XLSX workbook.
    """
    # Create the output XLSX file inside the output directory.
    prefix = os.path.basename(prefix)

    xlsx_file = os.path.join(outdir, f"{prefix}-taxa.xlsx")
    with pd.ExcelWriter(xlsx_file, engine="openpyxl") as writer:
        for level in levels:
            rank = level[0]
            csv_filename = os.path.join(outdir, f"{rank.lower()}.csv")
            if os.path.exists(csv_filename):
                # Read CSV file into a DataFrame.
                df = pd.read_csv(csv_filename)
                # Use the rank name as the sheet name (limit to 31 characters for Excel).
                sheet_name = rank if len(rank) <= 31 else rank[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Combined XLSX file written to {xlsx_file}")


def process_all_ranks(infile, outdir, levels):
    """
    Process all taxonomic ranks for the given TSV file.
    """
    for level in levels:
        if len(level) == 3:
            rank, include, exclude = level
            remove_pattern = None
        else:
            rank, include, exclude, remove_pattern = level
        process_rank(infile, outdir, rank, include, exclude, remove_pattern)


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
