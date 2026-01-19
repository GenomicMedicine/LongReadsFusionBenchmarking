# Analysis Scripts

Python scripts for benchmarking fusion detection tools and generating publication figures.

## Scripts Overview

### Simulated Data Analysis

| Script | Purpose | Output |
|--------|---------|--------|
| `collect_benchmark.py` | Collect tool results | CSV of all predictions |
| `calculate_performance.py` | Calculate metrics | Performance statistics |
| `generate_figure2.py` | Main figure panels | Figure 2 (A-H) |
| `generate_figureS2.py` | Supplementary figures | Figure S2 |
| `generate_tableS1.py` | Performance table | Table S1 |

### Real Data Analysis

| Script | Purpose | Output |
|--------|---------|--------|
| `02_upset_plot.py` | Tool overlap | UpSet plot |
| `03_method_consensus_plot.py` | Consensus analysis | Consensus plot |
| `06_ppv_tpr_plot.py` | PPV vs TPR curves | PPV-TPR plot |
| `generate_all_figures.py` | Run all analyses | All figures |
| `generate_figures_final.py` | Publication figures | Combined figures |
| `generate_heatmap_figure.py` | Detection heatmap | Heatmap |
| `generate_all_plots_corrected.py` | Corrected plots | Various plots |

## Installation

```bash
# Install required packages
pip install pandas numpy matplotlib seaborn scipy upsetplot
```

## Quick Start

### Analyze Simulated Data

```bash
# 1. Collect results from all tools
python collect_benchmark.py \
    --simulated_dir /path/to/simulated_data \
    --output benchmark_results.csv

# 2. Calculate performance metrics
python calculate_performance.py \
    --input benchmark_results.csv \
    --truth fusion_truth.txt \
    --output performance_metrics.csv

# 3. Generate figures
python generate_figure2.py --input performance_metrics.csv --output_dir figures/
```

### Analyze Real Data

```bash
# Generate all real data figures
python generate_all_figures.py \
    --real_data /path/to/real_data \
    --output real_results/
```

## Detailed Usage

See [../docs/ANALYSIS.md](../docs/ANALYSIS.md) for comprehensive documentation.

## Output Examples

### Figure 2 Panels
- **A**: F1-score vs Coverage depth
- **B**: F1-score vs Read identity
- **C**: F1-score vs Read length
- **D**: Platform comparison
- **E**: Sensitivity comparison
- **F**: Precision comparison
- **G**: Runtime analysis
- **H**: Memory usage

### Supplementary Figure S2
- Detailed performance heatmaps
- False discovery rate analysis
- Junction read support distributions

### Tables
- **Table S1**: Complete performance metrics for all tool-dataset combinations

## Citation

```
[Your Paper Citation]
```

---

For detailed documentation, see [../docs/ANALYSIS.md](../docs/ANALYSIS.md)
