#!/bin/bash

tool_name=$1
file=$2
seq_type=$3
corenum=$4
genome_name=$5 
gtf_name=$6



if [ ! -d "/dataset/$tool_name" ]; then
	mkdir /dataset/$tool_name
fi

fq_path=/dataset/$file.fastq
if [ ! -f "$fq_path" ]; then
    gunzip /dataset/$file.fastq.gz
    fq_path=/dataset/$file.fastq
fi

if [ "$seq_type" == "ONT_cDNA" ] || [ "$seq_type" == "ONT_dcDNA" ]; then
    mini_genome_opt="-x splice"
    mini_transcriptome_opt="-x map-ont"
elif [ "$seq_type" == "ONT_dRNA" ]; then
    mini_genome_opt="-x splice -uf -k14"
    mini_transcriptome_opt="-x map-ont"
elif [ "$seq_type" == "PacBio" ]; then
    mini_genome_opt="-x splice:hq -uf"
    mini_transcriptome_opt="-x map-pb"
else
    echo "Please input right sequencing type, such as ONT_cDNA, ONT_dRNA, PacBio"
fi
minimap2 -t $corenum $mini_genome_opt "/Reference/genome.fa" $fq_path > /dataset/$tool_name/${file}_$genome_name.paf 
minimap2 -t $corenum $mini_transcriptome_opt "/Reference/transcriptome.fa" $fq_path > /dataset/$tool_name/${file}_refseq.paf

python /FUGAREC/src/Prep_Gap-Realignment.py /dataset $file "/FUGAREC/data/ref" $genome_name $gtf_name

seqkit fq2fa $fq_path > ${fq_path%.fastq}.fa

#$seqkit_path split -p $corenum 
pblat -q=dna -t=dna -out=blast8 -minScore=15 -stepSize=5 -threads=$corenum /FUGAREC/data/ref/GRCh38.primary_assembly.genome.2bit ${fq_path%.fastq}.fa /dataset/$tool_name/${file}_gap_blat_min15_stp5.psl -ooc=/FUGAREC/data/ref/$genome_name.11.ooc

python /FUGAREC/src/Detect_Fusion.py /dataset $file "/FUGAREC/data/ref" $genome_name $gtf_name

if [ -f "$fq_path" ]; then
    gzip -c $fq_path > /dataset/$file.fastq.gz
    rm $fq_path
fi