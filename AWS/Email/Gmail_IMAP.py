#!/usr/bin/env python
# coding: utf-8

# In[57]:


# Script to Scrape Responses to Email and piece together for NO SQL DB.

import imaplib
import pandas as pd
import email
import re
import pymongo
import numpy as np
from pymongo import MongoClient
from config import gmail_password
subject_line = "green dot"

def scrape_outbox_or_inbox_w_subject(inbox_or_outbox, subject):


    # IMAP server settings for Gmail
    imap_server = 'imap.gmail.com'
    username = '2015samtaylor@gmail.com'
    password = gmail_password

    # Connect to the Gmail IMAP server
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, password)

    # to see what the mailbox names are, and what is available
    # status, mailboxes = imap.list()

    # Select the mailbox/folder where your emails are located
    
    if inbox_or_outbox == 'inbox':
        mailbox = 'INBOX'
    elif inbox_or_outbox == 'outbox':
        mailbox = '"[Gmail]/Sent Mail"'
    else:
        print('Wrong string for inbox or outbox')
        
    my_mail = imap.select(mailbox)

    # # Search for emails with a specific subject or other criteria
    search_criteria = f'SUBJECT "{subject}"'
    status, response = imap.search(None, search_criteria)

    if status == 'OK':
        email_ids = response[0].split()
        if email_ids:
            print(f"You have email responses to the specified search criteria in the {inbox_or_outbox}")
        else:
            print(f"There are no responses to the specified emails search criteria in the {inbox_or_outbox}")

    # ---------------------------iterate through email_ids, get the whole message and append the data to msgs list.

    msgs = [] 

    #Iterate through messages and extract data into the msgs list
    for num in email_ids:
        typ, data = imap.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)

        msgs.append(data)

#     -------------------------Cleanse the msgs list and extract what we want-------------------

    email_data = []

    for msg in msgs[::-1]:        #start from most recent message
        for response_part in msg:
            if isinstance(response_part, tuple):
                my_msg = email.message_from_bytes(response_part[1])

                email_dict = {
                    'subject': my_msg['subject'],
                    'from': my_msg['from'],
                    'to': my_msg['to'],
                    'date': my_msg['Date'],
                    'first_message': my_msg['body'],
                    'reply thread': ''
                }

                if my_msg.is_multipart():    #walk iterates through the message thread if multipart
                    for part in my_msg.walk():
                        content_type = part.get_content_type()
                        if content_type == 'text/plain':
                            
                            try:
                                body = part.get_payload(decode=True).decode('utf-8')
                            except UnicodeDecodeError:
                                body = part.get_payload(decode=True).decode('latin-1', 'replace')
                            email_dict['first_message'] = body
                            break  # Assuming you want only the first plain text body
                            
                else:
                    body = my_msg.get_payload(decode=True).decode()
                    email_dict['first_message'] = body

                email_data.append(email_dict)

    df = pd.DataFrame(email_data)
        
    
    try:
         #change date to datetime, in order to create unique _id reference of when the email occured
        df['date'] = pd.to_datetime(df['date'], errors='coerce', utc=True)
        df['_id'] = df['date'].dt.strftime('%m%d%Y%H%M%S')

        #create a new column that shows 1 if the message is a reply
        df['reply'] = np.where(df['subject'].str.contains('RE:', case=False, regex=True), 'Y', 'N')

         #Remove 'RE:' from the 'subject' column in order to merge on subject line
        df['subject'] = df['subject'].str.replace(r'^RE:\s*', '', case=False, regex=True)
         #Remove 'FWD:' and 'FW:' from the 'subject' column
        df['subject'] = df['subject'].str.replace(r'^FWD:\s*', '', case=False, regex=True)
        df['subject'] = df['subject'].str.replace(r'^FW:\s*', '', case=False, regex=True)
        df['subject'] = df['subject'].str.strip()

        #extract emails addresses from to & from columns
        df['to'] = df['to'].apply(lambda x: re.search(r'<([^<>]+)>', x).group(1) if '<' in x and '>' in x else x)
        df['from'] = df['from'].apply(lambda x: re.search(r'<([^<>]+)>', x).group(1) if '<' in x and '>' in x else x)
    
    except KeyError:
        pass
    
    
    if inbox_or_outbox == 'outbox':
        try:
            #make the body column a list
            df['body'] = df['body'].apply(lambda x: [x] if isinstance(x, str) else x)
        
        except KeyError:
            pass
        
                
    elif inbox_or_outbox == 'inbox':
        try:
            # Drop empty messages based on body
            df = df.dropna(subset=['first_message'], how='any')
            df = df.sort_values(by=['subject','date'], ascending=False)
            # Drop duplicates in the 'subject' column, keeping only the first occurrence (most recent)
            # Only keep the most latest thread, and attach it into the outbox body array
            df = df.drop_duplicates(subset='subject', keep='first').reset_index(drop = True)
        
        except KeyError:
            pass
    else:
        print('Wrong inbox or outbox variable')
        
    
    return(df)


# Get inbox/outbox into data frames
inbox = scrape_outbox_or_inbox_w_subject('inbox', subject_line)
inbox.name = 'inbox'

outbox = scrape_outbox_or_inbox_w_subject('outbox', subject_line)
outbox.name = 'outbox'

# ------------------------------------------Piece together replies to outbox emails------------------------------- 

#Three things need to happen to be pieced together
# 1. subject of inbox message contains sent message subject
# 2. Message must be a RE:
# 3. The outbox 'to' email must be the same as inbox 'from' email

def piece_together():
    for i in range(len(outbox)):

        idx_ref = outbox.iloc[i]
        sent_message_subject = idx_ref['subject']
        sent_message_to = idx_ref['to']

        #get date & body from inbox based on sent_message subject, and if the message is a reply
        message = inbox.loc[(inbox['subject'].str.contains(sent_message_subject, case=False, regex=True)) & (inbox['reply'] == 'Y')]


        # check if the initial sent to address is the same as the reply from. (Confirming the reply)
        if not message.empty:
            if message['from'].values[0] == sent_message_to:
                pass
            else:
                message = message.drop(index = message.index)        

        try:
            body = message['first_message'].values[0]
            date = str(message['date'].values[0])
            
            re_dict = {
                'date': date,
                'thread': body
            }

            re_dict = json.dumps(re_dict)
            #json.loads would have to be used to reformat it back

            outbox.loc[i, 'reply thread'] = re_dict

            # Update the 'reply' column to 'Y' for the specific index i
            outbox.loc[i, 'reply'] = 'Y'

        except IndexError:
            pass
        
    return(outbox)
    
df = piece_together()
df.name = 'mail'
    
# -------------------Create conn with MDB, and insert any new emails, or update them accordingly-------------------------

# Establish connection, create database, and create collection within it. If already exists, lines simply create connection

client = MongoClient('mongodb://localhost:27017/')


# Timestamp ID enforces CRUD on updates now
# Upsert based on _id, and overwite with any new data. 
def upsert_w_new(frame):
    
    db = client['CP_Emails']  #database name remains
    
    collection = db[frame.name]
    
    # Reshape pandas df to json, and insert all data  (if running multiple times will keep inserting data with new _id)
    data_records = frame.to_dict(orient='records')

    for record in data_records:
        filter_query = {'_id': record['_id']}
        update_query = {'$set': record}
        collection.update_one(filter_query, update_query, upsert=True)
        
# df is the final product between outbox, and inbox
upsert_w_new(df)

