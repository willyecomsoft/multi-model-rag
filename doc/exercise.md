# exercise

## exercise 1 - chat with local ai

**api call**
```
curl --location 'http://localhost:11434/api/generate' \
--header 'Content-Type: application/json' \
--data '{
  "model": "qwen2:0.5b",
  "prompt": "你是一名廣告行銷專業人員，請提供以下文字的廣告詞：咖啡"
}'
```

![api img](/static/images/exercise/ex1_api.png)

**create chat.py**
```
cd ${multi-model-rag-home}
vim chat.py
```

**chat.py**
```
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os 
```

```
load_dotenv()
ollama_base_url = os.getenv("OLLAMA_BASE_URL")

llm = Ollama(
    base_url=ollama_base_url, 
    model='qwen2:0.5b',
)

prompt = ChatPromptTemplate.from_template(
    "你是一名廣告行銷專業人員，請提供以下文字的廣告詞：{message}！"
)

chain = prompt | llm

print(chain.invoke({"message": "咖啡"}))
```

**run**
```
python chat.py
```

![run py](/static/images/exercise/ex1_run_py.png)

<br>

## exercise 2 - create embedding

**api call**
```
curl --location 'http://localhost:11434/api/embed' \
--header 'Content-Type: application/json' \
--data '{
  "model": "qwen2:1.5b",
  "input": "aaabbbccc is the framework for building context-aware reasoning applications"
}'
```

![ex2_api](/static/images/exercise/ex2_api.png)

**create embedding.py**
```
vim embedding.py
```

```
from langchain_community.embeddings import OllamaEmbeddings
from dotenv import load_dotenv
import os 
from openai import OpenAI
```

```
load_dotenv()
ollama_base_url = os.getenv("OLLAMA_BASE_URL")

client_openai = OpenAI()

def create_embedding(text = 'hello'):
    print(text)
    emb = OllamaEmbeddings(
        base_url=ollama_base_url, 
        model='qwen2:1.5b',
    )

    #qwen2同時也是embedding model
    embedding = emb.embed_documents(text)
    return embedding[0]

def create_openai_embeddings(input_message):
    return client_openai.embeddings.create(input = [input_message], model="text-embedding-ada-002").data[0].embedding

if __name__ == '__main__':
    print(create_embedding())
```

**run**
```
python embedding.py
```

<br>

## exercise 3 - insert json doc into couchbase

**create data.test.data**
![ex3_bucket](/static/images/exercise/ex3_bucket.png)

**create insertdoc.py**
```
vim insertdoc.py
```

```
from sharedfunctions.print import print_success, print_error, print_bold
from dotenv import load_dotenv
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import uuid
import os 
from datetime import timedelta

load_dotenv()
```

```
def insert_doc(bucket, scope, collection, doc_to_insert, doc_id=None): 

    auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
    cluster = Cluster(f'couchbase://{os.getenv("EE_HOSTNAME")}', ClusterOptions(auth))
    cluster.wait_until_ready(timedelta(seconds=5))
    print_success("Couchbase setup complete")
            
    try:

        docid = doc_id if doc_id else str(uuid.uuid4())

        cb_collection = cluster.bucket(bucket).scope(scope).collection(collection)
        
        cb_collection.insert(
            docid,
            doc_to_insert
        )
        
        print_bold(f"Insert {collection} successful: {docid}")
            
    except Exception as e:
        print_error(f"An error occurred: {e}")
```
```
if __name__ == '__main__':
    doc_to_insert = {
        "type": "test_embedding",
        "name": "test",
        "content": "aaabbbccc is the framework for building context-aware reasoning applications"
    }

    insert_doc('data', 'test', 'data', doc_to_insert)
```

**run**
```
python insertdoc.py
```

![ex3_run](/static/images/exercise/ex3_run.png)


## exercise 4 - Select doc from couchbase

**use sql++**
```
SELECT META().id, * FROM data.test.data where type = 'test_embedding' LIMIT 10
```
![ex4_sql](/static/images/exercise/ex4_sql.png)

**use sdk**
```
vim selectdoc.py
```

```
from sharedfunctions.print import print_success, print_error, print_bold
from dotenv import load_dotenv
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import os 
from datetime import timedelta
```
```
load_dotenv()

auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
cluster = Cluster(f'couchbase://{os.getenv("EE_HOSTNAME")}', ClusterOptions(auth))
cluster.wait_until_ready(timedelta(seconds=5))
print_success("Couchbase setup complete")
```
```
try:
    result = cluster.query(
        "SELECT META().id, * FROM data.data.data where type = 'test_embedding' LIMIT 10"
        )

    for row in result.rows():
        print_success(f"Found row: {row}")

except Exception as e:
    print_error(f"An error occurred: {e}")
```

