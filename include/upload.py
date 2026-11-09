import os
from importlib import import_module
from pathlib import Path

BlobServiceClient = import_module("azure.storage.blob").BlobServiceClient
load_dotenv = import_module("dotenv").load_dotenv

## Parent refers to the folder its under in this case "include". Before we introduced astro, there was no include folder,
## so the parent was civic_pulse_ucp. 
location = Path(__file__).resolve().parent ## says location is Include

project_root = location.parent ## says include is under civic_pulse parent. 

load_dotenv()

ACCOUNT_KEY = os.getenv('UCP_STORAGE_KEY')  
ACCOUNT_NAME = 'civicpulseucp'
CONTAINER_NAME = 'bronze-ucp'

LOCAL_FILE_PATH = project_root / "data" / "urban_service_requests.csv"
BLOB_NAME = "urban_service_requests.csv"

def upload_data():
    try:
        blob_service_client = BlobServiceClient(account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net", credential=ACCOUNT_KEY)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)

        with open(LOCAL_FILE_PATH, "rb") as data:
            blob_client.upload_blob(data, overwrite=True,max_concurrency=4)
        print(f"File {BLOB_NAME} uploaded to Azure Blob Storage successfully.")
    except Exception as e:
        print(f"Error uploading file to Azure Blob Storage: {e}")
    return None

upload_data()