#!/bin/bash

# 全局环境变量
export http_proxy=http://proxy.cloudstudio.work:8081
export HTTP_PROXY=http://proxy.cloudstudio.work:8081
export https_proxy=http://proxy.cloudstudio.work:8081
export HTTPS_PROXY=http://proxy.cloudstudio.work:8081
export no_proxy=127.0.0.1,localhost,.local,.tencent.com,tencentyun.com,ppa.launchpad.net,0.0.0.0
export NO_PROXY=127.0.0.1,localhost,.local,.tencent.com,tencentyun.com,ppa.launchpad.net,0.0.0.0

# Git 设置全局代理
git config --global http.proxy http://proxy.cloudstudio.work:8081
git config --global https.proxy http://proxy.cloudstudio.work:8081

# 修复 apt update 失败问题
cp /etc/apt/sources.list /etc/apt/sources.list.bak.`date +'%F-%T'`
sed -i 's/http:\/\/mirrors.cloud.tencent.com/https:\/\/mirrors.cloud.tencent.com/g' /etc/apt/sources.list

# （可选）保存到 bashrc
echo 'export http_proxy=http://proxy.cloudstudio.work:8081' >> ~/.bashrc
echo 'export HTTP_PROXY=http://proxy.cloudstudio.work:8081' >> ~/.bashrc
echo 'export https_proxy=http://proxy.cloudstudio.work:8081' >> ~/.bashrc
echo 'export HTTPS_PROXY=http://proxy.cloudstudio.work:8081' >> ~/.bashrc
echo 'export no_proxy=127.0.0.1,localhost,.local,.tencent.com,tencentyun.com,ppa.launchpad.net,0.0.0.0' >> ~/.bashrc
echo 'export NO_PROXY=127.0.0.1,localhost,.local,.tencent.com,tencentyun.com,ppa.launchpad.net,0.0.0.0' >> ~/.bashrc


# 升级系统到最新，以免后续安装依赖时报错
if [ "$(id -u)" -eq 0 ]; then
    apt -y update
    apt -y upgrade
else
    sudo apt -y update
    sudo apt -y upgrade
fi
