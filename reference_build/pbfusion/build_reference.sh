#!/bin/bash
set -e

COMMON_DIR="$(pwd)/../common"

# Ensure common has been downloaded 
if [ ! -f "$COMMON_DIR/GRCh38.primary_assembly.genome.fa" ] || [ ! -f "$COMMON_DIR/gencode.v44.primary_assembly.annotation.gtf" ]; then
    echo "Common references not found. Running common/build_reference.sh..."
    cd "$COMMON_DIR" && bash build_reference.sh
    cd -
fi

echo "Building pbfusion GTF bin from common GTF using pbfusion Docker container..."
# Use pbfusion container to index the GTF
docker run --rm -v $COMMON_DIR:/ref mark614/gfd:pbfusion-5.20 pbfusion index -g /ref/gencode.v44.primary_assembly.annotation.gtf -o /ref/annotation.bin

echo "Building pbfusion MM2 index (mmi) for GRCh38 using pbmm2 (Warning: requires pbmm2)..."
# In case pbmm2 is not found locally, we execute it via another logic or direct user to install pbmm2
if command -v pbmm2 >/dev/null 2>&1; then
    pbmm2 index "$COMMON_DIR/GRCh38.primary_assembly.genome.fa" "$COMMON_DIR/GRCh38.primary_assembly.genome.mmi"
else
    echo "Warning: pbmm2 is not installed natively. You'll need it locally or from a container to build 'GRCh38.primary_assembly.genome.mmi'."
    echo "Command to run: pbmm2 index GRCh38.primary_assembly.genome.fa GRCh38.primary_assembly.genome.mmi"
fi

echo "pbfusion indices (mmi and annotation.bin) generated in $COMMON_DIR."
