#!/bin/bash

tool_name=$1
file=$2
seq_type=$3
corenum=$4
min_support=$5

if [ ! -d "/dataset/$tool_name" ]; then
	mkdir "/dataset/$tool_name"
fi

fq_path=/dataset/$file.fastq
if [ ! -f "$fq_path" ]; then
    gunzip /dataset/$file.fastq.gz
    fq_path=/dataset/$file.fastq
fi

if [ "$seq_type" == "ONT_cDNA" ] || [ "$seq_type" == "ONT_dcDNA" ]; then
    mini_genome_opt="-ax splice"
    mini_transcriptome_opt="-ax map-ont"
    datatype="nanopore"
elif [ "$seq_type" == "ONT_dRNA" ]; then
    mini_genome_opt="-ax splice -uf -k14"
    mini_transcriptome_opt="-ax map-ont"
    datatype="nanopore"
elif [ "$seq_type" == "PacBio" ]; then
    mini_genome_opt="-ax splice:hq -uf"
    mini_transcriptome_opt="-ax map-pb"
    datatype="isoseq"
else
    echo "Please input right sequencing type, such as ONT_cDNA, ONT_dRNA, PacBio"
fi

minimap2 $mini_genome_opt "/Reference/genome.fa" $fq_path -t $corenum | samtools view -Sb | samtools sort -n -o /dataset/$tool_name/$file.bam

LongGF /dataset/$tool_name/$file.bam "/Reference/annotation.gtf" 100 50 100 0 0 $min_support > /dataset/$tool_name/Genefusion_result.csv

if [ -f "$fq_path" ]; then
    gzip -c $fq_path > /dataset/$file.fastq.gz
    rm $fq_path
fi