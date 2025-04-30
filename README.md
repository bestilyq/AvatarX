# AvatarX

A digital human project built with [LatentSync](https://github.com/bytedance/LatentSync) and [F5-TTS](https://github.com/SWivid/F5-TTS)

## 0、初始化系统环境（仅CloudStudio上免费GPU空间）

```bash
wget https://gist.githubusercontent.com/bestilyq/914346fcc138da5cf5e36b4f9476604e/raw/8a5423959da751bba80b10cf315a1607bb8efc80/init_cloudstudio.sh
chmod +x init_cloudstudio.sh
source init_cloudstudio.sh
```

## 1、下载项目代码

```bash
git clone --recursive https://github.com/bestilyq/AvatarX.git
cd AvatarX
```

## 2、创建python虚拟环境，安装项目依赖

```bash
source setup_env.sh
```

## 3、运行程序

```bash
./launch.sh
```

