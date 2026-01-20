# Long-read RNA-Seq Fusion Detection Benchmark

A comprehensive benchmark study of fusion detection tools for long-read RNA sequencing data (Oxford Nanopore and PacBio platforms).

## Overview

This repository contains Docker containers, analysis scripts, and links to datasets used for benchmarking 8 fusion detection tools designed for long-read RNA-seq data:

- **CTAT-LR-Fusion** - Comprehensive fusion detection for long reads
- **JAFFAL** - Joint Approach for Fusion gene Finding using Long-read Analysis
- **LongGF** - Long-read Gene Fusion detection
- **FusionSeeker** - Fusion detection with advanced filtering
- **FLAIR-fusion** - Fusion detection from FLAIR isoform analysis
- **pbfusion** - PacBio-optimized fusion caller
- **IFDlong** - Integrated Fusion Detection for long reads
- **genion** - Gene fusion detection tool

## Features

- 🐳 **Docker Containers**: Pre-configured environments for all 9 tools
- 📊 **Analysis Scripts**: Python scripts for performance evaluation and figure generation
- 📁 **Benchmark Datasets**: Links to simulated and real RNA-seq datasets
- 📈 **Results**: Pre-computed results from all tools on benchmark datasets

## Quick Start

### Prerequisites

- Docker (version 20.10 or higher)
- Python 3.7+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/GenomicMedicine/LongReadsFusionBenchmarking.git
cd LongReadsFusionBenchmarking

# Pull or build Docker images
cd dockerfiles/CTAT-LR-Fusion_docker
docker build -t ctat-lr-fusion:latest .
```

### Running a Tool

Example with CTAT-LR-Fusion:

```bash
cd dockerfiles/CTAT-LR-Fusion_docker
bash run_CTAT-LR-Fusion.sh \
    /path/to/input.fastq \
    /path/to/genome_lib \
    /path/to/output_dir
```

See individual tool documentation in `dockerfiles/` for specific usage.

## Repository Structure

```
.
├── dockerfiles/              # Docker containers for all 8 tools
│   ├── CTAT-LR-Fusion_docker/
│   ├── JAFFAL_docker/
│   ├── LongGF_docker/
│   ├── FusionSeeker_docker/
│   ├── FLAIR-fusion_docker/
│   ├── pbfusion_docker/
│   ├── IFDlong_docker/
│   └── genion_docker/
├── analysis_scripts/         # Python scripts for analysis
│   ├── collect_benchmark.py
│   ├── calculate_performance.py
│   ├── generate_figure2.py
│   ├── generate_figureS2.py
│   └── generate_tableS1.py
├── docs/                     # Documentation
│   ├── TOOLS.md
│   ├── DATASETS.md
│   └── ANALYSIS.md
├── data_links/               # Links to datasets and results
│   ├── SIMULATED_DATA.md
│   └── REAL_DATA.md
├── GFD_main.sh              # Main pipeline script
└── makefusion.sh            # Fusion simulation script
```

## Datasets

### Simulated Data

We generated 40 simulated datasets using **Badread** with varying parameters:

- **Platforms**: Oxford Nanopore (2018, 2020, 2023 chemistries), PacBio RS II (2016), PacBio HiFi (2021)
- **Coverage**: 1×, 5×, 10×, 50×, 100×
- **Read Identity**: 80%, 85%, 90%, 95%, 99.8%
- **Read Length**: 300bp, 1kb, 5kb, 15kb, 50kb

All datasets contain 500 simulated fusion transcripts generated using FusionSimulatorToolkit.

**Download**: See [data_links/SIMULATED_DATA.md](data_links/SIMULATED_DATA.md)

### Real Data

We analyzed real long-read RNA-seq datasets from:

- **Cell Lines**: A549, AML, H9, HCC827, Hct116, HepG2, HEYA8, K562, MCF7, NA12878, NCI-H1975, SKBR3, UHR
- **Platforms**: Oxford Nanopore, PacBio (Sequel IIe, Sequel II)
- **Single-cell RNA-seq**: CC, H838, HCC, LBT samples

**Download**: See [data_links/REAL_DATA.md](data_links/REAL_DATA.md)

## Analysis Scripts

### Simulated Data Analysis

```bash
cd analysis_scripts

# 1. Collect benchmark results
python collect_benchmark.py \
    --simulated_dir /path/to/simulated_data \
    --output benchmark_results.csv

# 2. Calculate performance metrics
python calculate_performance.py \
    --input benchmark_results.csv \
    --truth fusion_truth.txt \
    --output performance_metrics.csv

# 3. Generate figures
python generate_figure2.py --input performance_metrics.csv
python generate_figureS2.py --input performance_metrics.csv
python generate_tableS1.py --input performance_metrics.csv
```

### Real Data Analysis

```bash
# Generate comparison plots
python 02_upset_plot.py --input real_data_results/
python 03_method_consensus_plot.py --input real_data_results/
python 06_ppv_tpr_plot.py --input real_data_results/
python generate_figures_final.py --input real_data_results/
```

## Docker Containers

Each tool has a dedicated Docker container with all dependencies pre-installed.
Available at https://hub.docker.com/repository/docker/mark614/long-read_rna-seq_fusion_detection_benchmark/general

### Building Containers

```bash
# Build all containers
for tool in dockerfiles/*/; do
    cd "$tool"
    tool_name=$(basename "$tool" | sed 's/_docker//')
    docker build -t "LongReadsFusionBenchmarking/${tool_name}:latest" .
    cd -
done
```

### Running Containers

All tools follow a similar interface:

```bash
bash dockerfiles/<TOOL>_docker/run_<TOOL>.sh \
    <input_fastq> \
    <genome_lib> \
    <output_dir>
```

See tool-specific README files in each Docker directory for detailed usage.

## Citation

## Tool Citations

Please also cite the original tools:

- **CTAT-LR-Fusion**: Haas et al. (2019)
- **JAFFAL**: Davidson et al. (2022)
- **LongGF**: Haas et al. (2018)
- **FusionSeeker**: Akers et al. (2018)
- **FLAIR-fusion**: Tang et al. (2020)
- **pbfusion**: Wenger et al. (2019)
- **IFDlong**: Liu et al. (2020)
- **genion**: Umeda et al. (2021)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please:
- Open an issue on GitHub

## Acknowledgments

- **FusionSimulatorToolkit** for fusion transcript simulation
- **Badread** for long-read sequencing simulation
- All tool developers for their excellent software

---

**Repository**: https://github.com/GenomicMedicine/LongReadsFusionBenchmarking  
**Data Repository**: The Zenodo link will be updated soon.
**Last Updated**: January 2026

