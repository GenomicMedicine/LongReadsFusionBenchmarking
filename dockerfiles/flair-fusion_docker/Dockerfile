FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update && apt-get -qq -y install \
    build-essential \
    curl \
    libssl-dev \
    libsqlite3-dev \
    libreadline-dev \
    python3 \
    python3-dev \
    python3-distutils \
    python3-pip \
    python3-setuptools \
    zlib1g-dev


ENV LANG C.UTF-8
ENV SHELL /bin/bash
ENV SRC=/usr/local/src
ENV BIN=/usr/local/bin

RUN /bin/bash -c "curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-\$(uname -m).sh > mambaforge.sh && \
    bash mambaforge.sh -b -p /opt/conda && \
    rm mambaforge.sh"

ENV PATH="/opt/conda/bin:${PATH}"
ARG PATH="/opt/conda/bin:${PATH}"

RUN mamba create -q -y -c bioconda -n flair_fusion pysam flair minimap2 

RUN apt-get install -qq -y samtools bedtools

RUN mamba install -q -y -n flair_fusion scipy

#RUN git clone https://github.com/cafelton/FLAIR-fusion-v2.git

COPY FLAIR-fusion-v2 /FLAIR-fusion

ENV PATH="/opt/conda/envs/flair_fusion/bin:/FLAIR-fusion:${PATH}"

RUN echo "source activate flair_fusion" > ~/.bashrc

# use absolute path
COPY run_FLAIR-fusion.sh /usr/local/bin/script.sh
RUN chmod +x /usr/local/bin/script.sh

ENTRYPOINT ["/usr/local/bin/script.sh"]

