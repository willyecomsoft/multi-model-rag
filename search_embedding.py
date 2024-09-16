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

question = "what is aaabbbccc ?"

embedding = create_embedding(question)

load_dotenv()

auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
cluster = Cluster(f'couchbase://{os.getenv("EE_HOSTNAME")}', ClusterOptions(auth))
cluster.wait_until_ready(timedelta(seconds=5))
print_success("Couchbase setup complete")

try:
    scope = cluster.bucket("data").scope("test")
    
    search_req = search.SearchRequest.create(search.MatchNoneQuery()).with_vector_search(
    VectorSearch.from_vector_query(VectorQuery("embeddings", embedding, num_candidates=5)))
    result = scope.search("www", search_req, SearchOptions(limit=13, fields=['name', 'content', 'type']))
    for row in result.rows():
        print("Found row: {}".format(row))
    print("Reported total rows: {}".format(
        result.metadata().metrics().total_rows()))

except Exception as e:
    print_error(f"An error occurred: {e}")