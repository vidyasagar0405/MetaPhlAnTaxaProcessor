import os
import pandas as pd
from metaphlantaxaprocessor.process_rank import process_rank


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
