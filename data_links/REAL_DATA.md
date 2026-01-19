# Real Long-read RNA-Seq Datasets

## Overview

We analyzed real long-read RNA-seq datasets from multiple cell lines and platforms to validate fusion detection performance on biological data.

## Dataset Catalog

### Bulk RNA-seq Datasets

| Cell Line | Platform | Data Type | Fusions Known | Source |
|-----------|----------|-----------|---------------|--------|
| **A549** | ONT | Bulk | Yes | Lung adenocarcinoma |
| **AML** | ONT | Bulk | Yes | Acute myeloid leukemia |
| **H9** | ONT | Bulk | No | Embryonic stem cells |
| **HCC827** | ONT, Illumina, PacBio | Bulk | Yes | Lung adenocarcinoma |
| **Hct116** | ONT, PacBio | Bulk | Yes | Colorectal carcinoma |
| **HepG2** | ONT | Bulk | Yes | Hepatocellular carcinoma |
| **HEYA8** | ONT | Bulk | Yes | Ovarian carcinoma |
| **K562** | ONT | Bulk | Yes | Chronic myelogenous leukemia |
| **MCF7** | ONT, PacBio | Bulk | Yes | Breast adenocarcinoma |
| **NA12878** | ONT | Bulk | No | Normal B-lymphocyte |
| **NCI-H1975** | ONT, Illumina | Bulk | Yes | Lung adenocarcinoma |
| **SKBR3** | PacBio | Bulk | Yes | Breast adenocarcinoma |
| **UHR** | ONT | Bulk | No | Universal Human Reference |

### Single-cell RNA-seq Datasets

| Sample | Platform | Data Type | Source |
|--------|----------|-----------|--------|
| **CC** | ONT | scRNA-seq | Cell line culture |
| **H838** | ONT | scRNA-seq | Lung cancer |
| **HCC** | ONT | scRNA-seq | Hepatocellular carcinoma |
| **LBT** | ONT | scRNA-seq | Lung tissue |

## Data Structure

Each dataset directory contains:

```
HCC827/
├── ONT/
│   ├── reads.fastq.gz                   # Raw reads
│   ├── aligned.bam                      # Aligned reads (if available)
│   ├── known_fusions.txt                # Known/validated fusions
│   ├── CTAT-LR-Fusion/                  # Tool results
│   ├── JAFFAL/
│   ├── LongGF/
│   ├── FusionSeeker/
│   ├── FLAIR-fusion/
│   ├── pbfusion/
│   ├── IFDlong/
│   ├── genion/
│   └── FUGAREC/
├── Illumina/                            # Short-read data (if available)
│   └── ...
└── PacBio/                              # PacBio data (if available)
    └── ...
```

## Download Instructions

### Option 1: Google Drive

Download individual datasets:

```bash
# Install gdown
pip install gdown

# Download HCC827 ONT data
gdown --id FILE_ID -O HCC827_ONT.tar.gz
tar -xzf HCC827_ONT.tar.gz
```

**Google Drive Links**:
- Complete collection: [INSERT GOOGLE DRIVE LINK]
- Individual cell lines: See table below

### Option 2: Zenodo

Download from Zenodo (permanent DOI):

```bash
wget https://zenodo.org/record/XXXXXX/files/fusion_benchmark_real_data.tar.gz
tar -xzf fusion_benchmark_real_data.tar.gz
```

**Zenodo Repository**: [INSERT ZENODO DOI LINK]

### Option 3: Original Data Sources

Some datasets are publicly available from original sources:

| Dataset | Source | Accession |
|---------|--------|-----------|
| HCC827 | SRA | PRJNA XXX |
| K562 | SRA | PRJNA XXX |
| NA12878 | SRA | PRJNA XXX |

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
| Total Cell Lines | 13 bulk + 4 scRNA-seq |
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

If you use these datasets, please cite:

```
[Your Paper Citation]
```

And cite the original data sources:

- For SRA datasets, cite the original studies
- For cell line characterization, cite ATCC/vendor documentation

## Contact

For questions about the real datasets:
- Open an issue on GitHub
- Email: [YOUR_EMAIL]

## Acknowledgments

We thank:
- Original data generators and submitters
- SRA/ENA for data hosting
- Cell line repositories (ATCC, etc.)

---

**Last Updated**: January 2026  
**Dataset Version**: 1.0
