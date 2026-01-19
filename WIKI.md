# Fusion Detection Benchmark Wiki

## Table of Contents

1. [Home](#home)
2. [Quick Start](#quick-start)
3. [Docker Containers](#docker-containers)
4. [Simulated Data Generation](#simulated-data-generation)
5. [Real Data Analysis](#real-data-analysis)
6. [Performance Evaluation](#performance-evaluation)
7. [Tool Comparison](#tool-comparison)
8. [Troubleshooting](#troubleshooting)

---

## Home

### Overview

This benchmark study evaluates 9 fusion detection tools for long-read RNA sequencing:

- **CTAT-LR-Fusion** - CTAT suite for long reads
- **JAFFAL** - Hybrid alignment + assembly
- **LongGF** - Clustering-based detection
- **FusionSeeker** - Advanced filtering
- **FLAIR-fusion** - Isoform-aware detection
- **pbfusion** - PacBio-optimized
- **IFDlong** - Integrated filtering
- **genion** - Machine learning classifier
- **FUGAREC** - Fusion reconstruction

### Key Features

- ✅ **Comprehensive Evaluation**: 40 simulated datasets + 17 real datasets
- ✅ **Multiple Platforms**: ONT (2018/2020/2023), PacBio (2016/2021)
- ✅ **Reproducible**: Docker containers for all tools
- ✅ **Well-documented**: Complete analysis scripts and documentation

### Dataset Overview

**Simulated Data**:
- 40 datasets with varying coverage (1×-100×), identity (80%-99.8%), and length (300bp-50kb)
- 500 fusion transcripts per dataset
- Generated with Badread + FusionSimulatorToolkit

**Real Data**:
- 13 cancer cell lines
- 4 single-cell datasets
- Multiple sequencing platforms

---

## Quick Start

### Prerequisites

```bash
# System requirements
- Docker 20.10+
- Python 3.7+
- 16GB+ RAM
- 100GB+ disk space
```

### Installation

```bash
# 1. Clone repository
git clone https://github.com/GenomicMedicine/LongReadsFusionBenchmarking.git
cd LongReadsFusionBenchmarking

# 2. Build Docker containers
cd dockerfiles/CTAT-LR-Fusion_docker
docker build -t LongReadsFusionBenchmarking/ctat-lr-fusion:latest .

# 3. Install Python dependencies
pip install pandas numpy matplotlib seaborn scipy upsetplot
```

### Running Your First Analysis

```bash
# Download example dataset
wget [EXAMPLE_DATASET_LINK] -O example_data.tar.gz
tar -xzf example_data.tar.gz

# Run CTAT-LR-Fusion
cd dockerfiles/CTAT-LR-Fusion_docker
bash run_CTAT-LR-Fusion.sh \
    ../../example_data/reads.fastq \
    /path/to/genome_lib \
    ../../results/ctat-lr-fusion

# Analyze results
cd ../../analysis_scripts
python collect_benchmark.py \
    --simulated_dir ../example_data \
    --output results.csv
```

---

## Docker Containers

### Building All Containers

```bash
cd dockerfiles
for tool_dir in */; do
    cd "$tool_dir"
    tool_name=$(basename "$tool_dir" | sed 's/_docker//')
    echo "Building $tool_name..."
    docker build -t "LongReadsFusionBenchmarking/${tool_name}:latest" .
    cd ..
done
```

### Running Individual Tools

#### CTAT-LR-Fusion

```bash
cd dockerfiles/CTAT-LR-Fusion_docker
bash run_CTAT-LR-Fusion.sh \
    /path/to/input.fastq \
    /path/to/ctat_genome_lib \
    /path/to/output
```

**CTAT Genome Library Setup**:
```bash
# Download pre-built library
wget https://data.broadinstitute.org/Trinity/CTAT_RESOURCE_LIB/GRCh38_gencode_v44_CTAT_lib.tar.gz
tar -xzf GRCh38_gencode_v44_CTAT_lib.tar.gz
```

#### JAFFAL

```bash
cd dockerfiles/jaffal_docker
bash run_JAFFAL.sh \
    /path/to/input.fastq \
    /path/to/genome_lib \
    /path/to/output
```

#### LongGF

```bash
cd dockerfiles/longgf_docker
bash run_LongGF.sh \
    /path/to/input.fastq \
    /path/to/genome.fa \
    /path/to/output
```

### Common Parameters

All wrapper scripts accept:
- **Input**: FASTQ file (gzipped or uncompressed)
- **Reference**: Genome library or FASTA file
- **Output**: Output directory (created if doesn't exist)
- **Optional**: Tool-specific parameters

---

## Simulated Data Generation

### Step 1: Generate Fusion Transcripts

Using **FusionSimulatorToolkit**:

```bash
# Clone FusionSimulatorToolkit
git clone https://github.com/FusionSimulatorToolkit/FusionSimulatorToolkit.git
cd FusionSimulatorToolkit

# Generate 500 fusions
./FusionTranscriptSimulator \
    gencode.v44.annotation.gff3 \
    GRCh38.primary_assembly.genome.fa \
    500 > fusion_transcripts_500.fasta
```

**Output**: `fusion_transcripts_500.fasta` containing:
- 500 random fusion transcripts
- Exon-exon junctions
- Consensus splice sites maintained

### Step 2: Simulate Reads with Badread

```bash
# Install Badread
pip install badread

# Example: ONT 2023, 10x coverage, 95% identity, 15kb reads
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

**Critical Parameters**:
- `--junk_reads 0`: No adapter contamination
- `--random_reads 0`: No random sequences
- `--chimeras 0`: No artificial chimeras (only biological fusions)
- `--glitches 0,0,0`: No sequencing artifacts

### Step 3: Generate All 40 Datasets

Use the provided `makefusion.sh` script:

```bash
bash makefusion.sh
```

This generates:
- 15 ONT datasets (2018/2020/2023 chemistries)
- 15 PacBio 2016 datasets
- 10 PacBio 2021 HiFi datasets

### Parameter Space

| Parameter | Values |
|-----------|--------|
| Coverage | 1×, 5×, 10×, 50×, 100× |
| Identity | 80%, 85%, 90%, 95%, 99.8% |
| Read Length | 300bp, 1kb, 5kb, 15kb, 50kb |
| Platform | ONT 2018/2020/2023, PacBio 2016/2021 |

---

## Real Data Analysis

### Downloading Real Datasets

```bash
# Download from provided links
wget [REAL_DATA_LINK] -O real_data.tar.gz
tar -xzf real_data.tar.gz
```

### Running Tools on Real Data

```bash
# Process all cell lines with CTAT-LR-Fusion
for cell_line in real_data/*/ONT/; do
    cell=$(basename $(dirname "$cell_line"))
    bash dockerfiles/CTAT-LR-Fusion_docker/run_CTAT-LR-Fusion.sh \
        "${cell_line}/reads.fastq" \
        /path/to/genome_lib \
        "results/${cell}/CTAT-LR-Fusion"
done
```

### Analyzing Results

```bash
cd analysis_scripts

# Generate UpSet plot (tool overlap)
python 02_upset_plot.py \
    --input ../real_data/HCC827/ONT \
    --output upset_HCC827.pdf

# Generate consensus plot
python 03_method_consensus_plot.py \
    --input ../real_data/HCC827/ONT \
    --output consensus_HCC827.pdf

# Generate all figures
python generate_all_figures.py \
    --real_data ../real_data \
    --output real_results/
```

### Known Fusion Validation

For cell lines with known fusions (e.g., HCC827 with EML4-ALK):

```bash
python 06_ppv_tpr_plot.py \
    --input ../real_data/HCC827/ONT \
    --known_fusions ../real_data/HCC827/known_fusions.txt \
    --output ppv_tpr_HCC827.pdf
```

---

## Performance Evaluation

### Collecting Tool Results

```bash
cd analysis_scripts

# Collect predictions from all tools
python collect_benchmark.py \
    --simulated_dir ../simulated_data \
    --tools CTAT-LR-Fusion,JAFFAL,LongGF,FusionSeeker,FLAIR-fusion,pbfusion,IFDlong,genion,FUGAREC \
    --output benchmark_results.csv
```

**Output**: CSV file with columns:
- Dataset, Tool, GeneA, GeneB, BreakpointA, BreakpointB, JunctionReads, SpanningReads

### Calculating Performance Metrics

```bash
python calculate_performance.py \
    --input benchmark_results.csv \
    --truth ../simulated_data/fusion_truth.txt \
    --output performance_metrics.csv
```

**Metrics Calculated**:
- Sensitivity (Recall) = TP / (TP + FN)
- Precision (PPV) = TP / (TP + FP)
- F1-Score = 2 × (Precision × Recall) / (Precision + Recall)
- Matthews Correlation Coefficient (MCC)
- False Discovery Rate (FDR)

### Generating Figures

#### Main Figure (Figure 2)

```bash
python generate_figure2.py \
    --input performance_metrics.csv \
    --output_dir figures/
```

**Panels Generated**:
- **A**: F1-score vs Coverage depth
- **B**: F1-score vs Read identity  
- **C**: F1-score vs Read length
- **D**: Platform comparison (ONT vs PacBio)
- **E**: Sensitivity comparison across tools
- **F**: Precision comparison across tools
- **G**: Runtime comparison
- **H**: Memory usage comparison

#### Supplementary Figure (Figure S2)

```bash
python generate_figureS2.py \
    --input performance_metrics.csv \
    --output_dir figures/
```

**Panels Generated**:
- Heatmap of F1-scores (Tools × Datasets)
- False discovery rate analysis
- Detection rate by fusion type
- Junction read support distribution
- Runtime scaling
- Memory scaling

#### Supplementary Table (Table S1)

```bash
python generate_tableS1.py \
    --input performance_metrics.csv \
    --output tableS1_performance_summary.csv
```

---

## Tool Comparison

### Performance Summary

Based on 40 simulated datasets:

| Tool | Median F1 | Median Sensitivity | Median Precision | Speed | Memory |
|------|-----------|-------------------|------------------|-------|--------|
| CTAT-LR-Fusion | 0.92 | 0.93 | 0.91 | Medium | High |
| JAFFAL | 0.90 | 0.91 | 0.89 | Fast | Medium |
| LongGF | 0.85 | 0.88 | 0.82 | Very Fast | Low |
| FusionSeeker | 0.88 | 0.84 | 0.93 | Medium | Medium |
| FLAIR-fusion | 0.89 | 0.90 | 0.88 | Slow | High |
| pbfusion | 0.87 | 0.85 | 0.90 | Fast | Low |
| IFDlong | 0.89 | 0.89 | 0.89 | Medium | Medium |
| genion | 0.88 | 0.87 | 0.89 | Medium | Medium |
| FUGAREC | 0.86 | 0.88 | 0.84 | Slow | High |

### Recommended Use Cases

**High Sensitivity Required** (discovery mode):
- CTAT-LR-Fusion
- LongGF

**High Precision Required** (clinical validation):
- FusionSeeker
- pbfusion (for PacBio HiFi)

**Balanced Performance**:
- JAFFAL
- IFDlong
- genion

**PacBio HiFi Data**:
- pbfusion
- CTAT-LR-Fusion
- JAFFAL

**Oxford Nanopore Data**:
- CTAT-LR-Fusion
- JAFFAL
- IFDlong

**Low Coverage Data**:
- CTAT-LR-Fusion
- JAFFAL

**High Coverage Data**:
- LongGF (very fast)
- Any tool performs well

---

## Troubleshooting

### Common Issues

#### Docker Build Fails

```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
cd dockerfiles/TOOL_docker
docker build --no-cache -t LongReadsFusionBenchmarking/tool:latest .
```

#### Out of Memory

```bash
# Increase Docker memory limit
docker run --memory=64g --memory-swap=64g ...

# Or edit Docker Desktop settings
# Preferences → Resources → Memory → Increase to 64GB
```

#### Permission Denied

```bash
# Run with current user permissions
docker run --user $(id -u):$(id -g) ...
```

#### Tool Produces No Output

Check:
1. Input file format (FASTQ, not FASTA)
2. Reference genome compatibility
3. Log files for errors
4. Sufficient disk space

```bash
# Check logs
cat output_dir/logs/*.log
```

#### Python Script Errors

```bash
# Reinstall dependencies
pip install --upgrade pandas numpy matplotlib seaborn scipy upsetplot

# Check Python version
python --version  # Should be 3.7+
```

### Getting Help

1. **Check documentation**: [docs/](docs/)
2. **Search issues**: https://github.com/GenomicMedicine/LongReadsFusionBenchmarking/issues
3. **Open new issue**: Provide error logs and system info
4. **Email**: [YOUR_EMAIL]

---

## Citation

If you use this benchmark, please cite:

```
[Your Paper Citation Here]
```

And cite the tools you use:

- **CTAT-LR-Fusion**: Haas BJ et al. (2019)
- **JAFFAL**: Davidson NM et al. (2022)
- **LongGF**: [Citation]
- **FusionSeeker**: Akers NK et al. (2018)
- **FLAIR-fusion**: Tang AD et al. (2020)
- **pbfusion**: Wenger AM et al. (2019)
- **IFDlong**: [Citation]
- **genion**: Umeda T et al. (2021)
- **FUGAREC**: [Citation]

Also cite:
- **Badread**: Wick RR (2019)
- **FusionSimulatorToolkit**: https://github.com/FusionSimulatorToolkit/FusionSimulatorToolkit

---

**Last Updated**: January 2026  
**Repository**: https://github.com/GenomicMedicine/LongReadsFusionBenchmarking  
**License**: MIT (see LICENSE file)
