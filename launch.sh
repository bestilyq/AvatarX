source activate base
conda activate latentsync
export PYTHONPATH=$PYTHONPATH:./LatentSync
python gradio_app.py