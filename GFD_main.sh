#!/bin/bash

root=$1
file=$2
seq_type=$3 # ONT_cDNA, ONT_dcDNA, ONT_dRNA, PacBio

genome_name="hg38"
gtf_name="genCode44"
tools=("LongGF" "JAFFAL" "FLAIR_fusion" "FusionSeeker" "CTAT-LR-Fusion" "pbfusion" "genion" "IFDlong")

#tools=("IFDlong")
min_support=1 # Minimum read support for fusion calls
corenum=50

# obtain the absolute path

reference_data_path=$script_dir/Reference_data
# download from gencode: https://www.gencodegenes.org/human/
reference_genome=$reference_data_path/GRCh38.primary_assembly.genome.fa
reference_gtf=$reference_data_path/gencode.v44.primary_assembly.annotation.gtf
reference_transcriptome=$reference_data_path/gencode.v44.transcripts.fa

# download from Ensembl (110 is equal to gencode 44): https://ftp.ensembl.org/pub/release-110/gtf/homo_sapiens/
reference_gtf_ensembl=$reference_data_path/Homo_sapiens.GRCh38.110.gtf # for genion
reference_gtf_ucsc=$reference_data_path/Homo_sapiens/UCSC/hg38/Annotation/Genes/genes.gtf #for IFDlong
# download from ucsc: https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/
reference_duplication=$reference_data_path/genomicSuperDups.txt # for genion
reference_cdna_selfalign=$reference_data_path/cdna.selfalign.tsv # for genion

reference_genome_mmi=$reference_data_path/GRCh38.primary_assembly.genome.mmi # for pbfusion
reference_gtf_bin=$reference_data_path/gencode.v44.primary_assembly.annotation.gtf.bin # for pbfusion

# Convert memory usage to bytes
convert_to_bytes() {
  local value=$1
  local unit=${value: -3}
  local number=${value%$unit}

  case $unit in
    KiB)
      echo $(echo "$number / 1024" | bc)
      ;;
    MiB)
      echo $(echo "$number" | bc)
      ;;
    GiB)
      echo $(echo "$number * 1024" | bc)
      ;;
    TiB)
      echo $(echo "$number * 1024 * 1024" | bc)
      ;;
    *)
      echo $number
      ;;
  esac
}

for tool_name in "${tools[@]}"; do
  echo "Running $tool_name..."

  start_time=$(date +%s.%N)
  
  case $tool_name in
    LongGF)
      container_id=$(docker run --user=$(id -u):$(id -g) -d -v $root:/dataset -v $reference_genome:/Reference/genome.fa -v $reference_gtf:/Reference/annotation.gtf mark614/gfd:longgf-5.20 $tool_name $file $seq_type $corenum $min_support)
      ;;
    JAFFAL)
      container_id=$(docker run --user=$(id -u):$(id -g) -d -v $root:/dataset mark614/gfd:jaffal-5.20 $tool_name $file $genome_name $gtf_name)
      ;;
    FLAIR_fusion)
      container_id=$(docker run --user=$(id -u):$(id -g) -d -v $root:/dataset -v $reference_transcriptome:/Reference/transcriptome.fa -v $reference_genome:/Reference/genome.fa -v $reference_gtf:/Reference/annotation.gtf mark614/gfd:flair_fusion-5.20 $tool_name $file $corenum $min_support)
      ;;
    FusionSeeker)
      container_id=$(docker run --user=$(id -u):$(id -g) -d -v $root:/dataset -v $reference_genome:/Reference/genome.fa -v $reference_gtf:/Reference/annotation.gtf mark614/gfd:fusionseeker-5.20 $tool_name $file $seq_type $corenum $min_support)
      ;;
    CTAT-LR-Fusion)
      container_id=$(docker run --user=$(id -u):$(id -g) -d -v $root:/dataset -v $reference_data_path/GRCh38_gencode_v44_CTAT_lib_Oct292023.plug-n-play/ctat_genome_lib_build_dir:/ctat_genome_lib ctat_lr_fusion:5.20 $root $tool_name $file $corenum)
      ;;
    pbfusion)
      container_id=$(docker run --user=$(id -u):$(id -g) -d -v $root:/dataset -v $reference_genome_mmi:/Reference/genome.mmi -v $reference_gtf_bin:/Reference/annotation.bin mark614/gfd:pbfusion-5.20 $tool_name $file $seq_type $corenum $min_support)
      ;;
    genion)
      container_id=$(docker run --user=$(id -u):$(id -g) -d -v $root:/dataset -v $reference_genome:/Reference/genome.fa -v $reference_gtf_ensembl:/Reference/annotation_ensembl.gtf -v $reference_transcriptome:/Reference/transcriptome.fa -v $reference_duplication:/Reference/genomicSuperDups.txt -v $reference_cdna_selfalign:/Reference/cdna.selfalign.tsv mark614/gfd:genion-5.20 $tool_name $file $seq_type $corenum $min_support)
      ;;
    FUGAREC)
      container_id=$(docker run --user=$(id -u):$(id -g) -d -v $root:/dataset -v $reference_transcriptome:/Reference/transcriptome.fa -v $reference_genome:/Reference/genome.fa -v $reference_gtf:/Reference/annotation.gtf mark614/gfd:fugarec-5.20 $tool_name $file $seq_type $corenum $genome_name $gtf_name)
      ;;
    IFDlong)
      container_id=$(docker run --user=$(id -u):$(id -g) -d -v $root:/dataset mark614/gfd:ifdlong-5.20 $tool_name $file $seq_type $genome_name $corenum)
      ;;
    *)
      echo "Invalid tool name"
      ;;
  esac

  start_time=$(date +%s)
  max_memory_usage=0

  # Monitor the container's memory usage
  while [ "$(docker ps -q -f id=$container_id)" ]; do
    current_memory_usage=$(docker stats --no-stream --format "{{.MemUsage}}" $container_id | awk '{print $1}')
    current_memory_usage_mb=$(convert_to_bytes $current_memory_usage)
    
    if (( $(echo "$current_memory_usage_mb > $max_memory_usage" | bc -l) )); then
      max_memory_usage=$current_memory_usage_mb
    fi
    
  done

  end_time=$(date +%s)
  run_time=$((end_time - start_time))

  echo "Tool: $tool_name, File: $file:" >> "$root/$tool_name/runtime_memory.txt"
  echo "Total time (s): $run_time" >> "$root/$tool_name/runtime_memory.txt"
  echo "Memory usage (Mb): $max_memory_usage" >> "$root/$tool_name/runtime_memory.txt"
  echo "" >> "$root/$tool_name/runtime_memory.txt"

  docker rm $container_id

done
