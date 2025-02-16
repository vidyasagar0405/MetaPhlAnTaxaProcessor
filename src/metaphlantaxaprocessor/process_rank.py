import pandas as pd
import numpy as np

def process_rank(df, outdir, rank, include, exclude=None, remove_pattern=None):
    """
    Process the input TSV file for a given taxonomic level and write out a CSV.

    Parameters:
      outdir        : Output directory to write the CSV.
      rank          : Taxonomic rank name (e.g., "Kingdom").
      include       : String to include (e.g., "k__").
      exclude       : String to exclude (e.g., "p__"); if None, no exclusion is done.
      remove_pattern: Pattern to remove from the combined fields. If None, defaults to include.
    """

    df.columns = [rank, "NCBI_tax_id", "relative_abundance", "OTU"]

    if remove_pattern is None:
        remove_pattern = include

    df = df[df[rank].str.contains(include, na=False)].copy()

    if exclude is not None:
        df = df[~df[rank].str.contains(exclude, na=False)].copy()

    df.loc[:, rank] = df[rank].str.replace(fr'^.*{remove_pattern}', '', regex=True)
    df.loc[:, rank] = df[rank].str.replace('_', ' ')

    if rank == "Species_with_strain":
        df[rank] = df[rank].replace('\\|t  ', ' (', regex=True)
        df[rank] = df[rank].replace(r'$', ')', regex=True)

    df['NCBI_tax_id'] = df['NCBI_tax_id'].apply(lambda x: np.nan if x.endswith('|') else x.split('|')[-1])

    df.to_csv(f"{outdir}/{rank}.csv", index=False)
    print(f"Processed {rank} and wrote to {outdir}/{rank}.csv")
