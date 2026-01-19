FROM continuumio/miniconda3:latest

ENV DEBIAN_FRONTEND=noninteractive

ENV LANG C.UTF-8
ENV SHELL /bin/bash
ENV SRC=/usr/local/src
ENV BIN=/usr/local/bin

# Create a new environment named 'ifdlong'
RUN conda create -n ifdlong python=3.10 -y

# Activate the 'ifdlong' environment
#SHELL ["conda", "run", "-n", "ifdlong", "/bin/bash", "-c"]

# Install the required packages
RUN conda install -n ifdlong -c conda-forge -c defaults -c bioconda -c r \
    samtools \
    minimap2 \
    bedtools \
    libxml2 \
    bioconductor-summarizedexperiment \
    bioconductor-genomicalignments \
    bioconductor-rtracklayer \
    r-base \
    r-biocmanager \
    r-dplyr \
    r-stringr \
    r-devtools \
    r-rlist \
    -y

# IFDlong
COPY IFDlong /IFDlong

RUN chmod +x /IFDlong/*.sh

RUN mkdir -p /IFDlong/tools/bin

# R file
RUN chmod +x /IFDlong/scripts/*.R

RUN echo "// Path to scripts used by the IFDlong pipeline" > /IFDlong/tools.path \
    && echo "reportFuns=\"/IFDlong/scripts/reportFuns.R\"" >> /IFDlong/tools.path \
    && echo "reportFuns_parallel=\"/IFDlong/scripts/reportFuns_parallel.R\"" >> /IFDlong/tools.path \
    && echo "EXONuncover=\"/IFDlong/scripts/EXONuncover.R\"" >> /IFDlong/tools.path \
    && echo "report=\"/IFDlong/scripts/report.R\"" >> /IFDlong/tools.path \
    && echo "quant=\"/IFDlong/scripts/quant.R\"" >> /IFDlong/tools.path \
    && echo "refGen=\"/IFDlong/scripts/refGen.R\"" >> /IFDlong/tools.path \
    && echo "refAAGen=\"/IFDlong/scripts/refAAGen.R\"" >> /IFDlong/tools.path

RUN echo "source activate ifdlong" > ~/.bashrc

ENV PATH="/opt/conda/envs/ifdlong/bin:/IFDlong:${PATH}"

RUN R -e "devtools::install_github('helixcn/seqRFLP')" && exit

RUN R_path=$(which Rscript 2>/dev/null) \
    && if [ -z "$R_path" ]; then \
        echo "R not found! Require the dependent packages: parallel, rlist, stringr, rtracklayer, Biostrings, dplyr, seqRFLP." >&2 \
        && exit 1; \
    else \
        echo "Rscript=\"$R_path\"" >> /IFDlong/tools.path; \
    fi

RUN bedtools_path=$(which bedtools 2>/dev/null) \
    && if [ -z "$bedtools_path" ]; then \
        echo "bedtools not found!" >&2 \
        && exit 1; \
    else \
        echo "bedtools=\"$bedtools_path\"" >> /IFDlong/tools.path; \
    fi

RUN samtools_path=$(which samtools 2>/dev/null) \
    && if [ -z "$samtools_path" ]; then \
        echo "samtools not found!" >&2 \
        && exit 1; \
    else \
        echo "samtools=\"$samtools_path\"" >> /IFDlong/tools.path; \
    fi

RUN minimap2_path=$(which minimap2 2>/dev/null) \
    && if [ -z "$minimap2_path" ]; then \
        echo "minimap2 not found!" >&2 \
        && exit 1; \
    else \
        echo "minimap2=\"$minimap2_path\"" >> /IFDlong/tools.path; \
    fi

RUN echo "$(cat /IFDlong/tools.path)"

# use absolute path
COPY run_IFDlong.sh /usr/local/bin/script.sh
RUN chmod +x /usr/local/bin/script.sh

ENTRYPOINT ["/usr/local/bin/script.sh"]

