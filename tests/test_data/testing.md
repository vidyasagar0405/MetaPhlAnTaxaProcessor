import pandas as pd
import numpy as np

df = pd.read_csv("mock_data.tsv", sep="\t", header=4)
df = df[["#clade_name", "NCBI_tax_id", "relative_abundance", "#clade_name"]]
df = df.rename(columns={'#clade_name': 'clade_name'})
df.columns = ["clade_name", "NCBI_tax_id", "relative_abundance", "OTU"]

df = df[df['clade_name'].str.contains('s__', na=False)]
df = df[~df['clade_name'].str.contains('t__', na=False)]
df['clade_name'] = df['clade_name'].str.replace(r'^.*s__', '', regex=True)
df['NCBI_tax_id'] = df['NCBI_tax_id'].apply(lambda x: np.nan if x.endswith('|') else x.split('|')[-1])
