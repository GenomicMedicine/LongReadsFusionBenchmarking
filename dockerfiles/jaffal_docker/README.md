# JAFFAL Docker Container

JAFFAL (Joint Approach for Fusion Finding using Long-read Analysis) is a hybrid fusion detection tool.

## Reference Files

**Important**: The reference files directory `JAFFAL_reference_files_hg38_genCode44/` is not included in this repository due to large file sizes (~9.4 GB).

### Download Reference Files

You need to download or build the reference files separately:

**Option 1: Download pre-built files** (Recommended)

```bash
# Download from [INSERT DOWNLOAD LINK]
# Or build using JAFFAL tools
```

**Option 2: Build reference files**

```bash
# Install JAFFAL
git clone https://github.com/Oshlack/JAFFAL.git

# Download genome and annotation
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.primary_assembly.genome.fa.gz
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.primary_assembly.annotation.gtf.gz

# Build reference files following JAFFAL documentation
# https://github.com/Oshlack/JAFFAL
```

### Expected Directory Structure

```
JAFFAL_reference_files_hg38_genCode44/
├── hg38.fa                      # Reference genome (~3.1 GB)
├── hg38_genCode44.fa            # Transcriptome sequences
├── hg38_genCode44.*.bt2         # Bowtie2 indices
├── Masked_hg38.*.bt2            # Masked genome indices
├── hg38_genCode44_blast.*       # BLAST database files
├── hg38_genCode44.bed           # Gene annotations
└── hg38_genCode44.tab           # Gene table
```

## Building Docker Image

```bash
# Make sure reference files are in place
cd dockerfiles/jaffal_docker
docker build -t jaffal:latest .
```

## Running JAFFAL

```bash
bash run_JAFFAL.sh \
    /path/to/input.fastq \
    /path/to/JAFFAL_reference_files_hg38_genCode44 \
    /path/to/output
```

## Citation

Davidson NM, et al. (2022) JAFFAL: detecting fusion genes with long-read transcriptome sequencing. Genome Biology.
