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
minimap2 -t $corenum $mini_genome_opt -c "/Reference/genome.fa" $fq_path > /dataset/$tool_name/$file.paf

if [ ! -f "/Reference/cdna.selfalign.tsv" ]; then
	minimap2 "/Reference/transcriptome.fa" "/Reference/transcriptome.fa" -X -t $corenum -2 -c -o /Reference/cdna.selfalign.paf
	cat /Reference/cdna.selfalign.paf | cut -f1,6 | sed 's/_/\t/g' | awk 'BEGIN{OFS="\t";}{print substr($1,1,15),substr($2,1,15),substr($3,1,15),substr($4,1,15);}' | awk '$1!=$3' | sort | uniq > "/Reference/cdna.selfalign.tsv"
fi

# min-support=2 # Minimum read support for fusion calls (default: 3)
# Maximum distance between genes for read-through events (default: 500000)
#genion -i $fq_path --gtf "/Reference/annotation_ensembl.gtf" --gpaf /dataset/$tool_name/$file.paf -s "/Reference/cdna.selfalign.tsv" -d "/Reference/genomicSuperDups.txt" --min-support $min_support --max-rt-distance $max_rt_distance -o /dataset/$tool_name/fusion_detection_results.tsv

genion -i $fq_path --gtf "/Reference/annotation_ensembl.gtf" --gpaf /dataset/$tool_name/$file.paf -s "/Reference/cdna.selfalign.tsv" -d "/Reference/genomicSuperDups.txt" --min-support $min_support -o /dataset/$tool_name/fusion_detection_results.tsv

if [ -f "$fq_path" ]; then
    gzip -c $fq_path > /dataset/$file.fastq.gz
    rm $fq_path
fi
