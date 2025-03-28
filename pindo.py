
# python

import requests

token='your-token'
headers = {'Authorization': 'Bearer ' + token}
# For single sms
data = {'to' : '+250781234567', 'text' : 'Hello from Pindo', 'sender' : 'Pindo'}
url = 'https://api.pindo.io/v1/sms/'

# For bulk sms
data = {'recipients' : [{'phonenumber': '+250781234567', 'name': 'Remy Muhire'}], 'text' : 'Hello @contact.name, Welcome to Pindo', 'sender' : 'Pindo'}
url = 'https://api.pindo.io/v1/sms/bulk'

response = requests.post(url, json=data, headers=headers)
print(response)
print(response.json())
