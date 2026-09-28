---
title: "nvidia-docker + helm+cuda+gpu_burn"
date: "2024-08-01 17:51:49"
category: "集群"
source: "https://blog.51cto.com/hequan/11633590"
---
> **内容介绍**
>
> 本文是服务器集群与高可用架构实践,记录了「nvidia-docker + helm+cuda+gpu_burn」的相关内容。

> **技术备注**
>
> Docker 与 Kubernetes 生态演进较快,新版 K8s 默认运行时为 containerd,请注意适配。

---

```shell
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo |  tee /etc/yum.repos.d/nvidia-docker.repo

yum install -y nvidia-container-toolkit
yum install -y nvidia-docker2
yum install  nvidia-container-runtime -y

vim  /etc/docker/daemon.json
{
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}

systemctl daemon-reload && systemctl restart docker

vim   /etc/containerd/config.toml

[plugins."io.containerd.grpc.v1.cri"]
  [plugins."io.containerd.grpc.v1.cri".containerd]
    default_runtime_name = "nvidia-container-runtime" # 修改为nvidia-container-runtime
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
    runtime_type = "io.containerd.runc.v2" # 修改为io.containerd.runc.v2
  # 新增以下
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia-container-runtime]
    runtime_type = "io.containerd.runtime.v1.linux"
    runtime_engine = "/usr/bin/nvidia-container-runtime"

systemctl daemon-reload && systemctl restart containerd

wget  https://get.helm.sh/helm-v3.15.3-linux-amd64.tar.gz
tar xf 
mv helm  /usr/bin/

wget https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-rhel7.repo
cp cuda-rhel7.repo /etc/yum.repos.d/

yum clean all

yum makecache
yum install cuda-runtime-12-4  -y
yum install cuda-toolkit -y

git clone https:///wilicc/gpu-burn.git
cd gpu-burn
make
./gpu_burn -d 100
```
