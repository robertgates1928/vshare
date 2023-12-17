import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

DB_ENDPOINT = 'https://vshare.documents.azure.com:443/' 
DB_KEY = '4D2LAaskmdelMqQ1j6XKgtKRPRvvhIXuFJAHaBPOrxCJW786vU54C4A4ubYuupuWMH0FPQiM4JSSACDbslqQnA=='
DB_NAME = 'vshare'
CONTAINER_NAME = 'users'

client = CosmosClient(DB_ENDPOINT, DB_KEY)
database = client.get_database_client(DB_NAME)
container = database.get_container_client(CONTAINER_NAME)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info('Python Cosmos DB trigger function processed a request.')
    name = None
    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        name = req_body.get('name')
        password = req_body.get('pwd')
    if name:
        new_player = {
            "id": name,
            "username": name,
            "password": password  
        }

        container.create_item(body=new_player)
        return func.HttpResponse(f"Hello {name}!")
    else:
        return func.HttpResponse(
                    "Please pass a name on the query string or in the request body",
                    status_code=400
                )