**run**
```
python selectdoc.py
```
![ex4_run](/static/images/exercise/ex4_run.png)

## exercise 5 - store data with embedding

>previous insertdoc.py and embedding is required

**create store_embedding.py**
```
vim store_embedding.py
```

```
from embedding import create_embedding
from insertdoc import insert_doc
```

```
text = 'aaabbbccc is the framework for building context-aware reasoning applications'
embedding = create_embedding(text)

doc = {
    "type": "test_embedding",
    "name": "test",
    "content": text,
    "embeddings": embedding
}

insert_doc('data', 'test', 'data', doc)
```

**run**
```
python store_embedding.py
```

|||
|---|---|
|![ex5_doc](/static/images/exercise/ex5_doc.png)|![ex5_detail](/static/images/exercise/ex5_detail.png)|


## exercise 6 - vector search & full-text search

### 6.1. full-text search
**create index**
>Search -> QUICK INDEX

![ex6_quick_index](/static/images/exercise/ex6_quick_index.png)

<br>

Index Name: **test-fts**<br>
Keyspace: data.test.data

![ex6_fts1](/static/images/exercise/ex6_fts1.png)

>select filed -> checkbox -> ADD

![ex6_fts_f1](/static/images/exercise/ex6_fts_f1.png)
|||
|---|---|
|![ex6_fts_f2](/static/images/exercise/ex6_fts_f2.png)|![ex6_fts_f3](/static/images/exercise/ex6_fts_f3.png)|

embedding

![ex6_fts_emb](/static/images/exercise/ex6_fts_emb.png)


result
![ex6_fts_create](/static/images/exercise/ex6_fts_create.png)
![ex6_fts_create_result](/static/images/exercise/ex6_fts_create_result.png)

<br>

**basic search**
![ex6_fts_search1](/static/images/exercise/ex6_fts_search1.png)
![ex6_fts_search2](/static/images/exercise/ex6_fts_search2.png)

**search with sdk**
```
vim fts.py
```

```
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, SearchOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
import couchbase.search as search
from datetime import timedelta
import os 
from dotenv import load_dotenv
```

```
load_dotenv()

auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
cluster = Cluster(f'couchbase://{os.getenv("EE_HOSTNAME")}', ClusterOptions(auth))
cluster.wait_until_ready(timedelta(seconds=5))
print("Couchbase setup complete")
```

```
try:

    result = cluster.search_query('data.test.test-fts', search.QueryStringQuery('test*'), SearchOptions(limit=13, fields=['name', 'type', 'content']))

    for row in result.rows():
        print(f'Found row: {row}')

    print(f'Reported total rows: {result.metadata().metrics().total_rows()}')

except CouchbaseException as ex:
    import traceback
    traceback.print_exc()
```

**run**
```
python fts.py
```

![ex6_fts_run](/static/images/exercise/ex6_fts_run.png)


### 6.2. search embedding

```
vim search_embedding.py
```

```
from embedding import create_embedding
from sharedfunctions.print import print_success, print_error, print_bold
from dotenv import load_dotenv
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import os 
from datetime import timedelta
import couchbase.search as search
from couchbase.vector_search import VectorQuery, VectorSearch
from couchbase.options import SearchOptions

```

```
load_dotenv()

auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
cluster = Cluster(f'couchbase://{os.getenv("EE_HOSTNAME")}', ClusterOptions(auth))
cluster.wait_until_ready(timedelta(seconds=5))
print_success("Couchbase setup complete")
```

**embedding question**
```
question = "what is aaabbbccc ?"

embedding = create_embedding(question)
```

```
try:
    scope = cluster.bucket("data").scope("test")
    
    search_req = search.SearchRequest.create(search.MatchNoneQuery()).with_vector_search(
    VectorSearch.from_vector_query(VectorQuery("embeddings", embedding, num_candidates=5)))
    result = scope.search("test-fts", search_req, SearchOptions(limit=13, fields=['name', 'content', 'type']))
    for row in result.rows():
        print("Found row: {}".format(row))
    print("Reported total rows: {}".format(
        result.metadata().metrics().total_rows()))

except Exception as e:
    print_error(f"An error occurred: {e}")
```

**run**
```
python search_embedding.py
```
![ex6.2_run](/static/images/exercise/ex6.2_run.png)