---
title: "elasticsearch 7.x搭建集群和重启"
date: "2021-04-19 14:28:28"
category: "集群"
source: "https://blog.51cto.com/hequan/2717713"
---
> **内容介绍**
>
> 演示在 CentOS 7 上手工搭建 Elasticsearch 7.3 三节点集群：安装 OpenJDK 11、调整 `vm.max_map_count`、配置 `elasticsearch.yml` 中的集群名、节点角色、发现种子与初始主节点，并通过 `_cat/health`、`_cat/nodes` 验证集群状态。后半部分给出安全重启步骤：先关闭分片分配、执行 `synced flush`，重启后再恢复自动分片。

> **技术备注**
>
> 示例基于 Elasticsearch 7.3.2 与 CentOS 7 编写；CentOS 7 已于 2024 年 6 月 30 日 EOL，Elasticsearch 7.x 也已停止更新，建议生产环境迁移至 Rocky Linux/AlmaLinux 并升级到 Elasticsearch 8.x（需处理安全认证与 TLS 默认开启的变化）。原文配置片段缺少 `cluster.name` 与 `node.name` 的键名，且 `discovery.zen.*` 参数在 7.x 中已被 `discovery.seed_hosts` / `cluster.initial_master_nodes` 取代。

---

```shell
yum install java-11-openjdk-devel.x86_64

echo vm.max_map_count=655360 >> /etc/sysctl.conf
sysctl -p

wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.3.2-linux-x86_64.tar.gz
tar -zxvf elasticsearch-7.3.2.tar.gz
mv elasticsearch-7.3.2 /data
adduser es
chown -R es /data/elasticsearch-7.3.2

bin/elasticsearch

cluster.name: es-cluster
node.name: test1
node.master: true
node.data: true
http.port: 9200
transport.tcp.port: 9300
transport.tcp.compress: true
path.data: /data/es
path.logs: /data/logs
network.host: 192.168.100.101

discovery.zen.fd.ping_timeout: 1m
discovery.zen.fd.ping_retries: 5
discovery.seed_hosts: ["192.168.100.101", "192.168.100.102", "192.168.100.103"]
cluster.initial_master_nodes: ["test1", "test2","test3"]

http.cors.enabled: true
http.cors.allow-origin: "*"
```

```shell
curl -XGET http://192.168.100.101:9200/_cat/health?v

curl -XGET http://192.168.100.103:9200/_cat/nodes?v

curl -XGET http://192.168.100.101:9200/_cat/indices?v

curl -XPUT http://192.168.100.102:9200/cmdb/user/4 -d "{\"email\":\"test@\",\"name\":\"test\",\"username\":\"@test\"}"  -H "Content-Type: application/json"

curl -XGET http://192.168.100.101:9200/cmdb/user/1
```

```shell
一：关闭自动分片，即使新建index也无法分配数据分片。
curl -XPUT http://192.168.100.102:9200/_cluster/settings -d '{
  "transient" : {
    "cluster.routing.allocation.enable" : "none"
  }
}'   -H "Content-Type: application/json"

二：同步刷新
curl -X POST "192.168.100.102:9200/_flush/synced?pretty"

三：查看状态
curl http://192.168.100.102:9200/_cluster/settings?pretty

状态为: yellow
curl -XGET http://192.168.100.103:9200/_cat/health?v

curl -XGET http://192.168.100.103:9200/_cat/nodes?v

重启

四：启动 自动分片
curl -XPUT http://192.168.100.102:9200/_cluster/settings -d '{
  "transient" : {
    "cluster.routing.allocation.enable" : "all"
  }
}'   -H "Content-Type: application/json"

状态为: green
curl -XGET http://192.168.100.101:9200/_cat/health?v
```
