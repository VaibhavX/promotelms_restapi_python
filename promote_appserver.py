'''Python Code to Perform Automated Operations in Promote such as Adding User to DB,\
    Adding User to Program after Retrieving ID and Sending invitations to join program.\
    Code built inside AWS Cloud9 -- please use AWS credentials if \
        building in local IDE'''

import requests
import json
import boto3
import json
import pandas as pd
from botocore.errorfactory import ClientError
from io import StringIO

s3 = boto3.resource('s3')
client = boto3.client('ssm')

s3_object = s3.Bucket('S3 BUCKET NAME').Object('FILENAME.json').get()
file_content = s3_object['Body'].read().decode()

#Converting back to json file and extracting token
json_content = json.loads(file_content)
access_token = json_content['access_token']

client_id = (client.get_parameter(Name="PROMOTE SERVER", WithDecryption= True))['Parameter']['Value']
promote_server = "https://"+client_id+".promoteapp.net"

headers = {
    'Authorization': f"Bearer {access_token}",
    'Accept-Version': 'v3',
}

#Function to Get Current Users on the Application Server
def get_Users(user_data):
    
    
    get_users_url = promote_server + "/api/users"
    response = requests.get(get_users_url, headers=headers)
    assert response.status_code == 200, response.text
    x = response.json()['result'] #This contains all users in the promote user database
    
    for idx in range(len(user_data)):
        print("Checking for User: ", user_data['first_name'][idx], " ", user_data['last_name'][idx])
        chk = 0
        for i in range(len(x)):
            if (x[i]['id'] == user_data['email'][idx]):
                print("Record Found -- Continue to next step")
                chk = 1
                break
        if (chk == 0):
            print("Record not found, user has to be added to Database... Calling Create_user Function")
            new_df = user_data.iloc[idx,]
            create_Users(new_df)
            
    return
    

#Function to Create a New User
def create_Users(df):
    create_users_url = promote_server + "/api/users"
    files={
        'email':(None, df['email']), 
        'first_name' :(None, df['first_name']),
        'last_name' : (None, df['last_name']),
        'organization' :(None, df['organization']),
        'job_title': (None, df['job_title'])
    }
    response = requests.post(create_users_url, headers=headers, files=files)
    assert response.status_code == 201, response.text
    print('User Created', df['first_name'], " ", df['last_name'])


#Function to Update User - Currently not required. 

#Function to Delete User - Currently not required.

#Function to Get list of programs
def get_Programs(df):
    get_program_list = promote_server + "/api/programs"
    response = requests.get(get_program_list, headers = headers)
    assert response.status_code == 200, response.text
    x = response.json()['result'] #Contains all the programs inside Promote
    program_id =[]
    
    for idx in range(len(df)):
        print("Checking Program ID for user", df['first_name'], df['last_name'])
        found = 0
        for i in range(len(x)):
            if x[i]['name'] == df['program_name'][idx]:
                program_id.append(x[i]['id'])
                found = 1
        if(found ==0):
            print("Program not found - manually create the program on the UI")
            program_id.append("")
    return program_id

#Function to Check Users in a Program
def get_Program_User(program_id, email):
    user_list= promote_server+"/api/programs/"+program_id+"/members"
    response = requests.get(user_list, headers=headers)
    assert response.status_code == 200, response.text
    x = response.json()['result']
    for i in range(len(x)):
        print(x[i]['user'])
        if email == x[i]['user']:
            return 1
    print("User not in the Program")
    return 0

#Function to Add User to the Program
#It needs Roles = Learner, Start Date (optional) and End Date (optional)
def add_Program_User(program_id, learner, email):
    found = get_Program_User(program_id, email)
    if found == 1:
        print("User already present in the program")
        return
    add_user_url = promote_server+"/api/programs/"+program_id+"/members"
    
    files = {
        ('user',(None, email)),
        ('roles[]',(None, learner)),
        #'start_at':(None, start_date), #Start Date in YYYY-MM-DD format
        #'end_at':(None, end_date)
    }
    
    response = requests.post(add_user_url, headers=headers, files=files, verify=True)
    assert response.status_code == 201, response.text
    #Success Status Code should be 201 
    print("User added -- Now inviting them to the program")
    invite_user(program_id, email)

#Function to Update a Program Member is for future release

#Function to Delete Users from Program is for Future Use Case

#Function to Invite User to the Program
def invite_user(program_id, email):
    invite_user_url = promote_server+"/api/programs/"+program_id+"/invitations"
    files = {
        'users[]':(None, email)
    }
    responses = requests.post(invite_user_url, headers=headers, files=files)
    assert responses.status_code == 201, responses.text
    #Status Code should be 201
    print("Invitation Sent to User {}".format(email))




def main():
    
    #Read the Registrant List from S3 Server created by the CVENT code
    s3_object2 = s3.Bucket('S3 BUCKET NAME').Object('FILENAME.csv').get() ###Change here to add the correct file name containing user list in the S3 bucket
    file_contents = s3_object2['Body'].read().decode('utf-8')
    user_data = pd.read_csv(StringIO(file_contents))
    
    #Adding User to Promote - This will create user if that user doesn't exist in the system.
    get_Users(user_data)

    #Get Program Id for the Program Name in the dataframe(excel file)
    program_ids = get_Programs(user_data)
    print(program_ids)

    #Add User to the Program
    for idx in range(len(user_data)):
        print("Adding User {} to the Program".format(user_data['email'][idx]))
        add_Program_User(program_ids[idx], 'learner', user_data['email'][idx])

    
    #Sending user the invitation email --- ENABLE THIS IF YOU WANT TO SEND INVITATIONS FOR EVERYONE
    #for idx in range(len(user_data)):
    #    print("Inviting User {} to the Program".format(user_data['email'][idx]))
    #   invite_user(program_ids[idx],user_data['email'][idx])
    print("Program Successfully Executed!")

if(__name__ == '__main__'):
    main()
