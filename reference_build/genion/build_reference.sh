#!/bin/bash
set -e

echo "Downloading genion specific genomic super-duplications..."
wget -c "http://hgdownload.cse.ucsc.edu/goldenpath/hg38/database/genomicSuperDups.txt.gz"
gunzip -k -f genomicSuperDups.txt.gz || true

echo "Genion relies on 'cDNA self alignments'. For a generic genion run, ensure you provide the correct TSV mapping file as per their protocol."
echo "Reference files for genion (genomicSuperDups.txt) prepared."
