# Simulated Long-read RNA-Seq Datasets

## Overview

We generated 40 simulated long-read RNA-seq datasets to comprehensively benchmark fusion detection tools across different sequencing platforms, coverage depths, read accuracies, and read lengths.

## Dataset Generation Pipeline

### 1. Fusion Transcript Simulation

Fusion transcripts were generated using **FusionSimulatorToolkit**:

```bash
# Generate 500 fusion transcripts
FusionTranscriptSimulator \
    gencode.v44.annotation.gff3 \
    GRCh38.primary_assembly.genome.fa \
    500 > fusion_transcripts.fasta
```

**Reference Data**:
- Genome: GRCh38 primary assembly
- Annotation: GENCODE V44 comprehensive gene annotation
- Fusion Count: 500 randomly selected gene pairs

### 2. Read Simulation with Badread

All datasets were simulated using **Badread v0.4.1** with controlled parameters to avoid artificial chimeric reads:

```bash
badread simulate \
    --reference fusion_transcripts.fasta \
    --quantity 10x \
    --length 15000,13000 \
    --identity 95,99,2.5 \
    --error_model nanopore2023 \
    --qscore_model nanopore2023 \
    --junk_reads 0 \
    --random_reads 0 \
    --chimeras 0 \
    --glitches 0,0,0 \
    > simulated_reads.fastq
```

**Critical Parameters**:
- `--junk_reads 0`: No adapter/low-quality sequences
- `--random_reads 0`: No random sequence contamination
- `--chimeras 0`: No artificial chimeric reads (only biological fusions)
- `--glitches 0,0,0`: No sequencing artifacts

### Parameter Space

| Parameter | Values |
|-----------|--------|
| **Platform** | ONT 2018, ONT 2020, ONT 2023, PacBio 2016, PacBio 2021 |
| **Coverage** | 1×, 10×, 100× |
| **Mean Identity** | 80%, 85%, 99.8%, 95% *(legacy ONT2018/2020 only)* |
| **Mean Read Length** | 300bp, 1kb, 5kb, 15kb, 50kb |

### All Datasets (15 total)

#### Oxford Nanopore Datasets (5)

**ONT 2023 Chemistry**:
- `nanopore2023_10x_0.8_15000` - 10× coverage, 80% identity, 15kb reads
- `nanopore2023_10x_0.85_15000` - 10× coverage, 85% identity, 15kb reads
- `nanopore2023_10x_0.998_15000` - 10× coverage, 99.8% identity, 15kb reads ⭐ *Default*

**ONT 2020 Chemistry**:
- `nanopore2020_10x_0.95_15000` - 10× coverage, 95% identity, 15kb reads *(legacy profile)*

**ONT 2018 Chemistry**:
- `nanopore2018_10x_0.95_15000` - 10× coverage, 95% identity, 15kb reads *(legacy profile)*

#### PacBio Datasets (10)

**PacBio 2021 (Sequel IIe HiFi)**:
- `pacbio2021_1x_0.998_15000` - 1× coverage, 99.8% identity, 15kb reads
- `pacbio2021_10x_0.998_15000` - 10× coverage, 99.8% identity, 15kb reads ⭐ *Default*
- `pacbio2021_100x_0.998_15000` - 100× coverage, 99.8% identity, 15kb reads
- `pacbio2021_10x_0.998_300` - 10× coverage, 99.8% identity, 300bp reads
- `pacbio2021_10x_0.998_1000` - 10× coverage, 99.8% identity, 1kb reads
- `pacbio2021_10x_0.998_5000` - 10× coverage, 99.8% identity, 5kb reads
- `pacbio2021_10x_0.998_50000` - 10× coverage, 99.8% identity, 50kb reads

**PacBio 2016 (RS II, P6-C4 Chemistry)**:
- `pacbio2016_10x_0.998_15000` - 10× coverage, 99.8% identity, 15kb reads *(high-accuracy platform cohort)*

