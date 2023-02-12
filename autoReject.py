#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mimetypes
from email import encoders
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess
import os, re, requests,sys
from collections import namedtuple
sys.path.append(os.path.abspath("/root/ArturAuto"))
from lib.UTM import UTM

def send_email(email, path):
    sender = 'minimaltesttest@gmail.com'
    password = 'minimal$test'

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    try:
        server.login(sender, password)
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = email
        msg['Date'] = formatdate(localtime=True)
        ftype, encoding = mimetypes.guess_type(path)
        file_type, subtype = ftype.split('/')
        if file_type == 'image':
            msg["Subject"] = "Barcodes"
            with open(path, 'rb') as f:
                file = MIMEImage(f.read(), subtype)
        else:
            msg["Subject"] = "OSTATKI"
            file = MIMEBase('application', "octet-stream")
            file.set_payload(open(path, "rb").read())
            encoders.encode_base64(file)
        file.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(path))
        msg.attach(file)

        server.sendmail(sender, email, msg.as_string())

        # server.sendmail(sender, sender, f"Subject: CLICK ME PLEASE!\n{message}")
    except Exception as _ex:
        print(_ex)
        pass



def get_identity_and_EAN(ttn_info):
    """Принимает [ссылку на FORM2REGINFO, ссылку на Waybill_v4, номер ттн егаис]"""
    """Возвращает [Identity, EAN13, номер ттн егаис, ShortName, AlcCode, ProductVCode ]"""
    print(ttn_info[1])
    xml_string = requests.get(ttn_info[1]).text
    xml = ET.fromstring(xml_string)
    INN = xml.find('*/*/*/*/*/{http://fsrar.ru/WEGAIS/ClientRef_v2}INN').text
    adress = xml.find('*/*/*/{http://fsrar.ru/WEGAIS/TTNSingle_v4}Consignee/*/*/{http://fsrar.ru/WEGAIS/ClientRef_v2}description').text
    # adress = adress.find('*/*/{http://fsrar.ru/WEGAIS/ClientRef_v2}description').text
    Date = xml.find('*/*/*/{http://fsrar.ru/WEGAIS/TTNSingle_v4}Date').text
    NUMBER = xml.find('*/*/*/{http://fsrar.ru/WEGAIS/TTNSingle_v4}NUMBER').text
    if int(INN) != 1658067670: #1659091192:
        print("{} != 1658067670".format(INN))
        return []
    result = []
    EAN = namedtuple("Position_info",'adress Identity EAN13 FullName AlcCode count_amc ttn Date NUMBER')
    for identity in xml.findall('*/*/*/{http://fsrar.ru/WEGAIS/TTNSingle_v4}Position'):
        Identity = identity.find('{http://fsrar.ru/WEGAIS/TTNSingle_v4}Identity').text
        EAN13 = identity.find('{http://fsrar.ru/WEGAIS/TTNSingle_v4}EAN13').text
        FullName = identity.find('*/{http://fsrar.ru/WEGAIS/ProductRef_v2}FullName').text
        AlcCode = identity.find('*/{http://fsrar.ru/WEGAIS/ProductRef_v2}AlcCode').text
        count_amc = len(identity.findall('*/*/*/*/{http://fsrar.ru/WEGAIS/CommonV3}amc'))
        result.append(EAN(adress, Identity, EAN13, FullName, AlcCode, count_amc, ttn_info[2], Date, NUMBER))
    return result


def check_whitelist(path_whiteList, TTN_eans):
    black_EAN = []
    if TTN_eans:
        white_EAN = [EAN.strip() for EAN in open(path_whiteList, 'r').readlines()]
        for ean in TTN_eans:
            if ean.EAN13 in white_EAN or ean.AlcCode in white_EAN:
                black_EAN.append(ean)
    return black_EAN


def logger(inn, black_eans):
    date = str(datetime.utcnow())
    PC_name = os.uname()[1]
    OOO_name = ''

    if inn in ['1650388488', '1658228253', '1658227108', '1656113000']:
        OOO_name = "ROSSICH.log"
    if inn in ['1657253779', '1660340005', '1660343863', '1660344472', '1644096180', '1660346991', '1660347201', '1660349488', '1660349657']:
        OOO_name = "SAMAN.log"
    if inn in ['1659208757', '1644096744', '1659208740', '1659208820', '1659208718', '1659208838', '1659208845', '1659211693']:
        OOO_name = "PREMIER.log"

    for black_ean in black_eans:
        black_ean = "[adress='{}', Identity='{}', EAN13='{}', FullName='{}', AlcCode='{}', count_amc={}, ttn='{}', Date='{}', NUMBER='{}']".format(
                    black_ean.adress, black_ean.Identity, black_ean.EAN13, black_ean.FullName, black_ean.AlcCode, black_ean.count_amc, black_ean.ttn, black_ean.Date, black_ean.NUMBER)

        if OOO_name:
            with open(os.path.join('/linuxcash/net/server/server/logs/autoReject', OOO_name), 'a+') as log_file:
                log_file.write("{} {} {}\n".format(date, PC_name, black_ean))


def main(port):
    utm = UTM(port=port)
    path_whitelist = '/linuxcash/net/server/server/All/whiteList_eans.txt'
    # path_whitelist = 'TTN/whiteList_eans.txt.txt'
    for ttn_info in utm.get_Waybill_and_FORM2REGINFO():
        print(utm.get_Waybill_and_FORM2REGINFO())
        EANs= get_identity_and_EAN(ttn_info)
        black_ean = check_whitelist(path_whitelist, EANs)
        if black_ean:
            inn = [re.findall('[0-9]+', line) for line in open('/linuxcash/cash/conf/ncash.ini', 'r') if re.match('inn', line)][0][0]
            if inn in ['1650388488', '1658228253', '1658227108', '1656113000',
                       '1657253779', '1660340005', '1660343863', '1660344472', '1644096180', '1660346991', '1660347201', '1660349488', '1660349657',
                       '1659208757', '1644096744', '1659208740', '1659208820', '1659208718', '1659208838', '1659208845', '1659211693']:
                identity = ''
                for ean in black_ean:
                    identity += "{} ".format(ean.Identity)
                print('/linuxcash/net/server/server/All/Anvar/ttnstatus.sh', black_ean[0].ttn.split('-')[1], 'd_s', identity)
                subprocess.call(['/linuxcash/net/server/server/All/Anvar/ttnstatus.sh', black_ean[0].ttn.split('-')[1], 'd_s', identity])
                requests.delete(ttn_info[0])
                requests.delete(ttn_info[1])
                logger(inn, black_ean)



if __name__ == '__main__':
    main("8082")