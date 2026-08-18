#!/bin/bash
set -e

echo "Downloading CTAT-LR-Fusion plug-n-play genome library..."
wget -c "https://data.broadinstitute.org/Trinity/CTAT_RESOURCE_LIB/GRCh38_gencode_v44_CTAT_lib_Oct292023.plug-n-play.tar.gz"

echo "Extracting CTAT library (this may take a while)..."
tar -xvf GRCh38_gencode_v44_CTAT_lib_Oct292023.plug-n-play.tar.gz

echo "CTAT-LR-Fusion Reference successfully loaded in ctat_genome_lib_build_dir."
