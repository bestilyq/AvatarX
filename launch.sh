#!/bin/bash

source activate base
conda activate latentsync
export PYTHONPATH=$PYTHONPATH:./submodules/LatentSync
python gradio_app.py
conda deactivate