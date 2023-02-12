#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os.path
import sys
import xml.etree.ElementTree as ET


def logger(WayBill_path, amark, norm_EAN, bad_EAN, ShortName):
    with open('/linuxcash/net/server/server/logs/amcMissmatch.txt', 'a+', encoding='utf-8') as logs:
        logs.write("{} {} {} {}!={} {} {}\n".format(datetime.datetime.now(), os.uname()[1], ShortName, norm_EAN, bad_EAN, WayBill_path, amark))


def replace_ean(WayBill_path, amark, norm_EAN):
    if os.path.exists(WayBill_path):
        xml = ET.parse(WayBill_path)
        ShortName = xml.find('*/*/*/*/*/{http://fsrar.ru/WEGAIS/ClientRef_v2}ShortName').text
        for position in xml.findall("*/*/*/{http://fsrar.ru/WEGAIS/TTNSingle_v4}Position"):
            ean = position.find("{http://fsrar.ru/WEGAIS/TTNSingle_v4}EAN13")
            for amc in position.findall(".//{http://fsrar.ru/WEGAIS/CommonV3}amc"):  # {http://fsrar.ru/WEGAIS/CommonV3}amc
                if amark == amc.text:
                    if int(norm_EAN) != int(ean.text):
                        logger(WayBill_path, amark, norm_EAN, ean.text, ShortName)
                        # ean.text = str(norm_EAN)
                        # xml.write(WayBill_path, encoding='utf-8')


    else:
        print("Данного WayBill не существует '{}'".format(WayBill_path))


def main():
    if len(sys.argv) == 4:
        replace_ean(sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == '__main__':
    main()
