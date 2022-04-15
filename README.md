# promotelms_restapi_python
REST API Operations in Python for PROMOTE LMS

Files
------
1. promote_auth.py - Authenticates Credentials and Gets Access Token [RUN FIRST]
2. promote_appserver.py - Performs Operations to Automate Adding User to Promote DB, Retrieving Program ID, Adding User to Program and Sending Invitation to users to access the programs. 

Code in built in AWS Cloud9, hence the AWS Credentials are already authenticated. 
Both these code interact with AWS S3 to store and access processed dataframes (csv files), token response (json).

Final Step to create Scheduled Automation
Both these codes are deployed as AWS Lambda Functions and scheduled using AWS CloudWatch

@Author === Vaibhav Vishal
