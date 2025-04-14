@echo off

:: Create a new conda environment
call conda create -y -n latentsync python=3.10.13
call conda activate latentsync

:: Install ffmpeg
call conda install -y -c conda-forge ffmpeg

:: Python dependencies
call pip install -r requirements.txt

:: OpenCV dependencies - Windows doesn't need libgl1 installation
:: Windows equivalent is typically handled by the OpenCV package itself

:: Check if huggingface-cli is installed, if not install it
where huggingface-cli >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo huggingface-cli not found, installing...
    call pip install huggingface_hub[cli]
)

:: Download the checkpoints required for inference from HuggingFace
call huggingface-cli download ByteDance/LatentSync-1.5 whisper/tiny.pt --local-dir checkpoints
call huggingface-cli download ByteDance/LatentSync-1.5 latentsync_unet.pt --local-dir checkpoints

echo Setup completed successfully!