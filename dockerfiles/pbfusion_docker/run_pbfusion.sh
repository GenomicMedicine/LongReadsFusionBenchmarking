#!/bin/bash

tool_name=$1
file=$2
seq_type=$3
corenum=$4
min_support=$5



if [ ! -d "/dataset/$tool_name" ]; then
	mkdir "/dataset/$tool_name"
fi
chmod 755 /dataset/$tool_name

fq_path=/dataset/$file.fastq
if [ ! -f "$fq_path" ]; then
    gunzip /dataset/$file.fastq.gz
    fq_path=/dataset/$file.fastq
fi

if [[ "$seq_type" == 'PacBio' ]]; then
	seqtk seq -A $fq_path | awk '{if (/^>/){print $1"-molecule"} else {print}}' > /dataset/$tool_name/$file.fastq
	pbmm2 align --num-threads $corenum --preset ISOSEQ --sort "/Reference/genome.mmi" /dataset/$tool_name/$file.fastq /dataset/$tool_name/$file.bam
else
	seqtk seq -A $fq_path | awk '{if (/^>/){print $1"-ccs"} else {print}}' > /dataset/$tool_name/$file.fastq
	pbmm2 align --num-threads $corenum --preset CCS --sort "/Reference/genome.mmi" /dataset/$tool_name/$file.fastq /dataset/$tool_name/$file.bam
fi

# max_rt_distance [default: 100000]
#pbfusion discover -b /dataset/$tool_name/$file.bam --gtf "/Reference/annotation.bin" --output-prefix /dataset/$tool_name/fusion_detection --threads $corenum --max-readthrough $max_rt_distance --min-coverage $min_support
pbfusion discover -b /dataset/$tool_name/$file.bam --gtf "/Reference/annotation.bin" --output-prefix /dataset/$tool_name/fusion_detection --threads $corenum --min-coverage $min_support

if [ -f "$fq_path" ]; then
    gzip -c $fq_path > /dataset/$file.fastq.gz
    rm $fq_path
fi

