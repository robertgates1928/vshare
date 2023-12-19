import azure.functions as func
import json
from azure.cosmos import CosmosClient, PartitionKey
import logging
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import uuid
import requests
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.questionanswering import models as qna

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


DB_ENDPOINT = 'https://vshare.documents.azure.com:443/' 
DB_KEY = '4D2LAaskmdelMqQ1j6XKgtKRPRvvhIXuFJAHaBPOrxCJW786vU54C4A4ubYuupuWMH0FPQiM4JSSACDbslqQnA=='
DB_NAME = 'vshare'
client = CosmosClient(DB_ENDPOINT, DB_KEY)
database = client.get_database_client(DB_NAME)
container_user = database.get_container_client('users')
container_item = database.get_container_client('items')

@app.route(route="login")
def login(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('login function processed a request.')
    name = None
    pwd = None
    
    name = req.form["name"]
    pwd = req.form["pwd"]

    query = "SELECT * FROM c WHERE c.id=@username"
    users = list(container_user.query_items(
        query=query,
        parameters=[{"name":"@username","value":name}],
        enable_cross_partition_query=True
    ))

    if not users:
        return func.HttpResponse(
            json.dumps({"result": False, "msg": "Username or password incorrect"}),
            status_code=200
        )
    
    user = users[0]
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

@app.route(route="getimgs", auth_level=func.AuthLevel.ANONYMOUS)
def getimgs(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('getimgs processed a request.')
    # query = "SELECT * FROM c order by c.user_name desc"
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
    logging.info('qam function processed a request.')
    qam_endpoint = "https://vshareai.cognitiveservices.azure.com/"
    qam_credential = AzureKeyCredential("f1bf3bef64184095a4b9e8da304935db")

    question = req.form["qes"]
    
    
    # print(u"Q: {}".format(input.question))
    # print(u"A: {}".format(best_answer.answer))
    # print("Confidence Score: {}".format(output.answers[0].confidence))

    if question:
        client = QuestionAnsweringClient(qam_endpoint, qam_credential)
        with client:
            # question="How long does it takes to charge a surface?"
            input = qna.AnswersFromTextOptions(
                question=question,
                text_documents=[
                    "Power and charging. It takes two to four hours to charge the Surface Pro 4 battery fully from an empty state. " +
                    "It can take longer if you're using your Surface for power-intensive activities like gaming or video streaming while you're charging it.",
                    "You can use the USB port on your Surface Pro 4 power supply to charge other devices, like a phone, while your Surface charges. " +
                    "The USB port on the power supply is only for charging, not for data transfer. If you want to use a USB device, plug it into the USB port on your Surface.",
                ]
            )
            output = client.get_answers_from_text(input)

        best_answer = ''
        if output.answers:
            maxconf = 0
            for a in output.answers:
                if a.confidence > maxconf:
                    maxconf = a.confidence
                    best_answer = a.answer

        trs = getTranslate(best_answer)
        trs =trs[0]['translations']
        tmsg = ''
        for t in trs:
            tmsg += t['text']+'<br>'

        return func.HttpResponse(
            json.dumps({"result": True, "msg": tmsg}),
                status_code=200
        )
    else:
        return func.HttpResponse(
             json.dumps({"result": False, "msg": 'question_empty'}),
                status_code=200
        )

def getTranslate(msgstr):
    key_var_name = '828426c3ce3542e49982afa6249f7871'
    subscription_key = key_var_name

    region_var_name = 'eastus'
    region = region_var_name

    endpoint_var_name = 'https://api.cognitive.microsofttranslator.com/'
    endpoint = endpoint_var_name

    # If you encounter any issues with the base_url or path, make sure
    # that you are using the latest endpoint: https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate
    path = '/translate?api-version=3.0'
    params = '&from=en&to=de&to=it&to=zh-Hans'
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text' : msgstr
    }]
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()

    return response