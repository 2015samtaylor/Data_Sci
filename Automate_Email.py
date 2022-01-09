#!/usr/bin/env python
# coding: utf-8

# In[14]:


import smtplib
import os
from email.message import EmailMessage
import imghdr

EMAIL_ADDRESS = os.environ.get('EMAIL')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')

contacts = ['2015samtaylor@gmail.com', 'sammytaylor2006@yahoo.com']

msg = EmailMessage()
msg['Subject'] = 'Hello Kypee'
msg['From'] = EMAIL_ADDRESS
msg['To'] = (contact for contact in contacts)


msg.set_content('This is a plain text email')

msg.add_alternative("""<!DOCTYPE html>
<html>
    <body>
        <h1 style="color:SlateGray;">This is an HTML Email!</h1>
    <body>
</html>
""", subtype = 'html')



    
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)
    

