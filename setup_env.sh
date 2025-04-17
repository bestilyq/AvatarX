#!/bin/bash

# Create a new conda environment
conda create -y -n latentsync python=3.10.13
conda activate latentsync

# Install ffmpeg
conda install -y -c conda-forge ffmpeg

# Python dependencies
pip install -r requirements.txt

# OpenCV dependencies
if [ "$(id -u)" -eq 0 ]; then
    apt -y install libgl1
else
    sudo apt -y install libgl1
fi