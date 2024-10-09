# exercise pdf

## prepare data

- upload pdf
- pdf partition
- tex/table/image summarize 
- content embedding

![ex_2_flow](/static/images/exercise/ex_2_flow.png)

<br>

**run server**
```
python app.py
```

http://localhost:5002/

**upload pdf**
|||
|--|--|
|![ex_2_upload1](/static/images/exercise/ex_2_upload1.png)|![ex_2_upload2](/static/images/exercise/ex_2_upload2.png)|


> 執行後, 將檔案儲存, 並將metadata存入coucbase後結束 <br>
> 需要依序新增
> 1. parse_document api, 執行pdf partition
> 2. fileEvent, 當meta更新時, 觸發parse_document api
> 3. embedding api, 執行embedding
> 4. contentEvent, parse_document結束後觸發embedding
> 5. full-text search index


## exercise 1 - parse_document api

**app.py**
將partition_document註解拿掉
```
@app.route('/parse_document', methods=['POST'])
def parse_document():
    data = request.get_json()

    id = data.get("id")
    path = data.get("path")

    # partition_document(id, path)

    return jsonify({
        "message": "File parsed"
    }), 200
```

**查看parsedoc.py**
> 範例使用unstructured.partition.pdf, 將pdf分解為各種元素，例如段落、標題、列表、表格等
```
from unstructured.partition.pdf import partition_pdf
...
...

def partition_document(id, path):
    # Extract images, tables, and chunk text
    print_bold("partition_pdf...")
    raw_pdf_elements = partition_pdf(
        filename=path,
        extract_images_in_pdf=True,
        infer_table_structure=True,
        chunking_strategy="by_title",
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        image_output_dir_path=path + "/.."
    )
    print_bold(f"got {len(raw_pdf_elements)} elements")

    ...
    ...
    insert_into_couchbase(texts,  "text")
    insert_into_couchbase(images, "image")
    insert_into_couchbase(tables, "table")
```

## exercise 2 - add metadata eventing 
### 1. add function
![ex_2_1_add](/static/images/exercise/ex_2_1_add.png)

- Listen To Location
- Eventing Storage
- Deployment Feed Boundary (Everthing/From now)

**Bindings**
- bucket alias:
設定完後可以直接在js取得該bucket, 並執行db操作
- URL alias: 執行curl時的url

#### javascript
> 資料更新時, 當檔案格式為pdf時才執行ParseDoc
```
function OnUpdate(doc, meta) {

    let new_doc = doc
    let eventing = new_doc.eventing ?? {}
    
    if ( eventing.success ) {
        return
    }
    
    if ( doc.type == 'application/pdf' ) {
        EventingLog(new_doc, meta, {...eventing, 'success': true, 'message': 'processing'})
        
        let parse_result = ParseDoc(doc, meta)
        eventing = {...eventing, ...parse_result}
    } else {
        eventing.success = true
        eventing.message = 'skip'
    }
    
    EventingLog(new_doc, meta, eventing)
    
    log("processed", meta.id);
}
```
<br>

> 紀錄eventing時間
```
function EventingLog(new_doc, meta, eventing) {
    log(eventing)
    eventing.time = new Date()
    new_doc.eventing = eventing
    self[meta.id] = new_doc
}
```
<br>

> 呼叫api執行parse_document
```
function ParseDoc(doc, meta) {
    
    let request = {
        path: '/parse_document',
        params: {},
        body: {
            'id': meta.id,
            'path': doc.path
        }
    }
    
    let result = {
        'success': true
    }
        
    try {
        let response = curl('POST', end_point, request);
    
        if (response.status != 200) {
            log("Failed to create embedding", response.status, response.body)
            result.success = false
            result.error = response.body
        }
    } catch (e) {
        log(e)
        result.success = false
        result.error = e
    }
    
    
    return result;
}
```

<br>

> 預設的OnDelete
```
function OnDelete(meta, options) {
    log("Doc deleted/expired", meta.id);
}
```

### 2. deploy

|||
|--|--|
|![ex_2_1_deploy](/static/images/exercise/ex_2_1_deploy.png)|![ex_2_1_deploy_done](/static/images/exercise/ex_2_1_deploy_done.png)|


### 3. check data.uat collection meta and data

> 如果Deployment Feed Boundary為From now, 可以手動update meta以觸發event

![ex_2_1_meta](/static/images/exercise/ex_2_1_meta.png)
![ex_2_1_data](/static/images/exercise/ex_2_1_data.png)
![ex_2_1_log](/static/images/exercise/ex_2_1_log.png)


## exercise 3 - embedding api
**查看app.py**
```
@app.route('/embedding', methods=['GET'])
def embedding():
    doc_id = request.args.get('id')

    do_embedding(doc_id)

    return doc_id
```

## exercise 4 - import contentEvent

**import**

multi-model-rag/static/eventing/contentEvent.json
-> 修改url

|||
|--|--|
|![ex_2_4_import](/static/images/exercise/ex_2_4_import.png)|![ex_2_4_import_url](/static/images/exercise/ex_2_4_import_url.png)|

**deploy**
![ex_2_4_deploy](/static/images/exercise/ex_2_4_deploy.png)

**check data**
![ex_2_4_document](/static/images/exercise/ex_2_4_document.png)


## exercise 5 - import full-text search index

static/fts-index.json

|||
|--|--|
|![ex_2_5_index_add](/static/images/exercise/ex_2_5_index_add.png)|![ex_2_5_index_import](/static/images/exercise/ex_2_5_index_import.png)|
|![ex_2_5_index_import_json](/static/images/exercise/ex_2_5_index_import_json.png)|![ex_2_5_index_import_create](/static/images/exercise/ex_2_5_index_import_create.png)|


## exercise 6 - ask some question

```
In the bar charts for 50% read and 50% write workload, how does Couchbase does in terms of throughput in various clsuter sizes?
```

![question](/static/images/exercise/ex_2_6.png)|