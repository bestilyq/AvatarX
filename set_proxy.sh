#!/bin/bash

# 以下内容来自 https://doc.weixin.qq.com/doc/w3_AawAogYrAKkJQfjqKWLQtu972EETX?scode=AJEAIQdfAAoRmyu0uH

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

# 保存到 bashrc
echo 'export http_proxy=http://proxy.cloudstudio.work:8081' >> ~/.bashrc
echo 'export HTTP_PROXY=http://proxy.cloudstudio.work:8081' >> ~/.bashrc
echo 'export https_proxy=http://proxy.cloudstudio.work:8081' >> ~/.bashrc
echo 'export HTTPS_PROXY=http://proxy.cloudstudio.work:8081' >> ~/.bashrc
echo 'export no_proxy=127.0.0.1,localhost,.local,.tencent.com,tencentyun.com,ppa.launchpad.net,0.0.0.0' >> ~/.bashrc
echo 'export NO_PROXY=127.0.0.1,localhost,.local,.tencent.com,tencentyun.com,ppa.launchpad.net,0.0.0.0' >> ~/.bashrc