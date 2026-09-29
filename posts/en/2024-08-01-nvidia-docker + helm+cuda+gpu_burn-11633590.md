---
title: "nvidia-docker + helm + cuda + gpu_burn"
date: "2024-08-01 17:51:49"
category: "cluster"
source: "https://blog.51cto.com/hequan/11633590"
lang: "en"
---
> **About this post**
>
> This post records the process of setting up a Kubernetes GPU node environment: first install
> nvidia-container-toolkit and nvidia-docker2, and configure Docker and
> containerd to use the NVIDIA runtime; then install the Helm binary and the CUDA 12.4
> toolchain; finally, use gpu-burn to run a 100-second double-precision stress test on the GPU for verification.

> **Technical notes**
>
> The nvidia-docker project has been renamed NVIDIA Container Toolkit; nvidia-docker2
> is the legacy package name, and new environments only need to install
> nvidia-container-toolkit. The nvidia-docker.repo source URL used in this post is now
> deprecated. gpu-burn is an open-source GPU stress-test tool;
> `-d` means double precision and `100` is the duration in seconds; this post only installs the Helm binary,
> with no chart deployment involved. Newer Kubernetes versions use containerd as the default runtime, so pay attention to the configuration.

---

## 1. Install the NVIDIA Container Runtime

First add the nvidia-docker yum repository for your system version, then install the related packages:

```shell
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | tee /etc/yum.repos.d/nvidia-docker.repo

yum install -y nvidia-container-toolkit
yum install -y nvidia-docker2
yum install nvidia-container-runtime -y
```

## 2. Configure Docker to Use the NVIDIA Runtime

Edit `/etc/docker/daemon.json` to register a runtime named `nvidia`:

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

Reload the configuration and restart Docker:

```shell
systemctl daemon-reload && systemctl restart docker
```

## 3. Configure the containerd Default Runtime

Edit `/etc/containerd/config.toml` and change the default runtime to nvidia-container-runtime:

```toml
[plugins."io.containerd.grpc.v1.cri"]
  [plugins."io.containerd.grpc.v1.cri".containerd]
    default_runtime_name = "nvidia-container-runtime" # change to nvidia-container-runtime
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
    runtime_type = "io.containerd.runc.v2" # change to io.containerd.runc.v2
  # add the following
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia-container-runtime]
    runtime_type = "io.containerd.runtime.v1.linux"
    runtime_engine = "/usr/bin/nvidia-container-runtime"
```

Reload the configuration and restart containerd:

```shell
systemctl daemon-reload && systemctl restart containerd
```

## 4. Install Helm and CUDA

Download the Helm v3.15.3 binary and move it into PATH; at the same time, set up the CUDA yum repository and install:

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

## 5. gpu-burn Stress Test Verification

Compile gpu-burn and run a 100-second double-precision stress test on the GPU:

```shell
git clone https://github.com/wilicc/gpu-burn.git
cd gpu-burn
make
./gpu_burn -d 100
```
