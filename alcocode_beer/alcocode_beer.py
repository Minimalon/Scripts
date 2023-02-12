#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import xml.etree.ElementTree as ET
from sqlalchemy import *
from sqlalchemy.orm import *
sys.path.append(os.path.abspath("/root/ArturAuto"))
from lib import ORM

engine = create_engine("mysql+pymysql://progress:progress@10.8.16.18:3306/progress?charset=utf8mb4")
session = Session(bind=engine)

def get_all_WayBillv4(dir_path):
    dirs = os.listdir(dir_path)
    result = []
    for dir in dirs:
        wb = os.path.join(dir_path, dir, 'WayBill_v4.xml')
        if os.path.exists(wb):
            result.append(wb)
    return result


def get_info_from_Waybillv4(dirs_list):
    result = []
    for dir in dirs_list:
        tree = ET.fromstring(open(dir, 'r', encoding='utf8').read())
        for position in tree.findall('*/*/*/{http://fsrar.ru/WEGAIS/TTNSingle_v4}Position'):
            Price = position.find("{http://fsrar.ru/WEGAIS/TTNSingle_v4}Price").text
            for product in position.findall("{http://fsrar.ru/WEGAIS/TTNSingle_v4}Product"):
                Type = product.find("{http://fsrar.ru/WEGAIS/ProductRef_v2}Type").text
                FullName = product.find("{http://fsrar.ru/WEGAIS/ProductRef_v2}FullName").text
                AlcCode = product.find("{http://fsrar.ru/WEGAIS/ProductRef_v2}AlcCode").text
                AlcVolume = product.find("{http://fsrar.ru/WEGAIS/ProductRef_v2}AlcVolume").text
                ProductVCode = product.find("{http://fsrar.ru/WEGAIS/ProductRef_v2}ProductVCode").text
                UnitType = product.find("{http://fsrar.ru/WEGAIS/ProductRef_v2}UnitType").text
                uniq_insert(Type=Type, FullName=FullName, AlcCode=AlcCode, AlcVolume=AlcVolume, ProductVCode=ProductVCode, UnitType=UnitType, Price=Price)

def check_sql_cache(**kwargs):
    sql_cache_path = os.path.join(os.path.dirname(__file__), 'SQL_cache.txt')
    if os.path.exists(sql_cache_path):
        sql_cache = [line.strip() for line in open(sql_cache_path).readlines()]
        if kwargs["AlcCode"] in sql_cache:
            return False
    else:
        with open(sql_cache_path, 'w') as file:
            for line in session.query(ORM.Bottles_info).all():
                file.write(line.AlcCode + '\n')
        sql_cache = [line.strip() for line in open(sql_cache_path).readlines()]

    return sql_cache_path ,sql_cache

def uniq_insert(**kwargs):
    sql_cache = check_sql_cache(**kwargs)
    if sql_cache:
        AlcCode = session.query(ORM.Bottles_info).filter(ORM.Bottles_info.AlcCode == kwargs["AlcCode"]).first()
        if AlcCode is None:
            # Если все аргументы True
            if len(kwargs) == len([v for k, v in kwargs.items() if v]):
                if kwargs["AlcCode"] not in sql_cache:
                    AlcCode = ORM.Bottles_info(**kwargs)
                    session.add(AlcCode)
                    open(sql_cache[0], 'a+').write(kwargs["AlcCode"] + '\n')
        # else:
        #     SN.update(**kwargs)
        session.commit()


def main(ttnload_path):
    get_info_from_Waybillv4(get_all_WayBillv4(ttnload_path))


if __name__ == '__main__':
    main('/root/ttnload2/TTN')
