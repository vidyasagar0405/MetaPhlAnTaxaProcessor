# MetaPhlAnTaxaProcessor

[![PyPI - Version](https://img.shields.io/pypi/v/metaphlantaxaprocessor.svg)](https://pypi.org/project/metaphlantaxaprocessor)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/metaphlantaxaprocessor.svg)](https://pypi.org/project/metaphlantaxaprocessor)

-----

MetaPhlAnTaxaProcessor is a Python-based utility designed to streamline the downstream analysis of MetaPhlAn output. It processes MetaPhlAn's taxonomic profiling data, converting it into structured CSV files for each taxonomic rank (e.g., Kingdom, Phyla, Class, etc.). Additionally, it offers the option to consolidate these CSV files into a single Excel workbook, with each sheet named after the corresponding taxonomic rank. This tool enhances the accessibility and interpretability of metagenomic data, facilitating further statistical analysis and visualization.

-----

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

You can install the latest version of MetaPhlAnTaxaProcessor using pip:

```console
pip install metaphlantaxaprocessor
```

## Usage

Once installed, you can use MetaPhlAnTaxaProcessor via the command line to process your MetaPhlAn output files.

### Basic Command

```console
metaphlan-taxaprocessor.main INPUT_TSV_FILE
```

Where `INPUT_TSV_FILE` is the path to your MetaPhlAn-generated TSV file.

### Available Options

- `--outdir`: Specify the output directory for the generated CSV files (default is `<prefix>-taxa`).
- `--combine`: Optionally combine the generated CSV files into a single Excel workbook.

Example usage with options:

```console
metaphlan-taxaprocessor.main tests/test_data/Galaxy-res.tsv --outdir ./output --combine
```

This command will process the `Galaxy-res.tsv` file and store the CSVs in the `./output` directory, then combine them into a single Excel workbook.

## License

`metaphlantaxaprocessor` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
