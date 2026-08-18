# LongGF Reference Notes
LongGF relies on standard alignment outputs. It simply requires:
1. `GRCh38.primary_assembly.genome.fa` (for minimap2/bam alignments)
2. `gencode.v44.primary_assembly.annotation.gtf` (to identify fusion boundaries)

Please refer to the `../common/` folder and run `bash ../common/build_reference.sh` to download these foundational files.
