import numpy as np
import pandas as pd

LEVELS = [
    ("Kingdom", "k__", "p__"),
    ("Phyla", "p__", "c__"),
    ("Class", "c__", "o__"),
    ("Order", "o__", "f__"),
    ("Family", "f__", "g__"),
    ("Genus", "g__", "s__"),
    ("Species", "s__", "t__"),
    ("Species_with_strain", "t__", None, "s__"),
]

file = "mock_data.tsv"

def process_rank(df, rank, include, exclude=None, remove_pattern=None):

    df.columns = [rank, "NCBI_tax_id", "relative_abundance", "OTU"]

    if remove_pattern is None:
        remove_pattern = include

    df = df[df[rank].str.contains(include, na=False)].copy()

    if exclude is not None:
        df = df[~df[rank].str.contains(exclude, na=False)].copy()

    df.loc[:, rank] = df[rank].str.replace(fr'^.*{remove_pattern}', '', regex=True)
    df.loc[:, rank] = df[rank].str.replace('_', ' ')

    if rank == "Species_with_strain":
        df[rank] = df[rank].replace('\|t  ', ' (', regex=True)
        df[rank] = df[rank].replace(r'$', ')', regex=True)

    df['NCBI_tax_id'] = df['NCBI_tax_id'].apply(lambda x: np.nan if x.endswith('|') else x.split('|')[-1])

    df.to_csv(f"{rank}.tsv", sep="\t", index=False)

def main():

    df = pd.read_csv(file, sep="\t", header=4)
    df = df[["#clade_name", "NCBI_tax_id", "relative_abundance", "#clade_name"]]
    df = df.rename(columns={'#clade_name': 'clade_name'})

    for level in LEVELS:
        if len(level) == 3:
            rank, include, exclude = level
            remove_pattern = None
        else:
            rank, include, exclude, remove_pattern = level
        process_rank(df, rank, include, exclude, remove_pattern)

if __name__ == "__main__":
    main()
