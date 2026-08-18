# Analysis Scripts Documentation

## Overview

This directory contains Python scripts for benchmarking fusion detection tools on simulated and real datasets. The scripts generate performance metrics, statistical analyses, and publication-quality figures.

## Requirements

```bash
# Install dependencies
pip install pandas numpy matplotlib seaborn scipy upsetplot
```

**Python Version**: 3.7 or higher

## Simulated Data Analysis Scripts

### 1. collect_benchmark.py

**Purpose**: Collect and standardize fusion predictions from all tools across multiple simulated datasets.

**Usage**:
```bash
python collect_benchmark.py \
    --simulated_dir /path/to/simulated_data \
    --tools CTAT-LR-Fusion,JAFFAL,LongGF,FusionSeeker,FLAIR-fusion,pbfusion,IFDlong,genion,FUGAREC \
    --output benchmark_results.csv
```

**Parameters**:
- `--simulated_dir`: Directory containing simulated datasets
- `--tools`: Comma-separated list of tools to analyze
- `--output`: Output CSV file with collected results

**Output Format**:
```
Dataset,Tool,GeneA,GeneB,BreakpointA,BreakpointB,JunctionReads,SpanningReads
nanopore2023_10x_0.95_15000,CTAT-LR-Fusion,EML4,ALK,chr2:29446394,chr2:30142858,45,23
```

---

### 2. calculate_performance.py

**Purpose**: Calculate sensitivity, precision, F1-score, and other performance metrics by comparing predictions to ground truth.

**Usage**:
```bash
python calculate_performance.py \
    --input benchmark_results.csv \
    --truth /path/to/fusion_truth.txt \
    --output performance_metrics.csv
```

**Parameters**:
- `--input`: Collected benchmark results from step 1
- `--truth`: Ground truth fusion file
- `--output`: Output metrics file

**Metrics Calculated**:
- **Sensitivity (Recall)**: TP / (TP + FN)
- **Precision (PPV)**: TP / (TP + FP)
- **F1-Score**: 2 × (Precision × Recall) / (Precision + Recall)
- **False Discovery Rate**: FP / (TP + FP)
- **Matthews Correlation Coefficient (MCC)**

**Output Format**:
```
Dataset,Tool,TP,FP,FN,Sensitivity,Precision,F1,MCC
nanopore2023_10x_0.95_15000,CTAT-LR-Fusion,485,12,15,0.970,0.976,0.973,0.971
```

---

### 3. generate_figure2.py

**Purpose**: Generate Figure 2 (A-H) showing performance across different parameters.

**Usage**:
```bash
python generate_figure2.py \
    --input performance_metrics.csv \
    --output_dir figures/
```

**Generated Panels**:
- **Panel A**: F1-score vs Coverage (1×, 5×, 10×, 50×, 100×)
- **Panel B**: F1-score vs Read Identity (80%, 85%, 90%, 95%, 99.8%)
- **Panel C**: F1-score vs Read Length (300bp, 1kb, 5kb, 15kb, 50kb)
- **Panel D**: F1-score vs Platform (ONT 2018/2020/2023, PacBio 2016/2021)
- **Panel E**: Sensitivity comparison across all tools
- **Panel F**: Precision comparison across all tools
- **Panel G**: Runtime comparison
- **Panel H**: Memory usage comparison

**Output Files**:
```
figures/
├── figure2_panel_A.pdf
├── figure2_panel_B.pdf
├── figure2_panel_C.pdf
├── figure2_panel_D.pdf
├── figure2_panel_E.pdf
├── figure2_panel_F.pdf
├── figure2_panel_G.pdf
└── figure2_panel_H.pdf
```

---

### 4. generate_figureS2.py

**Purpose**: Generate Supplementary Figure S2 with detailed breakdowns.

**Usage**:
```bash
python generate_figureS2.py \
    --input performance_metrics.csv \
    --output_dir figures/
```

**Generated Panels**:
- **Panel A**: Heatmap of F1-scores (Tools × Datasets)
- **Panel B**: False discovery rate across parameters
- **Panel C**: Detection rate by fusion type
- **Panel D**: Junction read support distribution
- **Panel E**: Runtime scaling with coverage
- **Panel F**: Memory scaling with read length

---

### 5. generate_tableS1.py

**Purpose**: Generate Supplementary Table S1 with detailed performance metrics.

**Usage**:
```bash
python generate_tableS1.py \
    --input performance_metrics.csv \
    --output tableS1_performance_summary.csv
```

**Output**: Comprehensive table with all metrics for all tool-dataset combinations.

---

## Real Data Analysis Scripts

### 02_upset_plot.py

**Purpose**: Generate UpSet plot showing fusion detection overlap between tools.

**Usage**:
```bash
python 02_upset_plot.py \
    --input /path/to/real_data_results/ \
    --cell_line HCC827 \
    --output upset_plot.pdf
```

**Description**: Creates an UpSet plot showing which fusions are detected by single tools, pairs of tools, or multiple tools, providing insight into consensus and tool-specific findings.

---

### 03_method_consensus_plot.py

**Purpose**: Visualize method consensus for fusion calls.

**Usage**:
```bash
python 03_method_consensus_plot.py \
    --input /path/to/real_data_results/ \
    --cell_line HCC827 \
    --output consensus_plot.pdf
```

**Description**: Shows how many tools support each fusion call, stratified by fusion type or gene family.

