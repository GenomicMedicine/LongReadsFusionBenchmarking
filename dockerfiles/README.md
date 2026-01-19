# Docker Containers for Fusion Detection Tools

This directory contains Docker containers for 9 long-read fusion detection tools, providing reproducible analysis environments.

## Available Tools

| Tool | Directory | Platform | Build Status |
|------|-----------|----------|--------------|
| CTAT-LR-Fusion | `CTAT-LR-Fusion_docker/` | ONT, PacBio | ✓ |
| JAFFAL | `jaffal_docker/` | ONT, PacBio | ✓ |
| LongGF | `longgf_docker/` | ONT, PacBio | ✓ |
| FusionSeeker | `fusionseeker_docker/` | ONT, PacBio | ✓ |
| FLAIR-fusion | `flair-fusion_docker/` | ONT, PacBio | ✓ |
| pbfusion | `pbfusion_docker/` | PacBio | ✓ |
| IFDlong | `ifdlong_docker/` | ONT, PacBio | ✓ |
| genion | `genion_docker/` | ONT, PacBio | ✓ |
| FUGAREC | `fugarec_docker/` | ONT, PacBio | ✓ |

## Quick Start

### Building All Containers

```bash
# Build all Docker images
for tool_dir in */; do
    cd "$tool_dir"
    tool_name=$(basename "$tool_dir" | sed 's/_docker//')
    echo "Building $tool_name..."
    docker build -t "LongReadsFusionBenchmarking/${tool_name}:latest" .
    cd ..
done
```

### Building Individual Container

```bash
cd CTAT-LR-Fusion_docker
docker build -t LongReadsFusionBenchmarking/ctat-lr-fusion:latest .
```

### Running a Container

Each tool has a wrapper script for easy execution:

```bash
cd CTAT-LR-Fusion_docker
bash run_CTAT-LR-Fusion.sh \
    /path/to/input.fastq \
    /path/to/genome_lib \
    /path/to/output_dir
```

## Container Structure

Each tool directory contains:

```
TOOL_docker/
├── Dockerfile                   # Container definition
├── run_TOOL.sh                  # Wrapper script
├── README.md                    # Tool-specific documentation
└── [tool-specific files]        # Additional resources
```

## Common Usage Pattern

All tools follow a similar interface:

```bash
bash run_<TOOL>.sh \
    <input_fastq> \
    <genome_library> \
    <output_directory> \
    [tool-specific options]
```

**Parameters**:
- `input_fastq`: Path to input FASTQ file (ONT or PacBio reads)
- `genome_library`: Path to reference genome library/index
- `output_directory`: Directory for output files
- `tool-specific options`: Additional tool parameters (optional)

## Reference Data Requirements

Most tools require:

1. **Reference Genome**: GRCh38 primary assembly (FASTA)
2. **Gene Annotation**: GENCODE V44 GTF/GFF3
3. **Tool-Specific Indices**: Pre-built or generated on first run

### Preparing Reference Data

```bash
# Download reference genome
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.primary_assembly.genome.fa.gz
gunzip GRCh38.primary_assembly.genome.fa.gz

# Download annotation
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.primary_assembly.annotation.gtf.gz
gunzip gencode.v44.primary_assembly.annotation.gtf.gz

# Download transcriptome
wget http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.transcripts.fa.gz
gunzip gencode.v44.transcripts.fa.gz
```

See individual tool READMEs for specific index building instructions.

## Resource Requirements

### Minimum Requirements
- **CPU**: 4 cores
- **RAM**: 16 GB
- **Disk**: 100 GB (including reference data)
- **Docker**: Version 20.10 or higher

### Recommended Requirements
- **CPU**: 16+ cores
- **RAM**: 64 GB
- **Disk**: 500 GB
- **SSD**: For improved I/O performance

### Per-Tool Requirements

