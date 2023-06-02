#!/usr/bin/env python
# coding: utf-8

# In[4]:


import boto3
import pandas as pd
from config import aws_access_key_id, aws_secret_access_key

client = boto3.client('s3',
                     aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

buckets = client.list_buckets()
bucket_frame = pd.DataFrame(buckets['Buckets'])
bucket_name = bucket_frame.loc[bucket_frame['Name'].str.contains('tinyflixtutorial', case = False)]['Name'].values[0]

objects = client.list_objects(Bucket=bucket_name)
objects = pd.DataFrame(objects['Contents'])
key_name = objects.loc[objects['Key'].str.contains('Glendora_Parking', case = False)]['Key'].values[0]

url = client.generate_presigned_url(
ClientMethod='get_object', 
Params={'Bucket': bucket_name, 'Key': key_name},
ExpiresIn=3600)

