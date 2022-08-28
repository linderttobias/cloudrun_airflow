import os
import click
from google.cloud import storage

secret_file = os.environ["SECRET_FILE"]

@click.command()
@click.option(
    "--bucket_name",
    help="bucket name",
    prompt=False,
)
def find_matching_files(bucket_name):
    # Service Account linked to the Job will authenticate
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)
    for blob in blobs:
        if str(blob.name) == secret_file:
            print("MATCH")
        else:
            print("NO MATCH")

if __name__ == "__main__":
    find_matching_files()



