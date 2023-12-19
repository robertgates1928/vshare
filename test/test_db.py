import requests
import azure.functions as func
import json
from azure.cosmos import CosmosClient, PartitionKey
import logging
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import uuid

DB_ENDPOINT = 'https://vshare.documents.azure.com:443/' 
DB_KEY = '4D2LAaskmdelMqQ1j6XKgtKRPRvvhIXuFJAHaBPOrxCJW786vU54C4A4ubYuupuWMH0FPQiM4JSSACDbslqQnA=='
DB_NAME = 'vshare'

client = CosmosClient(DB_ENDPOINT, DB_KEY)
database = client.get_database_client(DB_NAME)
container_item = database.get_container_client('items')

# query = "SELECT * FROM c order by c.user_name desc"
query = "SELECT * FROM c WHERE c.user_name=@username"
items = list(container_item.query_items(
    query=query,
    parameters=[{"name":"@username","value":'test1'}],
    enable_cross_partition_query=True
))

if items:
    print('ok')
    
else:
    print('no')

