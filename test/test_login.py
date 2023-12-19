import requests


LOCAL_DEV_URL="http://localhost:7071/api/login"
PUBLIC_URL="https://vsharetest.azurewebsites.net/api/login"
TEST_URL = PUBLIC_URL
input_user = '{"name": "test1","pwd": "1234" }'

response = requests.get(TEST_URL,data=input_user)

dict_response = response.headers  

print(dict_response)

