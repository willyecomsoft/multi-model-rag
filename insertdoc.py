from sharedfunctions.print import print_success, print_error, print_bold
from dotenv import load_dotenv
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import uuid
import os 
from datetime import timedelta

load_dotenv()

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

if __name__ == '__main__':
    
    doc_to_insert = {
        "type": "test_embedding",
        "name": "test",
        "content": "aaabbbccc is the framework for building context-aware reasoning applications"
    }

    insert_doc('data', 'test', 'data', doc_to_insert)