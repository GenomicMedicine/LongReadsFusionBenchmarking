#!/bin/bash

root=$1
tool_name=$2
file=$3
corenum=$4



if [ ! -d "$root/$tool_name" ]; then
	mkdir $root/$tool_name
fi


ctat-LR-fusion -T "/dataset/$file.fastq.gz" \
                --genome_lib_dir /ctat_genome_lib \
                -o "/dataset/$tool_name" \
                --CPU $corenum