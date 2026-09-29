---
title: "nvidia-docker + helm+cuda+gpu_burn"
date: "2024-08-01 17:51:49"
category: "cluster"
source: "https://blog.51cto.com/hequan/11633590"
---
> **内容介绍**
>
> 本文记录 Kubernetes GPU 节点的环境搭建过程：先安装
> nvidia-container-toolkit 与 nvidia-docker2，配置 Docker 和
> containerd 使用 NVIDIA 运行时；再安装 Helm 二进制与 CUDA 12.4
> 工具链；最后用 gpu-burn 对 GPU 做 100 秒双精度压测验证。

> **技术备注**
>
> nvidia-docker 项目已更名为 NVIDIA Container Toolkit，nvidia-docker2
> 为旧包名，新环境只需安装 nvidia-container-toolkit 即可，文中的
> nvidia-docker.repo 源地址现已停用。gpu-burn 是开源 GPU 压测工具，
> `-d` 表示双精度、`100` 为持续秒数；文中仅安装 Helm 二进制，
> 未涉及 chart 部署。新版 K8s 默认运行时为 containerd，请留意配置。

---

## 1. 安装 NVIDIA 容器运行时

先按系统版本添加 nvidia-docker 的 yum 源，再安装相关包：

```shell
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | tee /etc/yum.repos.d/nvidia-docker.repo

yum install -y nvidia-container-toolkit
yum install -y nvidia-docker2
yum install nvidia-container-runtime -y
```

## 2. 配置 Docker 使用 NVIDIA 运行时

编辑 `/etc/docker/daemon.json`，注册名为 `nvidia` 的运行时：

```json
{
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

重载配置并重启 Docker：

```shell
systemctl daemon-reload && systemctl restart docker
```

## 3. 配置 containerd 默认运行时

编辑 `/etc/containerd/config.toml`，把默认运行时改为 nvidia-container-runtime：

```toml
[plugins."io.containerd.grpc.v1.cri"]
  [plugins."io.containerd.grpc.v1.cri".containerd]
    default_runtime_name = "nvidia-container-runtime" # 修改为nvidia-container-runtime
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
    runtime_type = "io.containerd.runc.v2" # 修改为io.containerd.runc.v2
  # 新增以下
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia-container-runtime]
    runtime_type = "io.containerd.runtime.v1.linux"
    runtime_engine = "/usr/bin/nvidia-container-runtime"
```

重载配置并重启 containerd：

```shell
systemctl daemon-reload && systemctl restart containerd
```

## 4. 安装 Helm 与 CUDA

下载 Helm v3.15.3 二进制并移入 PATH，同时配置 CUDA 的 yum 源并安装：

```shell
wget https://get.helm.sh/helm-v3.15.3-linux-amd64.tar.gz
tar xf helm-v3.15.3-linux-amd64.tar.gz
mv linux-amd64/helm /usr/bin/

wget https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-rhel7.repo
cp cuda-rhel7.repo /etc/yum.repos.d/

yum clean all

yum makecache
yum install cuda-runtime-12-4 -y
yum install cuda-toolkit -y
```

## 5. gpu-burn 压测验证

编译 gpu-burn 并对 GPU 做 100 秒双精度压测：

```shell
git clone https://github.com/wilicc/gpu-burn.git
cd gpu-burn
make
./gpu_burn -d 100
```
