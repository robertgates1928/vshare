import azure.functions as func
import json
from azure.cosmos import CosmosClient, PartitionKey
import logging
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import uuid

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

DB_ENDPOINT = 'https://vshare.documents.azure.com:443/' 
DB_KEY = '4D2LAaskmdelMqQ1j6XKgtKRPRvvhIXuFJAHaBPOrxCJW786vU54C4A4ubYuupuWMH0FPQiM4JSSACDbslqQnA=='
DB_NAME = 'vshare'

client = CosmosClient(DB_ENDPOINT, DB_KEY)
database = client.get_database_client(DB_NAME)
container = database.get_container_client('users')
container_item = database.get_container_client('items')
@app.route(route="login")
def login(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('login function processed a request.')
    name = None
    pwd = None
    
    name = req.form["name"]
    pwd = req.form["pwd"]

    query = "SELECT * FROM c WHERE c.id=@username"
    items = list(container.query_items(
        query=query,
        parameters=[{"name":"@username","value":name}],
        enable_cross_partition_query=True
    ))

    if not items:
        return func.HttpResponse(
            json.dumps({"result": False, "msg": "Username or password incorrect"}),
            status_code=200
        )
    
    user = items[0]
    if user['password'] == pwd:
        return func.HttpResponse(
            json.dumps({"result": True, "msg": "OK"}),
            status_code=200
        )
    else:
        return func.HttpResponse(
             json.dumps({"result": False, "msg": "Username or password incorrect"}),
             status_code=200
        )
    # if name:
    #     new_player = {
    #         "id": name,
    #         "username": name,
    #         "password": pwd  
    #     }

    #     container.create_item(body=new_player)
    #     return func.HttpResponse(f"Hello {name}!")
    # else:
    #     return func.HttpResponse(
    #                 "Please pass a name on the query string or in the request body",
    #                 status_code=400
    #             )

@app.route(route="upload", auth_level=func.AuthLevel.ANONYMOUS)
def upload(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('upload processed a request.')
    name = "test1"
    file = req.files.get('file')
    logging.info('file name:'+file.filename)
    blob_service_client = BlobServiceClient.from_connection_string('DefaultEndpointsProtocol=https;AccountName=vsharetest;AccountKey=b4SGnD03D66yiFKDYpJ8ylyLOioocHAiP8EEQSLYo1rO1EATeDcFT3rzLkCuJZk2rowYQi3noi0C+AStGUL/oQ==;EndpointSuffix=core.windows.net')
    container_client = blob_service_client.get_container_client('vshareblob')
    try:
        blob_client = container_client.get_blob_client(file.filename)
        blob_client.upload_blob(file)
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"result": False, "msg": "img_name_exist"}),
            status_code=200
        )
    new_items = {
        "id": str(uuid.uuid4()),
        "filename": file.filename,
        "user_name": name  
    }

    container_item.create_item(body=new_items)

    # url = "https://vsharetest.blob.core.windows.net/vshareblob/"+file.filename    
    # ks = "?st=2023-12-18T07:07:45Z&si=read&spr=https&sv=2022-11-02&sr=c&sig=xvA5P2UfuXbhPgWImvxBUYLJMOoc9xTGMHvhQaY3xDA%3D"
    # return func.HttpResponse(f"<html>Successfully uploaded {file.filename}!<img src='"+url+ks+"' /></html>")
    return func.HttpResponse(
                json.dumps({"result": True, "msg": "ok"}),
                status_code=200
            )

@app.route(route="list", auth_level=func.AuthLevel.ANONYMOUS)
def list(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('list processed a request.')

    query = "SELECT * FROM c WHERE c.user_name=@username"
    items = list(container_item.query_items(
        query=query,
        parameters=[{"name":"@username","value":'test1'}],
        enable_cross_partition_query=True
    ))

    if items:
        return func.HttpResponse(
            json.dumps(items),
            status_code=200
        )
    else:
        return func.HttpResponse(
             "",
             status_code=200
        )

@app.route(route="qam", auth_level=func.AuthLevel.ANONYMOUS)
def qam(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )