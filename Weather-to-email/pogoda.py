#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import requests
from lxml import etree
import smtplib
from email.mime.text import MIMEText
from contextlib import suppress

# Конфигурационные параметры
CONFIG = {
    'files': {
        'xml': './barnaul.xml',
        'html': './barnaul.html',
        'xslt': 'transcode.xslt'
    },
    'url': "https://meteoinfo.ru/rss/forecasts/index.php?s=29838",
    'email': {
        'from': "postmaster@domain.tld",
        'to': "recipient1@domain.tld",
        'cc': "recipient2@domain.tld",
        'subject': "Гидрометцентр RSS",
        'smtp_server': 'mx.domain.tld',
        'smtp_port': 587,
        'login': "LOGIN",
        'password': "PASSWORD"
    },
    'debug': False
}

def cleanup_files():
    """Удаление старых файлов если они существуют"""
    for file_type, file_path in CONFIG['files'].items():
        if file_type in ('xml', 'html'):
            with suppress(FileNotFoundError):
                os.remove(file_path)
                print(f"Удален старый файл: {file_path}")

def download_xml():
    """Загрузка XML файла с прогнозом погоды"""
    response = requests.get(CONFIG['url'])
    response.raise_for_status()
    with open(CONFIG['files']['xml'], 'wb') as f:
        f.write(response.content)

def transform_xml_to_html():
    """Преобразование XML в HTML с помощью XSLT"""
    xslt_transformer = etree.XSLT(etree.parse(CONFIG['files']['xslt']))
    output_doc = xslt_transformer(etree.parse(CONFIG['files']['xml']))
    
    with open(CONFIG['files']['html'], 'wb') as f:
        f.write(etree.tostring(output_doc, encoding='utf-8'))

def postprocess_html():
    """Постобработка HTML файла"""
    with open(CONFIG['files']['html'], 'r', encoding='utf-8') as file:
        filedata = file.read()
    
    # Оптимизированная замена текста
    replacements = [
        ('.', '. '),
        (' ,', ','),
        ('  ', ' ')
    ]
    for old, new in replacements:
        filedata = filedata.replace(old, new)
    
    with open(CONFIG['files']['html'], 'w', encoding='utf-8') as file:
        file.write(filedata)

def send_email():
    """Отправка email с прогнозом погоды"""
    with open(CONFIG['files']['html'], 'r', encoding='utf-8') as file:
        html_content = file.read()

    msg = MIMEText(html_content, 'html', "utf-8")
    msg['From'] = CONFIG['email']['from']
    msg['To'] = CONFIG['email']['to']
    msg['Cc'] = CONFIG['email']['cc']
    msg['Subject'] = CONFIG['email']['subject']

    if CONFIG['debug']:
        print(msg.as_string())
    else:
        recipients = [CONFIG['email']['to']] + CONFIG['email']['cc'].split(",")
        with smtplib.SMTP(CONFIG['email']['smtp_server'], CONFIG['email']['smtp_port']) as server:
            server.starttls()
            server.login(CONFIG['email']['login'], CONFIG['email']['password'])
            server.sendmail(CONFIG['email']['from'], recipients, msg.as_string())

def main():
    try:
        cleanup_files()
        download_xml()
        transform_xml_to_html()
        postprocess_html()
        send_email()
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