---

### 06_ppv_tpr_plot.py

**Purpose**: Generate Positive Predictive Value (PPV) vs True Positive Rate (TPR) plots.

**Usage**:
```bash
python 06_ppv_tpr_plot.py \
    --input /path/to/real_data_results/ \
    --known_fusions known_fusions.txt \
    --output ppv_tpr_plot.pdf
```

**Description**: For cell lines with known fusions, plot PPV vs TPR curves for each tool.

---

### generate_all_figures.py

**Purpose**: Run all real data analyses in one command.

**Usage**:
```bash
python generate_all_figures.py \
    --real_data /path/to/real_data/ \
    --output results/
```

**Description**: Generates all plots and tables for real data analysis.

---

### generate_figures_final.py

**Purpose**: Generate publication-ready figures combining simulated and real data.

**Usage**:
```bash
python generate_figures_final.py \
    --simulated_metrics performance_metrics.csv \
    --real_data /path/to/real_data/ \
    --output publication_figures/
```

**Description**: Creates combined figures showing:
- Simulated data performance
- Real data validation
- Cross-platform comparisons
- Known fusion detection rates

---

### generate_heatmap_figure.py

**Purpose**: Generate heatmaps of tool performance across cell lines.

**Usage**:
```bash
python generate_heatmap_figure.py \
    --input /path/to/real_data_results/ \
    --output heatmap.pdf
```

**Description**: Creates heatmap showing number of fusions detected by each tool in each cell line.

---

## Common Workflows

### Complete Simulated Data Analysis

```bash
# 1. Collect results
python collect_benchmark.py \
    --simulated_dir ../simulated_data \
    --tools CTAT-LR-Fusion,JAFFAL,LongGF,FusionSeeker,FLAIR-fusion,pbfusion,IFDlong,genion,FUGAREC \
    --output benchmark_results.csv

# 2. Calculate metrics
python calculate_performance.py \
    --input benchmark_results.csv \
    --truth ../simulated_data/fusion_truth.txt \
    --output performance_metrics.csv

# 3. Generate figures
python generate_figure2.py --input performance_metrics.csv --output_dir figures/
python generate_figureS2.py --input performance_metrics.csv --output_dir figures/

# 4. Generate tables
python generate_tableS1.py --input performance_metrics.csv --output tableS1.csv
```

### Complete Real Data Analysis

```bash
# Run all real data analyses
python generate_all_figures.py \
    --real_data ../real_data \
    --output real_data_results/

# Generate individual plots
python 02_upset_plot.py --input ../real_data/HCC827/ONT --output upset_HCC827.pdf
python 03_method_consensus_plot.py --input ../real_data/HCC827/ONT --output consensus_HCC827.pdf
python generate_heatmap_figure.py --input ../real_data --output heatmap_all.pdf
```

### Combined Analysis

```bash
# Generate publication figures combining both datasets
python generate_figures_final.py \
    --simulated_metrics performance_metrics.csv \
    --real_data ../real_data \
    --output publication_figures/
```

## Input File Formats

### Ground Truth Format (fusion_truth.txt)
```
GeneA--GeneB    TranscriptA--TranscriptB    BreakpointInfo
EML4--ALK       ENST00000393183--ENST00000389048    chr2:29446394-chr2:30142858[+]
```

### Known Fusions Format (known_fusions.txt)
```
GeneA--GeneB    Evidence    Source
BCR--ABL1       Validated   Literature
EML4--ALK       Validated   Clinical
```

### Tool Output Format
Tools should produce TSV files with columns:
- GeneA, GeneB
- BreakpointA, BreakpointB (optional)
- JunctionReads, SpanningReads (optional)

## Customization

### Modifying Figure Styles

Edit the matplotlib style settings in each script:

```python
import matplotlib.pyplot as plt
plt.style.use('seaborn-paper')  # Change to your preferred style
```

### Adding New Metrics

In `calculate_performance.py`, add custom metrics:

```python
def calculate_custom_metric(tp, fp, fn):
    # Your metric calculation
    return custom_score
```

### Filtering Results

Add filtering criteria in `collect_benchmark.py`:

```python
# Filter by minimum junction read support
df = df[df['JunctionReads'] >= min_reads]
```

## Troubleshooting

**Issue**: Missing dependencies
```bash
pip install --upgrade pandas numpy matplotlib seaborn scipy upsetplot
```

**Issue**: File not found errors
- Check that paths are absolute or relative to script location
- Verify dataset directory structure matches expected format

**Issue**: Memory errors with large datasets
- Process datasets in batches
- Increase system memory
- Use pandas chunking for large files

## Performance Tips

1. **Parallel Processing**: Use `--jobs N` parameter where available
2. **Caching**: Results are cached in `cache/` directory by default
3. **Incremental Analysis**: Scripts skip already-processed datasets

## Output File Naming

Scripts use consistent naming:
- `benchmark_results.csv` - Collected tool predictions
- `performance_metrics.csv` - Calculated metrics
- `figure2_panel_X.pdf` - Main figure panels
- `figureS2_panel_X.pdf` - Supplementary figure panels
- `tableS1_*.csv` - Supplementary tables


## Contact

For questions or issues:
- GitHub Issues: https://github.com/GenomicMedicine/LongReadsFusionBenchmarking/issues

---

**Last Updated**: January 2026