| Tool | CPU (cores) | RAM (GB) | Disk (GB) | Runtime* |
|------|-------------|----------|-----------|----------|
| CTAT-LR-Fusion | 8-16 | 32-64 | 50 | ~2h |
| JAFFAL | 4-8 | 16-32 | 30 | ~1h |
| LongGF | 4-8 | 8-16 | 20 | ~30min |
| FusionSeeker | 8-16 | 16-32 | 40 | ~1.5h |
| FLAIR-fusion | 8-16 | 32-64 | 60 | ~3h |
| pbfusion | 4-8 | 8-16 | 25 | ~30min |
| IFDlong | 8-16 | 16-32 | 35 | ~1.5h |
| genion | 8-16 | 16-32 | 30 | ~1h |
| FUGAREC | 8-16 | 32-64 | 50 | ~3h |

*Runtime for ~10× coverage, 15kb reads, ~5M reads

## Tool-Specific Notes

### CTAT-LR-Fusion
- Requires CTAT genome library (download separately)
- Supports both ONT and PacBio
- Comprehensive output with detailed evidence

### JAFFAL
- Fast hybrid approach
- Good for routine analysis
- Moderate resource usage

### LongGF
- Fastest tool
- Best for high-coverage data
- Minimal dependencies

### FusionSeeker
- High-precision filtering
- Configurable parameters
- Good for clinical applications

### FLAIR-fusion
- Full-length isoform analysis
- Provides quantification
- Requires more memory and time

### pbfusion
- Optimized for PacBio HiFi
- Simple workflow
- Fast execution

### IFDlong
- Multi-level filtering
- Machine learning components
- Balanced performance

### genion
- Random forest classifier
- Confidence scoring
- Pre-trained model included

### FUGAREC
- Reconstructs fusion transcripts
- BLAT-based gap filling
- Detailed junction sequences

## Batch Processing

Process multiple samples:

```bash
#!/bin/bash
for sample in samples/*.fastq; do
    sample_name=$(basename "$sample" .fastq)
    bash run_CTAT-LR-Fusion.sh \
        "$sample" \
        /path/to/genome_lib \
        "results/${sample_name}"
done
```

## Troubleshooting

### Docker Build Issues

```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t tool:latest .
```

### Permission Errors

```bash
# Run with user permissions
docker run --user $(id -u):$(id -g) ...
```

### Memory Issues

```bash
# Increase Docker memory limit
docker run --memory=64g ...
```

### Disk Space

```bash
# Check Docker disk usage
docker system df

# Clean up
docker system prune -a --volumes
```

## Output Files

Each tool produces different output formats. Common output files:

- `fusion_predictions.tsv` - Main fusion calls
- `junction_reads.bam` - Reads supporting junctions
- `logs/` - Execution logs
- `intermediate/` - Intermediate files

See individual tool documentation for specific output descriptions.

## Pre-built Images (Optional)

Pre-built Docker images are available on Docker Hub:

```bash
# Pull pre-built image
docker pull YOUR_DOCKERHUB/LongReadsFusionBenchmarking-ctat-lr-fusion:latest

# Run directly
docker run -v /data:/data YOUR_DOCKERHUB/LongReadsFusionBenchmarking-ctat-lr-fusion:latest \
    /data/input.fastq /data/genome_lib /data/output
```

## Citation

If you use these containers, please cite:

1. This benchmark study: [Your Citation]
2. Individual tools (see tool-specific READMEs)
3. Docker: Merkel, D. (2014). Docker: lightweight linux containers for consistent development and deployment.

## Contributing

To add a new tool:

1. Create new directory: `newtool_docker/`
2. Add `Dockerfile` with installation steps
3. Create `run_newtool.sh` wrapper script
4. Add tool documentation
5. Test build and execution
6. Submit pull request

## License

Individual tools retain their original licenses. Container configurations are provided under MIT License.

## Contact

- GitHub Issues: https://github.com/GenomicMedicine/LongReadsFusionBenchmarking/issues
- Email: [YOUR_EMAIL]

---

**Last Updated**: January 2026  
**Docker Version**: 20.10+  
**Platform**: Linux (tested), macOS (compatible), Windows WSL2 (compatible)
