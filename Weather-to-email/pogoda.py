#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import requests
import lxml.html
from lxml import etree
import smtplib
from email.mime.text import MIMEText

####################################

if os.path.exists("./barnaul.xml"):
    os.remove("./barnaul.xml")
else:
    print("The file does not exist")

if os.path.exists("./barnaul.html"):
    os.remove("./barnaul.html")
else:
    print("The file does not exist")

####################################

url = "https://meteoinfo.ru/rss/forecasts/index.php?s=29838"

r = requests.get(url)
with open('./barnaul.xml', 'w') as f:
    f.write(r.content)

####################################

xslt_doc = etree.parse("transcode.xslt")
xslt_transformer = etree.XSLT(xslt_doc)

source_doc = etree.parse("barnaul.xml")
output_doc = xslt_transformer(source_doc)

original_stdout = sys.stdout

with open('barnaul.html', 'w') as f:
    sys.stdout = f
    print(output_doc)
    sys.stdout = original_stdout

####################################

fromaddr = "FROM@EXAMPLE.COM"
toaddr = "TO@EXAMPLE.COM"
ccaddr = "CC@EXAMPLE.COM"

rcpt = ccaddr.split(",") + [toaddr]

html = open("barnaul.html")
msg = MIMEText(html.read(), 'html', "utf-8")
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Cc'] = ccaddr
msg['Subject'] = "Гидрометцентр России"

debug = False
if debug:
    print(msg.as_string())
else:
    server = smtplib.SMTP('MX.EXAMPLE.COM', 25)
    server.starttls()
    server.login("USER", "PASSWORD")
    text = msg.as_string()
    server.sendmail(fromaddr, rcpt, text)
    server.quit()
