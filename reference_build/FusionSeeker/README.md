# FusionSeeker Reference Notes
FusionSeeker relies on standard alignment tools and references:
1. `GRCh38.primary_assembly.genome.fa` (passed to minimap2 and `--ref`)
2. `gencode.v44.primary_assembly.annotation.gtf` (passed to `--gtf`)

Execute `bash ../common/build_reference.sh` to construct the base templates.
