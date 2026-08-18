# LongFuse: An Ensemble Method for Long-read RNA-Seq Fusion Detection

**LongFuse** is an ensemble method for detecting gene fusions from long-read RNA sequencing data (Oxford Nanopore and PacBio). Based on a comprehensive benchmark of 8 fusion detection tools, LongFuse integrates outputs from multiple callers (k2, k3, k5 configurations) to improve overall detection performance.

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/GenomicMedicine/LongReadsFusionBenchmarking.git
cd LongReadsFusionBenchmarking
```

### 2. Running LongFuse

LongFuse can be run in two main modes via a unified Python pipeline (`longFuse/longfuse_k235_pipeline.py`):

**Mode A: Kickstart (Fastest)**
If you already have caller result files from other tools, use `kickstart` to bypass caller execution:
```bash
python longFuse/longfuse_k235_pipeline.py kickstart \
    --method-results-root /path/to/method_results \
    --output-dir /path/to/output/longfuse_results \
    --execution parallel \
    --workers 3
```

**Mode B: Denovo**
Run the upstream callers from raw sequences and then automatically integrate their results:
```bash
python longFuse/longfuse_k235_pipeline.py denovo \
    --config config.yaml \
    --reads /path/to/sample.fastq \
    --seq-type ONT_cDNA \
    --runner-script /path/to/GFD_main.sh \
    --output-dir /path/to/output/longfuse_results \
    --execution parallel \
    --workers 3
```

For more details on customizing callers and using specific parameters, see the [LongFuse Pipeline Documentation](longFuse/README.md).

---

## Documentation

- **[Reference Build Guide](reference_build/README.md)**: Standardized scripts and instructions for building necessary genomes, GTF files, and tool-specific indices for all benchmarked callers.
- **[LongFuse Pipeline & Customization Guide](longFuse/README.md)**: Explore advanced configurations, customized subsets of callers, mode details, and outputs format.
- **[Docker Containers](dockerfiles/README.md)**: Find Docker environments for 9 integration tools, including `longfuse-k235-pipeline_docker`.
- **[Benchmark Datasets (Simulated)](data_links/SIMULATED_DATA.md)** & **[(Real Data)](data_links/REAL_DATA.md)**: Access 40 simulated long-read datasets and various real datasets used for evaluation.
- **[Individual Tool Usage](docs/TOOLS.md)**: Links and tips for running the 8 benchmarked tools individually.

---

## Docker Environments

Pre-configured Docker environments are provided for running LongFuse alongside the 8 sub-tools:
- **Available on DockerHub**: `mark614/long-read_rna-seq_fusion_detection_benchmark:*`

Run LongFuse Kickstart directly with Docker:
```bash
bash dockerfiles/longfuse-k235-pipeline_docker/run_longfuse_k235_pipeline.sh kickstart \
    --method-results-root /path/to/method_results \
    --output-dir /path/to/output/longfuse_results
```

---

## Citations and Benchmark

This repository also contains the framework and data to reproduce our benchmarking study across 8 fusion caller tools (CTAT-LR-Fusion, JAFFAL, LongGF, FusionSeeker, FLAIR-fusion, pbfusion, IFDlong, genion). Please refer to our [Analysis Guide](docs/ANALYSIS.md) and tool-specific citations in [TOOLS.md](docs/TOOLS.md).

**Repository**: https://github.com/GenomicMedicine/LongReadsFusionBenchmarking  
**Data Links**: https://pan.quark.cn/s/ab9b97e62598

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Tool Citations

Please also cite the original tools if you use their results:

- **CTAT-LR-Fusion**: Qin, Q., et al., "CTAT-LR-fusion: accurate fusion transcript identification from long and short read isoform sequencing at bulk or single cell resolution," bioRxiv, 2024. [doi: 10.1101/2024.02.05.578964]
- **JAFFAL**: Davidson, N. M., et al., "JAFFAL: detecting fusion genes with long-read transcriptome sequencing," Genome biology, vol. 23, no. 1, pp. 1-20, 2022. [doi: 10.1186/s13059-022-02610-1]
- **LongGF**: Liu, Q., et al., "LongGF: computational algorithm and software tool for fast and accurate detection of gene fusions by long-read transcriptome sequencing," BMC Genomics, vol. 21, no. 11, p. 793, 2020. [doi: 10.1186/s12864-020-07207-4]
- **FusionSeeker**: Chen, Y., et al., "Gene Fusion Detection and Characterization in Long-Read Cancer Transcriptome Sequencing Data with FusionSeeker," Cancer Research, vol. 83, no. 1, pp. 28-33, 2023. [doi: 10.1158/0008-5472.Can-22-1628]
- **FLAIR-fusion**: Felton, C., et al., "Detection of alternative isoforms of gene fusions from long-read RNA-seq with FLAIR-fusion," bioRxiv, 2023. [doi: 10.1101/2022.08.01.502364]
- **pbfusion**: Volden, R., et al., "Abstract LB078: pbfusion: Detecting gene-fusion and other transcriptional abnormalities using PacBio HiFi data," Cancer Research, vol. 83, no. 8_Supplement, pp. LB078-LB078, 2023. [doi: 10.1158/1538-7445.Am2023-lb078]
- **IFDlong**: Wang, W., et al., "IFDlong: an isoform and fusion detector for accurate annotation and quantification of long-read RNA-seq data," bioRxiv, 2024.
- **genion**: Karaoglanoglu, F., et al., "Genion, an accurate tool to detect gene fusion from long transcriptomics reads," BMC Genomics, vol. 23, no. 1, p. 129, 2022. [doi: 10.1186/s12864-022-08339-5]

