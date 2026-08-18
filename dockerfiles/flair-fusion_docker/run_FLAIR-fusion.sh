#!/bin/bash

tool_name=$1
file=$2
min_support=$3



if [ ! -d "/dataset/$tool_name" ]; then
	mkdir /dataset/$tool_name
fi

fq_path=/dataset/$file.fastq
if [ ! -f "$fq_path" ]; then
    gunzip /dataset/$file.fastq.gz
    fq_path=/dataset/$file.fastq
fi

bam_file=$(find "/FLAIR-fusion" -type f -name '*transcriptomeAligned.bam')
annotaion_file=$(find "/FLAIR-fusion" -type f -name '*annotation.tsv')
filteredReadLen_file=$(find "/FLAIR-fusion" -type f -name '*TranscriptomeGeneToNeighbors-filteredReadLen.tsv')

python /FLAIR-fusion/fusionfindingpipeline.py -r $fq_path -t "/Reference/transcriptome.fa" -g "/Reference/genome.fa" -a "/Reference/annotation.gtf" -o /dataset/$tool_name/$file -m -i -e $annotaion_file -p $filteredReadLen_file -s $bam_file -l $min_support

if [ -f "$fq_path" ]; then
    gzip -c $fq_path > /dataset/$file.fastq.gz
    rm $fq_path
fi

