import requests
import json

url = "http://a846eaa6a708b4d33bf9da122f4d2502-1243763753.ap-south-1.elb.amazonaws.com/v1/models/hand-gestures-classifier:predict"

with open("input.json") as f:
    payload = json.load(f)

headers = {"Host": "classifier-vit.default.project.emlo", "Content-Type": "application/json"}

response = requests.request("POST", url, headers=headers, json=payload)

print(response.headers)
print(response.status_code)
print(response.json())