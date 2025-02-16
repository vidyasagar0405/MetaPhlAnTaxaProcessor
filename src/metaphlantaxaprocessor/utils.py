import itertools
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


def get_info(infile, outfile):
    """
    Get metadata from the first 10 lines of the input TSV file.
    """
    with open(infile, "r") as f:
        with open(outfile, "a") as o:
            for line in itertools.islice(f, 10):  # Read only first 10 lines
                if line.startswith("#"):
                    o.write(line)


def get_unclassified(infile, outfile):
    """
    Get the unclassified reads from the input TSV file.
    """
    with open(infile, "r") as f:
        with open(outfile, "a") as o:
            for line in itertools.islice(f, 10):  # Read only first 10 lines
                if line.startswith("#clade_name"):
                    o.write(line.replace("\t", ","))
                if line.startswith("UNCLASSIFIED"):
                    o.write(line.replace("\t", ","))


def get_header(infile) -> int:
    """
    Get the header row number from the input TSV file.
    """
    with open(infile, "r") as f:
        for i, line in enumerate(f):
            if line.startswith("#clade_name"):
                return i
    return 4  # Default header row number

def combine_csv_to_xlsx(outdir, prefix):
    """
    Combine all structured files (CSV/TSV) into an XLSX workbook.
    Plain text files (.txt) are included as raw text.
    """
    prefix = os.path.basename(prefix)
    xlsx_file = os.path.join(outdir, f"{prefix}-taxa.xlsx")

    files = os.listdir(outdir)
    supported_formats = {".csv", ".tsv"}  # Only structured files
    text_formats = {".txt"}  # Read .txt files as raw text

    with pd.ExcelWriter(xlsx_file, engine="openpyxl") as writer:
        for file in files:
            file_path = os.path.join(outdir, file)
            ext = os.path.splitext(file)[-1].lower()

            if ext in supported_formats:  # Process structured files
                try:
                    delimiter = "\t" if ext == ".tsv" else ","
                    df = pd.read_csv(file_path, delimiter=delimiter)

                    sheet_name = os.path.splitext(file)[0][:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                except Exception as e:
                    print(f"⚠️ Skipping {file}: {e}")

            elif ext in text_formats:  # Process plain text files
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    df = pd.DataFrame({"MetaPhlAn run Info": lines})  # Save as one-column DataFrame
                    df.to_excel(writer, sheet_name=file, index=False)
                except Exception as e:
                    print(f"Skipping {file}: {e}")

    print(f"Combined XLSX file written to: {xlsx_file}")

def pre_process_ranks(infile, outdir, levels):
    """
    Process all taxonomic ranks for the given TSV file.
    """

    df = pd.read_csv(infile, sep="\t", header=get_header(infile))

    # Find column containing 'tax' and rename it to 'NCBI_tax_id'
    tax_col = next((col for col in df.columns if "tax" in col.lower()), None)
    if tax_col:
        df = df.rename(columns={tax_col: "NCBI_tax_id"})
    else:
        raise KeyError("No column containing 'tax' found in the file!")

    df = df.rename(columns={"#clade_name": "clade_name"})

    df = df[["clade_name", "NCBI_tax_id", "relative_abundance", "clade_name"]]

    for level in levels:
        if len(level) == 3:
            rank, include, exclude = level
            remove_pattern = None
        else:
            rank, include, exclude, remove_pattern = level
        process_rank(df, outdir, rank, include, exclude, remove_pattern)
