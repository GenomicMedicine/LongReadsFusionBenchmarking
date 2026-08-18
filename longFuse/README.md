# LongFuse Universal Pipeline

## Overview

LongFuse now provides two modes:

1. **denovo mode**: start from raw reads, run callers, then integrate by LongFuse k2/k3/k5.
2. **kickstart mode**: skip caller execution, directly ingest existing caller result files and integrate.

This design separates upstream calling from downstream integration while keeping one unified entrypoint.

## Recommended default (paper benchmark)

For **real-data** precision/recall analyses in our benchmark paper (28 consensus samples, 8 callers), the recommended default is:

**Consensus threshold K = 4**

- A fusion is treated as a consensus positive when **≥ 4 of 8** benchmark callers support it.
- This matches the default in `assembly_pipe/paper_fig/plot_r3_precision_recall_box_with_longfuse.py` (`--consensus-k 4`).
- LongFuse predictions are evaluated against these K=4 consensus positives on real data.

For **LongFuse integration** via this pipeline (`kickstart` / `denovo`), built-in ensemble sizes are **k2, k3, k5** (see [Built-in k configurations](#built-in-k-configurations) below). Sim+real parameter tuning in our benchmark favors **LongFuse_k3** for balanced sim F1 and real hit rate; use the `k3/` output folder unless your analysis specifies otherwise.

**Summary**

| Parameter | Recommended default | Meaning |
|-----------|---------------------|---------|
| Real-data consensus **K** | **4** | ≥4/8 callers agree → consensus positive (paper figures) |
| LongFuse integration **k** | **3** (among k2/k3/k5) | 3-method ensemble: FLAIR-fusion + JAFFAL + LongGF |

## Installation & Prerequisites

The installation requirements depend on which mode you plan to use: `kickstart` or `denovo`.

### For `kickstart` Mode (Basic Integration)
When using `kickstart`, you only need the basic Python dependencies to integrate existing caller results. No heavy caller dependencies or Docker are required.
- **Python**: 3.7+
- **Packages**: `pandas`, `pyyaml`

```bash
# Clone the repository
git clone https://github.com/GenomicMedicine/LongReadsFusionBenchmarking.git
cd LongReadsFusionBenchmarking

# Install basic wrapper requirements
pip install pandas pyyaml
```

### For `denovo` Mode (Full Execution via Docker)
When using `denovo`, LongFuse will orchestrate and execute the actual fusion callers. To ensure reproducible and clean environments for all 8 callers, **this mode heavily relies on Docker** and requires you to construct the proper **Reference Databases**.

- **Docker**: version 20.10 or higher.
- **Reference Genomes & Indices**: Please refer to the **[Reference Build Guide](../reference_build/README.md)** to download and build the exact reference files required by your selected callers.

To use `denovo` mode, you must first pull or build the pre-configured Docker images for the callers you intend to run. 

```bash
# Example: Pull the LongFuse pipeline environment and caller images
docker pull mark614/long-read_rna-seq_fusion_detection_benchmark:longfuse_pipeline

# Refer to dockerfiles/README.md to pull or build the specific 
# caller images (e.g., JAFFAL, LongGF, CTAT-LR-Fusion) before running denovo.
```

## Using Configuration Files (Recommended)

Instead of passing many CLI arguments (which can become complex when dealing with multiple callers), LongFuse supports setting all parameters via a unified `config.yaml` using the `--config` parameter.

Example `config.yaml`:
```yaml
# General Configurations
output_dir: /path/to/output/longfuse_results
execution: parallel
workers: 3

# Denovo Specific Configurations
reads: /path/to/sample.fastq
seq_type: ONT_cDNA
runner_script: /path/to/GFD_main.sh

# Caller Customization
callers:
  - JAFFAL
  - LongGF
  - CTAT-LR-Fusion
```

You can then run the pipeline as:
```bash
python longFuse/longfuse_k235_pipeline.py denovo --config config.yaml
```

## Mode 1: denovo

### Purpose

Use this mode when you want LongFuse to orchestrate caller execution first (via a runner script targeting Docker containers), then auto-detect caller outputs and integrate. By default, temporary caller results are saved in a `caller_workspace` folder inside your `output-dir`.

### Example (CLI approach)

```bash
python longFuse/longfuse_k235_pipeline.py denovo \
  --reads /path/to/sample.fastq \
  --seq-type ONT_cDNA \
  --runner-script /path/to/GFD_main.sh \
  --output-dir /path/to/output/longfuse_denovo \
  --execution parallel \
  --workers 3 
```

### Key Inputs

- `--reads`: input reads file for caller stage.
- `--output-dir`: Main output directory where `caller_workspace` will be created and where final integration outputs go.
- `--seq-type`: sequencing type passed to runner.
- `--runner-script`: caller orchestration script (default `GFD_main.sh`).
- `--config`: (Optional) YAML/JSON file containing parameter specifications.

## Mode 2: kickstart

### Purpose

Use this mode when caller results are already available (e.g. from previously executed caller tools) and you want to run **only** the integration steps.

### Example

```bash
python longFuse/longfuse_k235_pipeline.py kickstart \
  --method-results-root /path/to/method_results \
  --output-dir /path/to/output/longfuse_kickstart \
  --cohort real \
  --execution parallel \
  --workers 3
```

### Optional explicit file mapping

If you want to explicitly map scattered outputs rather than letting the directory scanner automatically discover them:

```bash
python longFuse/longfuse_k235_pipeline.py kickstart \
  --method-file JAFFAL=/path/to/jaffal_result.tsv \
  --method-file LongGF=/path/to/longgf_result.csv \
  --output-dir /path/to/output/longfuse_kickstart
```

## Packaging and Docker Workflow 

We highly recommend packing the entire sequence as a Docker execution. The inner callers will interact cleanly without local dependency conflicts. 

Run LongFuse natively in its Docker image using a foolproof step-by-step workflow:

**Step 1: Create your configuration file**  
Create a file named `my_longfuse_config.yaml` in your project folder. You can use the following command, making sure to replace the paths (`/path/to/...`) with the actual absolute paths on your system:

```bash
cat << 'YAML' > my_longfuse_config.yaml
# Main output directory (ensure you have write permissions)
output_dir: /full/absolute/path/to/output_folder

# Execution settings
execution: parallel
workers: 3

# Sequencing parameters
reads: /full/absolute/path/to/your_sample_reads.fastq
seq_type: ONT_cDNA

# Script to orchestrate callers
runner_script: /full/absolute/path/to/LongReadsFusionBenchmarking/GFD_main.sh

# Select which callers to run
callers:
  - JAFFAL
  - LongGF
  - CTAT-LR-Fusion
YAML
```

**Step 2: Execute the pipeline using Docker**  
Run the provided Docker wrapper script and pass your newly created configuration file:

```bash
bash dockerfiles/longfuse-k235-pipeline_docker/run_longfuse_k235_pipeline.sh denovo \
    --config $(pwd)/my_longfuse_config.yaml
```


## Built-in k configurations

- `k2`: `JAFFAL + LongGF`
- `k3`: `FLAIR-fusion + JAFFAL + LongGF`
- `k5`: `CTAT-LR-Fusion + FLAIR-fusion + JAFFAL + LongGF + genion`

If you are using custom configurations/YAML subsets, LongFuse will intelligently integrate only the available caller results. Built-in `k` results require the mandatory subsets of callers to execute successfully.
