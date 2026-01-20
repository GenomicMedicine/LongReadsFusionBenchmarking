# Fusion Detection Tools Documentation

## Overview

This benchmark evaluates 9 fusion detection tools designed for long-read RNA sequencing data. Each tool uses different algorithms and approaches for identifying gene fusions.

## Tools Comparison

| Tool | Version | Platform Support | Algorithm | Speed | Resource |
|------|---------|------------------|-----------|-------|----------|
| **CTAT-LR-Fusion** | 0.13.0 | ONT, PacBio | Alignment-based | Medium | High |
| **JAFFAL** | 2.3 | ONT, PacBio | Hybrid (alignment + assembly) | Fast | Medium |
| **LongGF** | 1.0 | ONT, PacBio | Read clustering | Fast | Low |
| **FusionSeeker** | 1.2 | ONT, PacBio | Split-read mapping | Medium | Medium |
| **FLAIR-fusion** | 2.0 | ONT, PacBio | Isoform-aware | Slow | High |
| **pbfusion** | 0.4.0 | PacBio (optimized) | Junction-based | Fast | Low |
| **IFDlong** | 1.0 | ONT, PacBio | Integrated filtering | Medium | Medium |
| **genion** | 1.1 | ONT, PacBio | Machine learning | Medium | Medium |


## Tool Details

### CTAT-LR-Fusion

**Description**: Comprehensive fusion detection tool from the CTAT (Cancer Transcript Annotation Toolkit) suite, specifically adapted for long reads.

**Algorithm**:
- Aligns reads to reference genome and transcriptome
- Identifies chimeric alignments spanning gene boundaries
- Advanced filtering for false positives
- Provides detailed junction support

**Strengths**:
- High sensitivity and specificity
- Well-documented and maintained
- Part of established CTAT ecosystem
- Detailed output with evidence tracking

**Limitations**:
- Higher computational requirements
- Slower than some alternatives

**Citation**: Haas BJ et al. (2019) CTAT-LR-Fusion

**Docker Usage**:
```bash
cd dockerfiles/CTAT-LR-Fusion_docker
bash run_CTAT-LR-Fusion.sh \
    /path/to/reads.fastq \
    /path/to/ctat_genome_lib \
    /path/to/output
```

---

### JAFFAL

**Description**: Joint Approach for Fusion Finding using Long-read Analysis. Combines alignment and assembly approaches.

**Algorithm**:
- Initial alignment to transcriptome and genome
- Extracts candidate fusion-supporting reads
- Local assembly of fusion junctions
- Validates with multiple evidence types

**Strengths**:
- Fast execution time
- Good balance of sensitivity/precision
- Handles complex rearrangements well
- Moderate resource requirements

**Limitations**:
- May miss low-coverage fusions
- Assembly step can be sensitive to parameters

**Citation**: Davidson NM et al. (2022) JAFFAL: detecting fusion genes with long-read transcriptome sequencing

**Docker Usage**:
```bash
cd dockerfiles/jaffal_docker
bash run_JAFFAL.sh \
    /path/to/reads.fastq \
    /path/to/genome_lib \
    /path/to/output
```

---

### LongGF

**Description**: Long-read Gene Fusion detection through read clustering.

**Algorithm**:
- Clusters reads by similarity
- Identifies split alignments within clusters
- Reports fusions with cluster support
- Fast k-mer based approach

**Strengths**:
- Very fast
- Low memory footprint
- Simple installation
- Good for high-coverage datasets

**Limitations**:
- Lower sensitivity at low coverage
- May merge similar fusion events

**Citation**: Haas BJ et al. (2018) LongGF

**Docker Usage**:
```bash
cd dockerfiles/longgf_docker
bash run_LongGF.sh \
    /path/to/reads.fastq \
    /path/to/genome_lib \
    /path/to/output
```

---

### FusionSeeker

**Description**: Fusion detection with advanced filtering strategies.

**Algorithm**:
- Split-read mapping to genome
- Junction extraction and classification
- Multi-level filtering pipeline
- False positive reduction

**Strengths**:
- High precision
- Configurable filtering
- Good annotation integration

**Limitations**:
- May have lower sensitivity
- Requires careful parameter tuning

**Citation**: Akers NK et al. (2018) FusionSeeker

**Docker Usage**:
```bash
cd dockerfiles/fusionseeker_docker
bash run_FusionSeeker.sh \
    /path/to/reads.fastq \
    /path/to/genome_lib \
    /path/to/output
```

---

### FLAIR-fusion

**Description**: Fusion detection from FLAIR full-length isoform analysis.

**Algorithm**:
- Full-length isoform reconstruction
- Identifies chimeric isoforms
- Quantifies fusion isoform expression
- Detailed junction characterization

**Strengths**:
- Isoform-level resolution
- Quantification included
- Handles complex splicing
- Detailed output

