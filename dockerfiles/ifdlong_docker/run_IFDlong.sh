#!/bin/bash

tool_name=$1
file=$2
seq_type=$3
genome_name=$4
corenum=$5



if [ ! -d "/dataset/$tool_name" ]; then
	mkdir /dataset/$tool_name
fi

fq_path=/dataset/$file.fastq
if [ ! -f "$fq_path" ]; then
    gunzip /dataset/$file.fastq.gz
    fq_path=/dataset/$file.fastq
fi

if [ "$seq_type" == "ONT_cDNA" ] || [ "$seq_type" == "ONT_dcDNA" ]; then
    mini_genome_opt="-ax splice"
    mini_transcriptome_opt="-ax map-ont"
elif [ "$seq_type" == "ONT_dRNA" ]; then
    mini_genome_opt="-ax splice -uf -k14"
    mini_transcriptome_opt="-ax map-ont"
elif [ "$seq_type" == "PacBio" ]; then
    mini_genome_opt="-ax splice:hq -uf"
    mini_transcriptome_opt="-ax map-pb"
else
    echo "Please input right sequencing type, such as ONT_cDNA, ONT_dRNA, PacBio"
fi

#minimap2 -t $corenum $mini_genome_opt /IFDlong/refData/$genome_name/genome.fa $fq_path | samtools view -Sb | samtools sort -o /dataset/$tool_name/$file.bam
#samtools index /dataset/$tool_name/$file.bam 
#bash /IFDlong/IFDlong.sh -o /dataset/$tool_name -n $file -b "/dataset/$tool_name/$file.bam" -l "self_align" -g $genome_name -t 9 -a 10 -c $corenum

bash /IFDlong/IFDlong_minimap2_opt.sh -o /dataset/$tool_name -n $file -i $fq_path -g $genome_name -t 9 -a 10 -c $corenum -m "$mini_genome_opt"

if [ -f "$fq_path" ]; then
    gzip -c $fq_path > /dataset/$file.fastq.gz
    rm $fq_path
fi




