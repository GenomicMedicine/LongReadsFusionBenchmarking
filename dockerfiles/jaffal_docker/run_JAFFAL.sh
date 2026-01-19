#!/bin/bash

tool_name=$1
file=$2
genome_name=$3
gtf_name=$4


if [ ! -d "/dataset/$tool_name" ]; then
	mkdir "/dataset/$tool_name"
fi

fa_path=/dataset/$file.fasta
if [ ! -f "$fa_path" ]; then
    seqtk seq -A "/dataset/$file.fastq.gz" > "$fa_path"
else
    echo "$fa_path exist"
fi
cd /dataset/$tool_name
/opt/JAFFA/tools/bin/bpipe run -p genome=$genome_name -p annotation=$gtf_name /opt/JAFFA/JAFFAL.groovy $fa_path > ./$file.fastq.gz
rm $fa_path