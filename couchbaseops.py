from couchbase.vector_search import VectorQuery, VectorSearch
import couchbase.search as search
from couchbase.options import SearchOptions
from dotenv import load_dotenv
import uuid
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from datetime import timedelta
import os 
import couchbase.subdocument as SD
from sharedfunctions.print import print_success
import sys


load_dotenv()


# Couchbase connection
auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
cluster = Cluster(f'couchbase://{os.getenv("EE_HOSTNAME")}', ClusterOptions(auth))
cluster.wait_until_ready(timedelta(seconds=5))
print_success("Couchbase setup complete")


# CRUD operations
def get_doc(bucket, scope, collection, doc_id):
    collection = cluster.bucket(bucket).scope(scope).collection(collection)
    
    try:
        result = collection.get(doc_id)
        return result.content_as[dict]
        
    except Exception as e:
        print("exception:", e, file=sys.stderr)
        
        return None

# Insert a document into a collection
def insert_doc(bucket, scope, collection, doc, doc_id=None): 
    
    cb_collection = cluster.bucket(bucket).scope(scope).collection(collection)
        
    try:
        docid = doc_id if doc_id else str(generate_uuid())
        
        cb_collection.insert(
            docid,
            doc
        )
        
        print(f"Insert {collection} successful: {docid}", file=sys.stderr)
        
        return docid
        
    except Exception as e:
        print("exception:", e, file=sys.stderr)
        
        return None 

# Generate a UUID
def generate_uuid(): 
    return uuid.uuid4()

# Run vector search
def cb_vector_search(bucket_name, scope_name, fts_index, embedding_field, vector, key_context_fields): 
    scope = cluster.bucket(bucket_name).scope(scope_name)
    
    search_req = search.SearchRequest.create(search.MatchNoneQuery()).with_vector_search(
    VectorSearch.from_vector_query(VectorQuery(embedding_field, vector, num_candidates=5)))
    return scope.search(fts_index, search_req, SearchOptions(limit=13, fields=key_context_fields))

# Delete a document
def delete_doc(bucket, scope, collection, doc_id):
    collection = cluster.bucket(bucket).scope(scope).collection(collection)
    
    try:
        collection.remove(doc_id)
        print("Deleted doc with id:", doc_id, file=sys.stderr)
        
    except Exception as e:
        print("exception:", e, file=sys.stderr)
        
        return None
    
# Flush a collection
def flush_collection(bucket_name, scope_name, collection_name):
    try:
        result = cluster.query(
            f"""
                select meta().id 
                from `{bucket_name}`.`{scope_name}`.`{collection_name}`
            """
        )

        for row in result:
            doc_id = row["id"]
            delete_doc(bucket_name, scope_name, collection_name, doc_id)
            
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

    print_success(f"collection `{bucket_name}.{scope_name}.{collection_name}` flushed")
    
 
# subdoc upsert   
def subdocument_upsert(bucket, scope, collection, doc_id, path, value):
    cb_collection = cluster.bucket(bucket).scope(scope).collection(collection)
    
    try:
        cb_collection.mutate_in(doc_id, [SD.upsert(path, value)])
        
        print(f"Subdocument upsert successful for {doc_id}, collection {collection}, path {path} and value {value}", file=sys.stderr)
        
    except Exception as e:
        print("exception with subdoc upsert:", e, file=sys.stderr)
        
        return None
    
# subdoc insert
def subdocument_insert(bucket, scope, collection, doc_id, path, value):
    cb_collection = cluster.bucket(bucket).scope(scope).collection(collection)
    
    try:
        cb_collection.mutate_in(doc_id, [SD.insert(path, value)])
        
        print(f"Subdocument insert successful for {doc_id}, collection {collection}, path {path} and value {value}", file=sys.stderr)
        
    except Exception as e:
        print("exception with subdoc insert:", e, file=sys.stderr)
        
        return None
    
# execute multiple subdoc upserts
def mutliple_subdoc_upsert(bucket, scope, collection, doc_id, path_value_dict):
    cb_collection = cluster.bucket(bucket).scope(scope).collection(collection)
    
    try:
        operations = [SD.upsert(path, value) for path, value in path_value_dict.items()]
        
        cb_collection.mutate_in(doc_id, operations)
        
        print(f"Multiple subdocument upsert successful for {doc_id}, collection {collection}, path_value_dict {path_value_dict}", file=sys.stderr)
        
    except Exception as e:
        print("exception:", e, file=sys.stderr)
        
        return None

# run a query
def run_query(query, execute=False):
    try:
        result = cluster.query(query).execute() if execute else cluster.query(query)
        print(f"Query successful: {query}, result: {result}", file=sys.stderr)
        return result
        
    except Exception as e:
        print("exception:", e, file=sys.stderr)
        
        return None
    
    
