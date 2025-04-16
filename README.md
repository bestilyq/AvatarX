# LatentSync
Custom Latentsync from bytedance/Latentsync

## 1、下载代码
```shell
git clone --recursive https://github.com/bestilyq/LatentSync.git
```

## 2、使用国内hugging face镜像，设置 HF_ENDPOINT 环境变量
### Linux/Mac OS
```shell
export HF_ENDPOINT="https://hf-mirror.com"
```

### Linux 写入到~/.bashrc中：
```shell
echo 'export HF_ENDPOINT="https://hf-mirror.com"' >> ~/.bashrc
```

### Mac OS 写入到 ~/.zshrc 中：
```shell
echo 'export HF_ENDPOINT="https://hf-mirror.com"' >> ~/.zshrc
```

### Windows Powershell写入到 ~\Documents\WindowsPowerShellMicrosoft.PowerShell_profile.ps1 中：
```powershell
Add-Content -Path $PROFILE -Value '$env:HF_ENDPOINT = "https://hf-mirror.com"'
```

### Python
```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```
> **注意：** os.environ 必须在 import huggingface 库相关语句之前执行。

## 3、下载模型文件
### 下载hfd
```shell
wget https://hf-mirror.com/hfd/hfd.sh
chmod a+x hfd.sh
```

### 安装hfd依赖
#### Linux
```shell
sudo apt install -y aria2 jq
```
#### Windows
```shell
choco install aria2 jq
```

### 下载模型
```shell
./hfd.sh ByteDance/LatentSync-1.5 --local-dir checkpoints
```

## 4、安装Python环境
### 确认cuda版本
```bash
nvcc --version
```
**注意：** 如果cuda版本为11.x，需要将requirements.txt中的onnxruntime-gpu改为onnxruntime-gpu==1.18.0

### 创建python虚拟环境，安装项目依赖
```bash
source setup_env.sh
```
### 运行gradio主程序
```bash
python gradio_app.py
```

### 如果创建共享链接失败则执行下面命令后再运行gradio程序
```bash
mv frpc_linux_amd64_v0.3 ~/.cache/huggingface/gradio/frpc/frpc_linux_amd64_v0.3
chmod a+x ~/.cache/huggingface/gradio/frpc/frpc_linux_amd64_v0.3
```