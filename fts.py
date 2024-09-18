from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, SearchOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
import couchbase.search as search
from datetime import timedelta
import os 
from dotenv import load_dotenv

load_dotenv()

auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
cluster = Cluster(f'couchbase://{os.getenv("EE_HOSTNAME")}', ClusterOptions(auth))
cluster.wait_until_ready(timedelta(seconds=5))
print("Couchbase setup complete")


try:

    result = cluster.search_query('data.test.test-fts', search.QueryStringQuery('test*'), SearchOptions(limit=13, fields=['name', 'type', 'content']))

    for row in result.rows():
        print(f'Found row: {row}')

    print(f'Reported total rows: {result.metadata().metrics().total_rows()}')

except CouchbaseException as ex:
    import traceback
    traceback.print_exc()