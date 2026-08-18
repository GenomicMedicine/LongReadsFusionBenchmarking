#!/bin/bash
set -e

echo "Downloading common GRCh38 genome and GENCODE v44 annotations..."
wget -c "http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/GRCh38.primary_assembly.genome.fa.gz"
wget -c "http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.primary_assembly.annotation.gtf.gz"
wget -c "http://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.transcripts.fa.gz"

echo "Extracting common references..."
gunzip -k -f GRCh38.primary_assembly.genome.fa.gz || true
gunzip -k -f gencode.v44.primary_assembly.annotation.gtf.gz || true
gunzip -k -f gencode.v44.transcripts.fa.gz || true

echo "Common References (Genome FASTA, GTF, Transcriptome) are ready."
