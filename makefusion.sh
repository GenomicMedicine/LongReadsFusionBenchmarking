#!/bin/bash

##coverage: 1,5,10,50,100
#identities: 80%(80,90,6), 85% (85,95,4.5), 90%(90,95,3.5), 95%(95,99,2.5), 99.8% (30,3)
#mean_read_length: 300,100; 1000,800; 5000,4000; 15000,13000; 50000,20000
#error_model: nanopore2023(ONT R10.4.1 reads from 2023),nanopore2020(ONT R9.4.1 reads from 2020),nanopore2018(ONT R9.4/R9.4.1 reads from 2018),pacbio2016(PacBio RS II reads from 2016),pacbio2021(PacBio Sequel IIe HiFi reads from 2021)
#qscore_model：nanopore2023(ONT R10.4.1 reads from 2023),nanopore2020(ONT R9.4.1 reads from 2020),nanopore2018(ONT R9.4/R9.4.1 reads from 2018),pacbio2016(PacBio RS II reads from 2016),pacbio2021(PacBio Sequel IIe HiFi reads from 2021) 
#
#default: 10X, 95%, 15000,13000, nanopore2023
#other options: --junk_reads 0 --random_reads 0 --chimeras 0
ref=$1
coverage=$2
identities=$3
case $identities in
    "0.8")
        identities_update="80,90,6"
        ;;
    "0.85")
        identities_update="85,95,4.5"
        ;;
    "0.9")
        identities_update="90,95,3.5"
        ;;
    "0.95")
        identities_update="95,99,2.5"
        ;;
    "0.998")
        identities_update="30,3"
        ;;
    *)
        echo "Invalid identities selected"
        ;;
esac

mean_read_length=$4
case $mean_read_length in
    "300")
        mean_read_length_update="300,100"
        ;;
    "1000")
        mean_read_length_update="1000,800"
        ;;
    "5000")
        mean_read_length_update="5000,4000"
        ;;
    "15000")
        mean_read_length_update="15000,13000"
        ;;
    "50000")
        mean_read_length_update="50000,20000"
        ;;
    *)
        echo "Invalid mean_read_length selected"
        ;;
esac

error_model=$5
qscore_model=$5


output=$6
name="${output}/${error_model}_${coverage}x_${identities}_${mean_read_length}"

badread simulate --reference $ref --quantity ${coverage}x --length $mean_read_length_update --identity $identities_update --error_model $error_model --qscore_model $qscore_model --junk_reads 0 --random_reads 0 --chimeras 0| gzip > $name.fastq.gz

