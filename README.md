# LatentSync
Custom Latentsync from bytedance/Latentsync

## 0、初始化系统环境（可选）
```bash
./init_env.sh
```

## 1、下载代码
```bash
git clone --recursive https://github.com/bestilyq/LatentSync.git
```

## 2、创建python虚拟环境，安装项目依赖
```bash
source setup_env.sh
```
## 3、运行gradio主程序
```bash
export PYTHONPATH=$PYTHONPATH:./LatentSync
python gradio_app.py
```
或者
```bash
./launch.sh
```