⭐ *Default datasets* are recommended for initial benchmarking.


## Download Instructions

### Option 1: Google Drive (Recommended for Individual Datasets)

Download individual datasets from Google Drive:

```bash
# Install gdown for Google Drive downloads
pip install gdown

# Download a specific dataset (example)
gdown --id FILE_ID -O nanopore2023_10x_0.95_15000.tar.gz
tar -xzf nanopore2023_10x_0.95_15000.tar.gz
```

**Google Drive Links**:
- Full dataset collection: [INSERT GOOGLE DRIVE LINK]
- Individual datasets: See table below

### Option 2: Zenodo (Recommended for Complete Collection)

Download the complete dataset collection from Zenodo (with permanent DOI):

```bash
# Download complete collection (~500 GB)
wget https://zenodo.org/record/XXXXXX/files/fusion_benchmark_simulated_data.tar.gz
tar -xzf fusion_benchmark_simulated_data.tar.gz
```

**Zenodo Repository**: [INSERT ZENODO DOI LINK]

### Option 3: Command Line Download Script

Use our automated download script:

```bash
# Download specific datasets
bash download_simulated_data.sh \
    --datasets nanopore2023_10x_0.95_15000,pacbio2021_10x_0.998_15000 \
    --output_dir ./simulated_data

# Download all datasets
bash download_simulated_data.sh --all --output_dir ./simulated_data
```

## Dataset Structure

Each dataset contains:

```
nanopore2023_10x_0.95_15000/
├── reads.fastq                          # Simulated reads
├── fusion_truth.txt                     # Ground truth fusion list
├── CTAT-LR-Fusion/                      # Tool results
│   ├── ctat-LR-fusion.fusion_predictions.tsv
│   └── ...
├── JAFFAL/
├── LongGF/
├── FusionSeeker/
├── FLAIR-fusion/
├── pbfusion/
├── IFDlong/
├── genion/
└── FUGAREC/
```

## File Formats

### reads.fastq
Standard FASTQ format with simulated long reads

### fusion_truth.txt
Ground truth fusion list with format:
```
GeneA--GeneB    TranscriptA--TranscriptB    Breakpoint_Info
```

### Tool Results
Each tool produces its own output format. See tool documentation for details.

## Data Statistics

| Metric | Value |
|--------|-------|
| Total Datasets | 40 |
| Total Size (compressed) | ~500 GB |
| Reads per Dataset | Variable (1× to 100× coverage) |
| Fusion Transcripts | 500 per dataset |
| Reference Genome | GRCh38 |
| Annotation Version | GENCODE V44 |

## Reproducibility

To regenerate any dataset:

```bash
# Example: nanopore2023_10x_0.95_15000
badread simulate \
    --reference fusion_transcripts_500.fasta \
    --quantity 10x \
    --length 15000,13000 \
    --identity 95,99,2.5 \
    --error_model nanopore2023 \
    --qscore_model nanopore2023 \
    --junk_reads 0 \
    --random_reads 0 \
    --chimeras 0 \
    --glitches 0,0,0 \
    --seed 12345 \
    > nanopore2023_10x_0.95_15000.fastq
```

See complete simulation commands in [TableS3_Simulated_Datasets.csv](../docs/TableS3_Simulated_Datasets.csv)

## Citation

If you use these datasets, please cite:

```
[Your Paper Citation]
```

And also cite:

- **Badread**: Wick RR (2019) Badread: simulation of error-prone long reads. Journal of Open Source Software, 4(36), 1316.
- **FusionSimulatorToolkit**: Haas BJ et al. (2019) https://github.com/FusionSimulatorToolkit/FusionSimulatorToolkit
- **GENCODE**: Frankish A et al. (2021) GENCODE 2021. Nucleic Acids Res.

## Contact

For questions about the datasets:
- Open an issue on GitHub
- Email: [YOUR_EMAIL]

---

**Last Updated**: January 2026  
**Dataset Version**: 1.0
