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

# Check if huggingface-cli is installed, if not install it
if ! command -v huggingface-cli &> /dev/null; then
    echo "huggingface-cli not found, installing..."
    pip install huggingface_hub[cli]
fi

# Download the checkpoints required for inference from HuggingFace
huggingface-cli download ByteDance/LatentSync-1.5 whisper/tiny.pt --local-dir checkpoints
huggingface-cli download ByteDance/LatentSync-1.5 latentsync_unet.pt --local-dir checkpoints