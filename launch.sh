#!/bin/bash

source activate base
conda activate latentsync
export PYTHONPATH=$PYTHONPATH:./submodules/LatentSync:./submodules/F5-TTS/src
python gradio_app.py
conda deactivate