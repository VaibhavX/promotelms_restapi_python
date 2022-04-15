'''Python Code to Authenticate Promote and Get Access Token. \
    Code built inside AWS Cloud9 -- please use AWS credentials if \
        building in local IDE'''

import requests
import json
import boto3
from botocore.errorfactory import ClientError

s3 = boto3.client('s3')

auth_server = "PROMOTE_SERVER"
grant_type="GRANT_TYPE"
client_id = "CLIENT_ID"
username = "USERNAME"
password = "PASS"

files = {
    'grant_type': (None, grant_type),
    'client_id': (None, client_id),
    'username' : (None, username),
    'password': (None, password)
}
auth_target = auth_server + "/oauth/token"

response = requests.post(auth_target, files=files)
assert response.status_code == 201, response.text

json_response = response.json()
access_token = json_response["access_token"]
print(access_token) #Retrieved Access Token

#Adding Access Token Response to Json File on root
json_object = json.dumps(json_response, indent = 4)

with open("FILENAME.json", "w") as outfile:
    outfile.write(json_object)

#Uploading Json File to S3
with open("FILENAME.json", "rb") as f:
    s3.upload_fileobj(f, "S3 BUCKET NAME", "FILENAME.json")
    
#Testing if file successfully uploaded to S3
try:
    s3.head_object(Bucket ='S3 BUCKET NAME',Key ='FILENAME.json')
except ClientError as e:
    if e.response['Error']['Code'] == 404:
        print("Object Does not Exist")
    else:
        print("Error in Load Process")
        raise
else:
    print("Object exists")
