import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey
import logging
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

DB_ENDPOINT = 'https://vshare.documents.azure.com:443/' 
DB_KEY = '4D2LAaskmdelMqQ1j6XKgtKRPRvvhIXuFJAHaBPOrxCJW786vU54C4A4ubYuupuWMH0FPQiM4JSSACDbslqQnA=='
DB_NAME = 'vshare'
CONTAINER_NAME = 'users'

client = CosmosClient(DB_ENDPOINT, DB_KEY)
database = client.get_database_client(DB_NAME)
container = database.get_container_client(CONTAINER_NAME)

@app.route(route="login")
def login(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info('Python Cosmos DB trigger function processed a request.')
    name = None
    pwd = None
    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        name = req_body.get('name')
        pwd = req_body.get('pwd')
    if name:
        new_player = {
            "id": name,
            "username": name,
            "password": pwd  
        }

        container.create_item(body=new_player)
        return func.HttpResponse(f"Hello {name}!")
    else:
        return func.HttpResponse(
                    "Please pass a name on the query string or in the request body",
                    status_code=400
                )

@app.route(route="upload", auth_level=func.AuthLevel.ANONYMOUS)
def upload(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    file = req.files.get('file')
    logging.info('file name:'+file.filename)
    blob_service_client = BlobServiceClient.from_connection_string('DefaultEndpointsProtocol=https;AccountName=vsharetest;AccountKey=b4SGnD03D66yiFKDYpJ8ylyLOioocHAiP8EEQSLYo1rO1EATeDcFT3rzLkCuJZk2rowYQi3noi0C+AStGUL/oQ==;EndpointSuffix=core.windows.net')
    container_client = blob_service_client.get_container_client('vshareblob')
    blob_client = container_client.get_blob_client(file.filename)
    blob_client.upload_blob(file)
    url = "https://vsharetest.blob.core.windows.net/vshareblob/"+file.filename    
    ks = "?st=2023-12-18T07:07:45Z&si=read&spr=https&sv=2022-11-02&sr=c&sig=xvA5P2UfuXbhPgWImvxBUYLJMOoc9xTGMHvhQaY3xDA%3D"
    return func.HttpResponse(f"<html>Successfully uploaded {file.filename}!<img src='"+url+ks+"' /></html>")