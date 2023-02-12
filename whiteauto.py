#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, sys
import xml.etree.ElementTree as ET


def add_solo_ttn(ttn, ttnload_path):
    os.chdir(ttnload_path)
    if re.match(r"[0-9]{10}", ttn):
        if os.path.exists('TTN-{}/WayBill_v4.xml'.format(ttn)) or os.path.exists('TTN-{}/WayBill_v3.xml'.format(ttn)):
            waybill = ET.parse("TTN-{}/{}".format(ttn, [line for line in os.listdir('TTN-{}'.format(ttn)) if re.findall('WayBill_v[3-4].xml', line)][0]))
            with open('/linuxcash/net/server/server/whitelist/{}/amark.txt'.format(hostname), 'a+') as whitelist:
                for position in waybill.getroot().findall('*/*/*/{http://fsrar.ru/WEGAIS/TTNSingle_v4}Position'):
                    try:
                        ean = position.find('{http://fsrar.ru/WEGAIS/TTNSingle_v4}EAN13').text
                    except:
                        ean = ''
                    for boxpos in position.findall('*/*/{http://fsrar.ru/WEGAIS/CommonV3}boxpos'):
                        for amc in boxpos.findall('*/{http://fsrar.ru/WEGAIS/CommonV3}amc'):
                            whitelist.write("{} {}\n".format(amc.text, ean))
        else:
            print("Не найден WayBill в данной накладной '{}'".format(ttn))
    else:
        print("Аргумент не проходит проверку [0-9]{10}")


def add_list_ttn(range, ttnload_path):
    os.chdir(ttnload_path)
    ttnload = list(reversed(os.listdir(ttnload_path)))
    ttnload = [ttn for ttn in ttnload if re.match('TTN', ttn)]
    ttnload.sort()
    for ttn in ttnload[-range:]:
        print(ttn)
        if os.path.exists('{}/WayBill_v4.xml'.format(ttn)) or os.path.exists('{}/WayBill_v3.xml'.format(ttn)):
            waybill = ET.parse("{}/{}".format(ttn, [line for line in os.listdir('{}'.format(ttn)) if re.findall('WayBill_v[3-4].xml', line)][0]))
            with open('/linuxcash/net/server/server/whitelist/{}/amark.txt'.format(hostname), 'a+') as whitelist:
                for position in waybill.getroot().findall('*/*/*/{http://fsrar.ru/WEGAIS/TTNSingle_v4}Position'):
                    try:
                        ean = position.find('{http://fsrar.ru/WEGAIS/TTNSingle_v4}EAN13').text
                    except:
                        ean = ''
                    for boxpos in position.findall('*/*/{http://fsrar.ru/WEGAIS/CommonV3}boxpos'):
                        for amc in boxpos.findall('*/{http://fsrar.ru/WEGAIS/CommonV3}amc'):
                            whitelist.write("{} {}\n".format(amc.text, ean))
        else:
            print("Не найдено данной накладной {}".format(ttn))



if __name__ == '__main__':
    hostname = os.uname()[1].split('-')[1]
    inn = [re.findall('[0-9]+', line) for line in open('/linuxcash/cash/conf/ncash.ini', 'r') if re.match('inn', line)][0]
    kpp = [re.findall('[0-9]+', line) for line in open('/linuxcash/cash/conf/ncash.ini', 'r') if re.match('kpp', line)][0]
    server_path = os.path.join("/linuxcash/net/server/server/exchange", str(inn[0]), str(kpp[0]))
    local_path = "/root/ttnload/TTN"


    if len(sys.argv) == 2:
        ttn = sys.argv[1]
        if os.path.exists(os.path.join(local_path, 'TTN-{}'.format(ttn))):
            add_solo_ttn(ttn, local_path)
        else:
            if os.path.exists(os.path.join(server_path, 'TTN-{}'.format(ttn))):
                add_solo_ttn(ttn, server_path)
            else:
                print("\033[0;31m{} '{}'\033[0m".format("ТТН не найдена", ttn))
    else:
        range = 15
        if os.path.exists(server_path):
            add_list_ttn(range, server_path)
        else:
            add_list_ttn(range, local_path)
