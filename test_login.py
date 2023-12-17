import requests


LOCAL_DEV_URL="http://localhost:7071/api/http_trigger"
PUBLIC_URL="https://vsharetest.azurewebsites.net/api/http_trigger"
TEST_URL = PUBLIC_URL
input_user = '{"name": "testname","pwd": "pwd111" }'

response = requests.get(TEST_URL,data=input_user)

dict_response = response.raw  

print(dict_response)

