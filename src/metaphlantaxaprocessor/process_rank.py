import os
import csv
import re


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
