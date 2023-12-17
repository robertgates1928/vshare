import requests


LOCAL_DEV_URL="http://localhost:7071/api/http_trigger"
PUBLIC_URL="https://quiplashtest.azurewebsites.net/api/player/login"
TEST_URL = LOCAL_DEV_URL
input_user = '{"name": "testname","pwd": "pwd111" }'

response = requests.get(TEST_URL,data=input_user)

dict_response = response.content  

print(dict_response)