**Limitations**:
- Slower execution
- Higher memory requirements
- More complex workflow

**Citation**: Tang AD et al. (2020) Full-length transcript characterization of SF3B1 mutation in chronic lymphocytic leukemia reveals downregulation of retained introns

**Docker Usage**:
```bash
cd dockerfiles/flair-fusion_docker
bash run_FLAIR-fusion.sh \
    /path/to/reads.fastq \
    /path/to/genome_lib \
    /path/to/output
```

---

### pbfusion

**Description**: PacBio-optimized fusion caller designed for HiFi reads.

**Algorithm**:
- Optimized for high-accuracy PacBio HiFi
- Junction-based detection
- CCS read-aware filtering
- Fast processing

**Strengths**:
- Excellent for PacBio HiFi data
- Very fast
- Low false positive rate
- Simple workflow

**Limitations**:
- Optimized for PacBio (less optimal for ONT)
- May require high-quality reads

**Citation**: Wenger AM et al. (2019) Accurate circular consensus long-read sequencing improves variant detection and assembly of a human genome

**Docker Usage**:
```bash
cd dockerfiles/pbfusion_docker
bash run_pbfusion.sh \
    /path/to/reads.fastq \
    /path/to/genome_lib \
    /path/to/output
```

---

### IFDlong

**Description**: Integrated Fusion Detection for long reads with comprehensive filtering.

**Algorithm**:
- Multi-step alignment strategy
- Integration of multiple evidence types
- Machine learning-based filtering
- Breakpoint refinement

**Strengths**:
- Comprehensive filtering reduces false positives
- Good for complex genomes
- Detailed breakpoint annotation

**Limitations**:
- Moderate computational requirements
- More complex setup

**Citation**: Liu C et al. (2020) IFDlong

**Docker Usage**:
```bash
cd dockerfiles/ifdlong_docker
bash run_IFDlong.sh \
    /path/to/reads.fastq \
    /path/to/genome_lib \
    /path/to/output
```

---

### genion

**Description**: Gene fusion detection with machine learning classification.

**Algorithm**:
- Read alignment and junction extraction
- Feature extraction from alignments
- Random forest classification
- Confidence scoring

**Strengths**:
- Machine learning reduces false positives
- Confidence scores for predictions
- Handles noisy data well

**Limitations**:
- Requires training data (pre-trained model included)
- Moderate speed

**Citation**: Umeda T et al. (2021) genion

**Docker Usage**:
```bash
cd dockerfiles/genion_docker
bash run_genion.sh \
    /path/to/reads.fastq \
    /path/to/genome_lib \
    /path/to/output
```

---



## Output Formats

### Standard Output Fields

Most tools produce TSV/CSV files with these common fields:

- **Gene_A**: 5' fusion partner gene
- **Gene_B**: 3' fusion partner gene
- **Breakpoint_A**: Breakpoint position in Gene A
- **Breakpoint_B**: Breakpoint position in Gene B
- **Junction_Reads**: Number of junction-spanning reads
- **Spanning_Reads**: Number of spanning read pairs (if applicable)
- **Confidence**: Tool-specific confidence score

### Tool-Specific Outputs

Each tool may include additional information:
- Isoform details (FLAIR-fusion)
- Machine learning scores (genion)
- Reconstructed sequences (FUGAREC)
- Quality metrics (various)

## Recommended Workflows

### For High-Accuracy Data (PacBio HiFi)

```bash
# Primary analysis
pbfusion → CTAT-LR-Fusion → JAFFAL

# Validation
FusionSeeker (high precision filtering)
```

### For Oxford Nanopore Data

```bash
# Primary analysis
CTAT-LR-Fusion → JAFFAL → IFDlong

# High sensitivity
LongGF

# Detailed characterization
FLAIR-fusion
```

### For Low Coverage Data

```bash
# Recommended
CTAT-LR-Fusion → JAFFAL

# Avoid
LongGF (clustering requires depth)
```

## Performance Considerations

### Speed (fastest to slowest)
1. pbfusion, LongGF
2. JAFFAL, genion
3. CTAT-LR-Fusion, FusionSeeker, IFDlong
4. FLAIR-fusion, FUGAREC

### Memory Requirements
- **Low (<8GB)**: pbfusion, LongGF
- **Medium (8-16GB)**: JAFFAL, FusionSeeker, genion, IFDlong
- **High (>16GB)**: CTAT-LR-Fusion, FLAIR-fusion, FUGAREC

### Sensitivity/Specificity Trade-off
- **High Sensitivity**: CTAT-LR-Fusion, LongGF
- **Balanced**: JAFFAL, IFDlong, genion
- **High Specificity**: FusionSeeker, pbfusion

## Citation

If you use this benchmark, please cite the individual tools you analyzed.

---

**Last Updated**: January 2026
