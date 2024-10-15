# Workshop Dev env Setup

```
ssh workshop@20.82.2.134
```
>password: workshop

<br>

### create your resources

||||
|--|--|--|
|file|desc|note|
|.env|執行app使用的環境變數||
|contentEvent.json|couchbase eventing json|for exercise_pdf|
|fileEvent.json|couchbase eventing json|for exercise_pdf|
|fts-index.json|couchbase full text search json|for exercise_pdf|
|start.sh|建立docker container script||

<br>

```
bash create_user.sh $scope $app_port
cd $scope
bash start.sh
docker exec -it $scope-rag bash
```

> $app_port: python app port, 可以選擇5003~5022

> e.g. bash create_user.sh willy 5003