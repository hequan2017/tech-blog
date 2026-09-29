---
title: "Setting Up and Safely Restarting an Elasticsearch 7.x Cluster"
date: "2021-04-19 14:28:28"
category: "cluster"
source: "https://blog.51cto.com/hequan/2717713"
lang: "en"
---
> **About this post**
>
> Demonstrates how to manually set up a three-node Elasticsearch 7.3 cluster on CentOS 7: installing OpenJDK 11, tuning `vm.max_map_count`, and configuring the cluster name, node roles, discovery seeds, and initial master nodes in `elasticsearch.yml`, then verifying the cluster status via `_cat/health` and `_cat/nodes`. The second half provides safe restart steps: disable shard allocation first, run a `synced flush`, and re-enable automatic allocation after the restart.

> **Technical notes**
>
> The examples were written against Elasticsearch 7.3.2 and CentOS 7; CentOS 7 reached EOL on June 30, 2024, and Elasticsearch 7.x is no longer updated either. For production, consider migrating to Rocky Linux/AlmaLinux and upgrading to Elasticsearch 8.x (which requires handling the changes of security authentication and TLS being enabled by default). The original configuration snippet lacks the keys for `cluster.name` and `node.name`, and the `discovery.zen.*` parameters have been replaced by `discovery.seed_hosts` / `cluster.initial_master_nodes` in 7.x.

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
Step 1: Disable automatic shard allocation, so that even newly created indices cannot have data shards allocated.
curl -XPUT http://192.168.100.102:9200/_cluster/settings -d '{
  "transient" : {
    "cluster.routing.allocation.enable" : "none"
  }
}'   -H "Content-Type: application/json"

Step 2: Synced flush
curl -X POST "192.168.100.102:9200/_flush/synced?pretty"

Step 3: Check the status
curl http://192.168.100.102:9200/_cluster/settings?pretty

Status: yellow
curl -XGET http://192.168.100.103:9200/_cat/health?v

curl -XGET http://192.168.100.103:9200/_cat/nodes?v

Restart

Step 4: Re-enable automatic shard allocation
curl -XPUT http://192.168.100.102:9200/_cluster/settings -d '{
  "transient" : {
    "cluster.routing.allocation.enable" : "all"
  }
}'   -H "Content-Type: application/json"

Status: green
curl -XGET http://192.168.100.101:9200/_cat/health?v
```
