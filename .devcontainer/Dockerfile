FROM python:3.14-slim

ENV DEBIAN_FRONTEND=noninteractive

# HA dependencies per https://developers.home-assistant.io/docs/development_environment/
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-dev python3-venv autoconf libssl-dev libxml2-dev libxslt1-dev libjpeg-dev \
    libffi-dev libudev-dev zlib1g-dev pkg-config libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev \
    libswscale-dev libswresample-dev libavfilter-dev ffmpeg libgammu-dev libpcap-dev libturbojpeg0 build-essential

# Add go2rtc binary
COPY --from=ghcr.io/alexxit/go2rtc:latest /usr/local/bin/go2rtc /bin/go2rtc

# additional nice to haves
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    wget \
    less \
    vim \
    jq \
    iputils-ping \
    iproute2 \
    procps \
    htop \
    && rm -rf /var/lib/apt/lists/*

# opencode
RUN apt-get update && apt-get install -y --no-install-recommends \
    ripgrep \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g opencode-ai

ARG REMOTE_USER=vscode
ARG REMOTE_UID=1200
ARG REMOTE_GID=1200

# Create the user and home directory without sudo
RUN groupadd --gid $REMOTE_GID $REMOTE_USER \
    && useradd --uid $REMOTE_UID --gid $REMOTE_GID -m $REMOTE_USER -s /bin/bash

RUN pip install --no-cache-dir uv

USER $REMOTE_USER
WORKDIR /home/$REMOTE_USER

RUN mkdir -p /home/$REMOTE_USER/.local/share
RUN mkdir -p /home/$REMOTE_USER/.local/state
RUN mkdir -p /home/$REMOTE_USER/.config

RUN echo host.docker.internal | tee /home/$REMOTE_USER/.local.modelserver

RUN uv venv /home/vscode/.venvs/homeassistant --python /usr/local/bin/python

