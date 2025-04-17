# LatentSync
Custom Latentsync from bytedance/Latentsync

## 0、环境配置
Cloud Studio中免费基础型GPU空间需手动配置代理，其他空间无需配置
```bash
source set_proxy.sh
```

## 1、下载代码
```bash
git clone --recursive https://github.com/bestilyq/LatentSync.git
```

## 2、下载模型文件，使用hfd加速下载
### 下载hfd，添加可执行权限
```bash
wget https://hf-mirror.com/hfd/hfd.sh
chmod +x hfd.sh
```

### 安装hfd依赖【非root用户需要sudo】
```bash
apt install -y aria2 jq
```

### 下载模型
```bash
./hfd.sh ByteDance/LatentSync-1.5 --include whisper/tiny.pt latentsync_unet.pt --local-dir checkpoints
```

## 3、安装Python环境
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
wget https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64 -O ~/.cache/huggingface/gradio/frpc/frpc_linux_amd64_v0.3
chmod +x ~/.cache/huggingface/gradio/frpc/frpc_linux_amd64_v0.3
```