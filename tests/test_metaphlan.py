import os
import subprocess
import sys
import pytest
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from metaphlantaxaprocessor.utils import (
    check_and_create_dir,
    combine_csv_to_xlsx,
)
from metaphlantaxaprocessor.process_rank import process_rank

LEVELS = [
    ("Kingdom", "k__", "p__"),
    ("Phyla", "p__", "c__"),
    ("Species_with_strain", "t__", None, "s__"),
]

@pytest.fixture
def sample_tsv(tmpdir):
    tsv_content = [
        "k__Bacteria\tdata\t0.8",
        "p__Firmicutes\tdata\t0.6",
        "t__Strain1\tdata\t0.1",
        "invalid_line",
    ]
    file = tmpdir.join("sample.tsv")
    file.write("\n".join(tsv_content))
    return str(file)

# Unit Tests
def test_check_and_create_dir(tmpdir):
    test_dir = tmpdir.join("new_dir")
    check_and_create_dir(str(test_dir))
    assert test_dir.exists()

def test_process_rank(tmpdir):
    infile = tmpdir.join("input.tsv")
    infile.write("k__Bacteria\tx\t0.5\np__Firmicutes\tx\t0.3\n")
    outdir = tmpdir.mkdir("output")

    process_rank(str(infile), str(outdir), "Kingdom", "k__", "p__")

    csv_file = outdir.join("kingdom.csv")
    assert csv_file.read() == (
        "Kingdom,Relative_abundance,OUT\n"
        "Bacteria,0.5,k__Bacteria\n"
    )

def test_combine_csv_to_xlsx(tmpdir):
    outdir = tmpdir.mkdir("output")
    outdir.join("kingdom.csv").write("Kingdom,abundance\nBacteria,0.5")
    combine_csv_to_xlsx(str(outdir), "test", LEVELS)

    xlsx = outdir.join("test-taxa.xlsx")
    df = pd.read_excel(xlsx, sheet_name="Kingdom")
    assert "Bacteria" in df.values

# CLI Tests
def test_cli_basic(sample_tsv, tmpdir):
    cmd = f"metaphlan-taxaprocessor {sample_tsv}"
    result = subprocess.run(cmd, shell=True, check=True)
    assert result.returncode == 0
    outdir = os.path.splitext(sample_tsv)[0] + "-taxa"
    assert os.path.exists(outdir)
    assert os.path.isfile(os.path.join(outdir, "kingdom.csv"))

def test_cli_combine(sample_tsv):
    cmd = f"metaphlan-taxaprocessor {sample_tsv} --combine"
    result = subprocess.run(cmd, shell=True, check=True)
    assert result.returncode == 0
    outdir = os.path.splitext(sample_tsv)[0] + "-taxa"
    assert os.path.isfile(os.path.join(outdir, "sample-taxa.xlsx"))

def test_cli_outdir(sample_tsv, tmpdir):
    custom_out = tmpdir.mkdir("custom_out")
    cmd = f"metaphlan-taxaprocessor {sample_tsv} --outdir {custom_out}"
    subprocess.run(cmd, shell=True, check=True)
    assert os.path.isfile(os.path.join(str(custom_out), "kingdom.csv"))

def test_cli_combine_outdir(sample_tsv, tmpdir):
    custom_out = tmpdir.mkdir("custom_combined")
    cmd = f"metaphlan-taxaprocessor {sample_tsv} --outdir {custom_out} --combine"
    subprocess.run(cmd, shell=True, check=True)
    assert os.path.isfile(os.path.join(str(custom_out), "sample-taxa.xlsx"))

def test_cli_nonexistent_file():
    result = subprocess.run(
        "metaphlan-taxaprocessor nonexistent.tsv",
        shell=True,
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
