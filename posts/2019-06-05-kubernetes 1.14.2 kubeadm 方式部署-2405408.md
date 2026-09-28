---
title: "kubernetes 1.14.2  kubeadm 方式部署"
date: "2019-06-05 15:43:40"
category: "kubernetes"
source: "https://blog.51cto.com/hequan/2405408"
---
> **内容介绍**
>
> 本文记录用 kubeadm 在 3 台 CentOS 7 主机上部署 Kubernetes 1.14.2 集群的完整过程：关闭防火墙/SELinux/交换分区、配置 hosts 与内核参数、安装 Docker 与 kubelet/kubeadm/kubectl（阿里云镜像源）、提前拉取并 retag gcr.io 镜像解决国内拉取困难，最后 kubeadm init 初始化 master、node 节点 join、部署 flannel 网络插件。

> **技术备注**
>
> Kubernetes 1.14 是 2019 年 3 月发布的版本，早已停止维护。几个重要变化：① K8s 1.24 起移除了 dockershim，默认容器运行时为 containerd，不再需要装 Docker；② 文中阿里云的 kubernetes-el7 yum 源已失效，现官方源为 pkgs.k8s.io（按 minor 版本分仓库）；③ 手动 retag gcr.io 镜像的做法已被 `kubeadm config images pull --image-repository` 或镜像代理取代；④ flannel v0.10 的 CNI 配置写法与现在差异较大，新集群更常用 Calico 或 Cilium；⑤ CentOS 7 已于 2024-06-30 EOL。

---

### kubernetes 1.14.2  kubeadm方式部署

#### 主机

> 192.168.100.111 k8s-master
> 192.168.100.112 k8s-node1
> 192.168.100.113 k8s-node2

#### 基本环境

```shell
systemctl stop firewalld
systemctl disable firewalld
sed -i 's/enforcing/disabled/' /etc/selinux/config
setenforce 0

swapoff -a
vim /etc/fstab

cat /etc/hosts
192.168.100.111 k8s-master
192.168.100.112 k8s-node1
192.168.100.113 k8s-node2

yum install ntpdate -y
ntpdate

yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

yum install docker

systemctl enable docker && systemctl start docker

vim  /etc/sysctl.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-arptables = 1

sysctl -p
```

#### 部署

```shell
cat << EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF

yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
systemctl enable kubelet && systemctl start kubelet

kubeadm config images list  ##查询需要的版本

/kube-apiserver:v1.14.2
/kube-controller-manager:v1.14.2
/kube-scheduler:v1.14.2
/kube-proxy:v1.14.2
/pause:3.1
/etcd:3.3.10
/coredns:1.3.1

## 修改对应的版本号

K8S_VERSION=v1.14.2
ETCD_VERSION=3.3.10
DNS_VERSION=1.3.1
PAUSE_VERSION=3.1
FLANNEL_VERSION=v0.11.0-amd64

# 基本组件
docker pull /google_containers/kube-apiserver-amd64:$K8S_VERSION
docker pull /google_containers/kube-controller-manager-amd64:$K8S_VERSION
docker pull /google_containers/kube-scheduler-amd64:$K8S_VERSION
docker pull /google_containers/kube-proxy-amd64:$K8S_VERSION
docker pull /google_containers/etcd-amd64:$ETCD_VERSION
docker pull /google_containers/pause:$PAUSE_VERSION
docker pull /google_containers/coredns:$DNS_VERSION

# 网络组件

docker pull quay.io/coreos/flannel:$FLANNEL_VERSION

# 修改tag

docker tag /google_containers/kube-apiserver-amd64:$K8S_VERSION /kube-apiserver:$K8S_VERSION
docker tag /google_containers/kube-controller-manager-amd64:$K8S_VERSION /kube-controller-manager:$K8S_VERSION
docker tag /google_containers/kube-scheduler-amd64:$K8S_VERSION /kube-scheduler:$K8S_VERSION
docker tag /google_containers/kube-proxy-amd64:$K8S_VERSION /kube-proxy:$K8S_VERSION
docker tag /google_containers/etcd-amd64:$ETCD_VERSION /etcd:$ETCD_VERSION
docker tag /google_containers/pause:$PAUSE_VERSION /pause:$PAUSE_VERSION
docker tag /google_containers/coredns:$DNS_VERSION /coredns:$DNS_VERSION
```

#### 安装

```shell
kubeadm init --kubernetes-version=1.14.2 --pod-network-cidr=10.244.0.0/16 --apiserver-advertise-address=192.168.100.111

To start using your cluster, you need to run the following as a regular user:

###  master执行
  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

## node 节点执行
kubeadm join 192.168.100.111:6443 --token ws2hxe.zeq9skej2ppjx4ip \
    --discovery-token-ca-cert-hash sha256:abf8f2694f738fcd199aa5bbf99491b0f9248b3750b1df7ba47450bbe9a75f81
```

```shell
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

##三台都执行
mkdir -p /etc/cni/net.d/
cat <<EOF> /etc/cni/net.d/10-flannel.conf
{"name":"cbr0","type":"flannel","delegate": {"isDefaultGateway": true}}
EOF
mkdir /usr/share/oci-umount/oci-umount.d -p
mkdir /run/flannel/
cat <<EOF> /run/flannel/subnet.env
FLANNEL_NETWORK=10.244.0.0/16
FLANNEL_SUBNET=10.244.0.1/24
FLANNEL_MTU=1450
FLANNEL_IPMASQ=true
EOF

## master
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/v0.10.0/Documentation/kube-flannel.yml
```

```shell
kubectl get nodes
NAME         STATUS   ROLES    AGE   VERSION
k8s-master   Ready    master   50m   v1.14.2
k8s-node1    Ready    <none>   46m   v1.14.2
k8s-node2    Ready    <none>   46m   v1.14.2
```

---
