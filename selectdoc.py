from sharedfunctions.print import print_success, print_error, print_bold
from dotenv import load_dotenv
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import os 
from datetime import timedelta

load_dotenv()

auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
cluster = Cluster(f'couchbase://{os.getenv("EE_HOSTNAME")}', ClusterOptions(auth))
cluster.wait_until_ready(timedelta(seconds=5))
print_success("Couchbase setup complete")

try:
    result = cluster.query(
        "SELECT META().id, * FROM data.test.data where type = 'test_embedding' LIMIT 10"
        )

    for row in result.rows():
        print_success(f"Found row: {row}")

except Exception as e:
    print_error(f"An error occurred: {e}")
