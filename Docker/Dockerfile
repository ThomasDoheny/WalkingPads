FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq -y && apt-get install -qq -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    libsuperlu-dev \
    libblas-dev \
    liblapack-dev \
    perl \
    gnuplot \
    imagemagick \
    vim \
    tmux \
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN pip install numpy --break-system-packages

RUN git clone https://github.com/ThomasDoheny/WalkingPads.git && \
    cd /WalkingPads/voltspot && make clean && make && cd ../.. && rm -rf WalkingPads

CMD ["/bin/bash"]
