#!/bin/bash

# Create a new conda environment
conda create -y -n avatarx python=3.10.13
conda activate avatarx

# Install ffmpeg
conda install -y -c conda-forge ffmpeg

# Upgrade pip
python -m pip install --upgrade pip

# OpenCV dependencies
if [ "$(id -u)" -eq 0 ]; then
    apt -y install libgl1
else
    sudo apt -y install libgl1
fi

# 获取CUDA版本
CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $6}' | cut -d',' -f1 | cut -d'V' -f2)
echo "CUDA Version: $CUDA_VERSION"

# 如果CUDA版本低于12.0，修改临时文件中的onnxruntime-gpu版本
if [[ "$(echo $CUDA_VERSION | cut -d'.' -f1)" -lt 12 ]]; then
    # 判断是否为macOS
    if [[ "$(uname -s)" == "Darwin" ]]; then
        SED_INPLACE="sed -i ''"
    else
        SED_INPLACE="sed -i"
    fi
    # 修改文件中的onnxruntime-gpu版本
    $SED_INPLACE "s/onnxruntime-gpu==1.21.0/onnxruntime-gpu==1.18.0/" "$TEMP_FILE"
fi

pip install -e . --extra-index-url https://download.pytorch.org/whl/cu121

# Download the checkpoints required for inference use hfd
if [ "$(id -u)" -eq 0 ]; then
    apt install -y aria2 jq
else
    sudo apt install -y aria2 jq
fi
wget https://hf-mirror.com/hfd/hfd.sh -O hfd.sh
chmod +x hfd.sh
./hfd.sh ByteDance/LatentSync-1.5 --include whisper/tiny.pt latentsync_unet.pt --local-dir checkpoints