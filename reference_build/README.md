# 🧬 Reference Environments for Long-read RNA-seq Fusion Detection

Welcome to the **LongFuse Reference Build Guide**! 

To run the fusion callers benchmarked in LongFuse (especially in `denovo` mode), you must first prepare the necessary genomic references, transcriptome databases, and tool-specific indices. This directory contains reproducible, user-friendly scripts to automatically download and build these dependencies.

---

## 🚀 Unified Building (Recommended)

If you plan to test all 8 callers or use the full LongFuse ensemble, we provide a master script that iteratively builds everything for you.

### ⚠️ Prerequisites & System Requirements
- **Disk Space**: At least **~100 GB** of free storage.
- **Time**: Depending on your internet connection and CPU cores, this can take **several hours**. We recommend running this in a `tmux` or `screen` session.
- **Dependencies**: 
  - `wget`, `gunzip`, `tar` (standard Linux utilities)
  - **Docker** (required for `pbfusion` and `JAFFAL` indexing steps)

### Run the Master Script
Simply execute the unified script from this directory:
```bash
# Ensure you have Docker running and sufficient disk space
bash build_all_references.sh
```
This script will sequentially enter each sub-folder and trigger the respective build process. If any step fails (e.g., due to network issues), you can simply re-run the specific sub-folder script.

---

## 🗂️ Method-specific Builds (Advanced)

If you only want to run a specific subset of tools (e.g., only `k2`: JAFFAL + LongGF), you can save time and disk space by only building what you need. Navigate to the respective directories and run their individual `build_reference.sh` scripts:

*   **`common/`** - **(Required for most tools)** Downloads the base GRCh38 genome (FASTA) and GENCODE v44 GTF/Transcriptome. 
    * *Used directly by: LongGF, FusionSeeker, FLAIR-fusion, IFDlong.*
*   **`CTAT-LR-Fusion/`** - Downloads the massive Broad Institute `plug-n-play` pre-compiled fusion bundle.
*   **`JAFFAL/`** - Initializes the internal JAFFA architecture and reference DBs using its Docker-based installer.
*   **`pbfusion/`** - Uses `pbmm2` and `pbfusion index` (via Docker) to compile the `.mmi` and `.bin` binaries.
*   **`genion/`** - Acquires genomic super-duplications and prepares the required masking/mapping tables.

*(Note: Folders like `LongGF/`, `FusionSeeker/`, `FLAIR-fusion/`, and `IFDlong/` do not have specialized scripts because they strictly depend on the output generated in the `common/` folder.)*

## 🔗 Next Steps
Once your references are built, you are ready to detect fusions! 
Head over to the **[LongFuse Pipeline Guide](../longFuse/README.md)** or the main **[LongFuse README](../README.md)** to start your analysis.
