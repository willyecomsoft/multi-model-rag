# Couchbase Setup

>user vm or docker

## install

**vm**
```
#!/bin/bash
sudo wget https://packages.couchbase.com/releases/7.6.1/couchbase-server-enterprise-7.6.1-linux.x86_64.rpm
yes | sudo yum install ./couchbase-server*.rpm
sudo systemctl start couchbase-server
```

**docker**
```
docker run -d --name couchbase -p 8091-8096:8091-8096 -p 11210-11211:11210-11211 couchbase:enterprise-7.6.1
```


## init

http://localhost:8091/

**Setup New Cluster**

|       |   |
|  ----  | ----  |
|![couchbase_new_cluster](/static/images/couchbase_new_cluster.png) | ![couchbase_cluster_info](/static/images/couchbase_cluster_info.png)|
|![couchbase_cluster_config](/static/images/couchbase_cluster_config.png)|![couchbase_cluster_terms](/static/images/couchbase_cluster_terms.png)
|

## project setup

> we need to create
> - bucket: data
> - scope: uat
> - collection: meta, data, event

**1. create bucket**

```
curl -X POST http://<EE_HOSTNAME>:8091/pools/default/buckets \
     -u <CB_USERNAME>:<CB_PASSWORD> \
     -d name=data \
     -d ramQuota=3000 \
     -d bucketType=couchbase \
     -d flushEnabled=1
```

same as
![couchbase_create_bucket](/static/images/couchbase_create_bucket.png)

<br>

**2. create "uat" scope under "data" bucket**
```
curl -X POST http://<EE_HOSTNAME>:8091/pools/default/buckets/data/scopes \
     -u <CB_USERNAME>:<CB_PASSWORD> \
     -d name=uat
```

same as
|||
|---|---|
|![couchbase_create_scope1](/static/images/couchbase_create_scope1.png)|![couchbase_create_scope2](/static/images/couchbase_create_scope2.png)|


**3. create collection "data", "meta", "event" under "data" scope**

- meta: store file path and other metadata
- data: store file content, embedding
- event: store event data, used by couchbase

<br>

```
curl -X POST http://<EE_HOSTNAME>:8091/pools/default/buckets/data/scopes/uat/collections \
     -u <CB_USERNAME>:<CB_PASSWORD> \
     -d name=data
```
```
curl -X POST http://<EE_HOSTNAME>:8091/pools/default/buckets/data/scopes/uat/collections \
     -u <CB_USERNAME>:<CB_PASSWORD> \
     -d name=meta
```
```
curl -X POST http://<EE_HOSTNAME>:8091/pools/default/buckets/data/scopes/uat/collections \
     -u <CB_USERNAME>:<CB_PASSWORD> \
     -d name=event
```