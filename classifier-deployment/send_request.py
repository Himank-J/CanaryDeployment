import requests
import json

url = "http://a69b8985142d54578a1f905f3af09724-1477477813.ap-south-1.elb.amazonaws.com/v1/models/emotions-classifier:predict"

with open("input.json") as f:
    payload = json.load(f)

headers = {"Host": "emotions-classifier-vit.default.project.emlo", "Content-Type": "application/json"}

response = requests.request("POST", url, headers=headers, json=payload)

print(response.headers)
print(response.status_code)
print(response.json())