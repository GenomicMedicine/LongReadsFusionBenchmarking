# Real Long-read RNA-Seq Datasets

## Overview

We analyzed real long-read RNA-seq datasets from multiple cell lines and platforms to validate fusion detection performance on biological data.

## Dataset Catalog

| Sample / Cell Line | Sequencing Platform | Biological Origin / Cancer Type | Data Source / Accession |
|---|---|---|---|
| MCF7, SKBR3 | PacBio Iso-Seq | Breast Cancer | SRA: SRP055913, SRP150606 |
| HCT116 | PacBio Iso-Seq | Colon Cancer | SRA: SRP091981 (PRJNA321560) |
| MCF7, A549, K562, HCT116, HepG2, H9, HEYA8 | Oxford Nanopore (ONT) | Multiple Cancer Types | GoekeLab sg-nex-data (https://github.com/GoekeLab/sg-nex-data/) |
| Colon Cancer (Primary) | Long-read RNA-seq | Colon Cancer | GEO: GSE155921 (PRJNA656187) |
| AML (Primary) | Long-read RNA-seq | Acute Myeloid Leukemia | BioProject: PRJNA640456 |
| NA12878 | Oxford Nanopore (ONT) | Normal Human Cell Line | Nanopore WGS Consortium (https://github.com/nanopore-wgs-consortium/NA12878) |
| UHR (Universal Human Reference) | ONT (GridION) | Pooled (10 Cell Lines) | BioProject: PRJNA639366 |


## Download Instructions

```bash
# Download from SRA
prefetch SRRXXXXXX
fastq-dump --split-files SRRXXXXXX
```

## Known Fusions

### HCC827
- **EML4-ALK** (validated, targetable)
- Additional fusions detected

### K562
- **BCR-ABL1** (Philadelphia chromosome, validated)
- Additional fusions detected

### MCF7
- Multiple recurrent fusions
- Literature-validated events

### SKBR3
- **ERBB2** amplification-related events
- NRG1 fusions

### Hct116
- Colorectal cancer-associated fusions

### NCI-H1975
- **EGFR** mutations (not fusions)
- Additional fusion events

## Data Statistics

| Metric | Value |
|--------|-------|
| Total Cell Lines | 13 bulk |
| ONT Datasets | 15 |
| PacBio Datasets | 4 |
| Illumina Datasets | 2 |
| Total Size | ~800 GB |

## Multi-platform Cell Lines

Three cell lines have data from multiple platforms for cross-platform validation:

### HCC827
- **ONT**: PromethION, ~50× coverage
- **PacBio**: Sequel IIe, ~30× coverage  
- **Illumina**: NovaSeq, ~100M reads

### Hct116
- **ONT**: PromethION, ~40× coverage
- **PacBio**: Sequel II, ~25× coverage

### MCF7
- **ONT**: PromethION, ~45× coverage
- **PacBio**: Sequel IIe, ~30× coverage

### NCI-H1975
- **ONT**: PromethION, ~55× coverage
- **Illumina**: NovaSeq, ~100M reads

## Analysis Results

Pre-computed results from all 9 tools are included for each dataset:

- Fusion predictions (TSV/CSV format)
- Read support information
- Quality metrics
- Junction sequences

## Usage Example

```bash
# Download and analyze HCC827 data
gdown --id FILE_ID -O HCC827_ONT.tar.gz
tar -xzf HCC827_ONT.tar.gz

# Run analysis scripts
cd analysis_scripts
python generate_all_figures.py \
    --real_data ../data/HCC827/ONT \
    --output results/

# Generate comparison plots
python 02_upset_plot.py --input ../data/HCC827/ONT
python 03_method_consensus_plot.py --input ../data/HCC827/ONT
```

## Validation Approach

For cell lines with known fusions:

1. **Literature Validation**: Compared to published fusion events
2. **Illumina Cross-validation**: For multi-platform datasets
3. **Sanger Sequencing**: Selected events were validated (where applicable)
4. **Database Matching**: Checked against FusionGDB, COSMIC, ChimerDB

## Citation

If you use these datasets, please cite the original data sources:

- For SRA datasets, cite the original studies
- For cell line characterization, cite ATCC/vendor documentation

## Contact

For questions about the real datasets:
- Open an issue on GitHub

## Acknowledgments

We thank:
- Original data generators and submitters
- SRA/ENA for data hosting
- Cell line repositories (ATCC, etc.)

---

**Last Updated**: January 2026  
**Dataset Version**: 1.0
