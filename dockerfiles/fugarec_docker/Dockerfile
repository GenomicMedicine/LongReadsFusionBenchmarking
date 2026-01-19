FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update && apt-get -qq -y install \
    build-essential \
    bzip2 \
    curl \
    gcc \
    g++ \
    git \
    libbz2-dev \
    libffi-dev \
    libncurses5-dev \
    libreadline-dev \
    libssl-dev \
    libsqlite3-dev \
    libssl-dev \
    libgdbm-dev \
    libc6-dev \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    libcurl4-openssl-dev \
    make \
    python3 \
    python3-dev \
    python3-distutils \
    python3-pip \
    python3-setuptools \
    tk-dev \
    uuid-dev \
    zlib1g-dev


ENV LANG C.UTF-8
ENV SHELL /bin/bash
ENV SRC=/usr/local/src
ENV BIN=/usr/local/bin


# pblat
WORKDIR $SRC
RUN git clone https://github.com/icebert/pblat.git \
    && cd pblat \
    && make \
    && mv pblat $BIN/ \
    && cd .. \
    && rm -rf pblat

RUN /bin/bash -c "curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-\$(uname -m).sh > mambaforge.sh && \
    bash mambaforge.sh -b -p /opt/conda && \
    rm mambaforge.sh"

ENV PATH="/opt/conda/bin:${PATH}"
ARG PATH="/opt/conda/bin:${PATH}"

RUN mamba create -q -y -c bioconda -n fugarec minimap2 seqkit

RUN apt-get install -qq -y samtools 

RUN mamba install -q -y -c conda-forge -n fugarec pandas numpy tqdm

#RUN git clone https://github.com/cafelton/FLAIR-fusion-v2.git

COPY FUGAREC /FUGAREC

ENV PATH="/opt/conda/envs/fugarec/bin:/FUGAREC:${PATH}"

RUN echo "source activate flair_fusion" > ~/.bashrc

# use absolute path
COPY run_FUGAREC.sh /usr/local/bin/script.sh
RUN chmod +x /usr/local/bin/script.sh

ENTRYPOINT ["/usr/local/bin/script.sh"]

