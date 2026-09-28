---
title: "elasticsearch 7.x搭建集群和重启"
date: "2021-04-19 14:28:28"
category: "集群"
source: "https://blog.51cto.com/hequan/2717713"
---
> **内容介绍**
>
> 本文是服务器集群与高可用架构实践,记录了「elasticsearch 7.x搭建集群和重启」的相关内容。

> **技术备注**
>
> CentOS 7 已于 2024 年 6 月 30 日停止维护(EOL),建议迁移至 Rocky Linux 9 / AlmaLinux 9 或国产 openEuler。

---

```shellyum install java-11-openjdk-devel.x86_64

echo vm.max_map_count=655360 >> /etc/sysctl.conf
sysctl -p

wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.3.2-linux-x86_64.tar.gz
tar -zxvf elasticsearch-7.3.2.tar.gz
mv elasticsearch-7.3.2 /data
adduser es
chown -R es /data/elasticsearch-7.3.2

bin/elasticsearch

: es-cluster
: test1
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
```shell

```shellcurl -XGET http://192.168.100.101:9200/_cat/health?v

curl -XGET http://192.168.100.103:9200/_cat/nodes?v

curl -XGET http://192.168.100.101:9200/_cat/indices?v

curl -XPUT http://192.168.100.102:9200/cmdb/user/4 -d "{\"email\":\"test@\",\"name\":\"test\",\"username\":\"@test\"}"  -H "Content-Type: application/json"

curl -XGET http://192.168.100.101:9200/cmdb/user/1
```

```shell一：关闭自动分片，即使新建index也无法分配数据分片。
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
