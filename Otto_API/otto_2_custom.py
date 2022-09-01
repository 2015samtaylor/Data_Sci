#!/usr/bin/env python
# coding: utf-8

# In[2]:


import json
import requests
import pandas as pd
from urllib.request import urlretrieve as retrieve
import pysftp 
import config

class get_otto:
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
    
    def login(self):
        s = requests.Session()
        payload = {
            'username' : self.username,
            'password' : self.password,
            "grant_type": "password"
        }

        headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic UDcwUTdKZXVBRjBKMHF1UUpKcVh0Vzd3M1NMaVl0MWhKRHVDTFc4OTp4QnE2N21HU2t2V0EyNFR0RUliMDZ0T1FmeVBMZjFySm9lNVBqZlQwek5EZXNlbWtZSjdJek9taFVlVHFpUGNTUEU0RFlpTERQNjdIQ3NnWnJNSjlTYkZ4R2h4T1AwQm1KYUl4QnZUYjF4REpJZHFOejExSzFxUlZwU2pHM21ndQ=='
        }

        res = s.post('https://ottocap.com/signin/token/', headers=headers, data=payload)

        session_output = (json.loads(res.content)['access_token'])
        
        headers_2 = {
        'Authorization': 'Bearer '+session_output
        }
        
        URL_2 = 'https://ottocap.com/api/s/download_inventory'
        response = requests.get(URL_2, headers=headers_2)
        final_url = response.json()['file']
        
        return(final_url)
        
    
# passing in variables to create object, final output returns unique url with AWS access key id
# url is passed into function to create dataframe. Frame is sent to Google Sheets. 

# drive.mount('/content/drive', force_remount = False)
# %cd /content/drive/My Drive/gspread_pandas

otto_calls = get_otto(config.otto_email, config.otto_pass)
# c = gspread_pandas.conf.get_config('/content/drive/My Drive/gspread_pandas', 'stock-2015-d4639aac1fb5.json')

def retrieve_send():

    retrieve(otto_calls.login(), 'ottocap_inventory.csv')
    
    df = pd.read_csv('ottocap_inventory.csv')
    df2 = df[['sku_parent', 'sku_no', 'name', 'color', 'size','instock', 'CA', 'TX', 'GA']].copy()
    
    return(df2)
    
df = retrieve_send()
df.to_csv('otto_inv.csv', index = False)

# ----------------------------------------------- send otto inventory to remote server------

Hostname = '165.22.33.209'
Username = 'root'
Password = 'S1lverado14!'
sftpPort = 22

# ignore hosts check
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None


with pysftp.Connection(host=Hostname, port=sftpPort, username=Username, password=Password, cnopts = cnopts) as sftp:
    print('Connection established')
    
    remotepath = '/var/www/html/admin/ottoexcelfile/otto_inv.csv'
    localpath = 'otto_inv.csv'
    sftp.put(localpath, remotepath)

