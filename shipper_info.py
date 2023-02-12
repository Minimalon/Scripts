#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.orm import *
from bs4 import BeautifulSoup
import os, sys

sys.path.append(os.path.abspath("/root/ArturAuto"))
from lib import ORM

engine = create_engine("mysql+pymysql://progress:progress@10.8.16.18:3306/progress?charset=utf8mb4")
session = Session(bind=engine)


def check_sql_cache(**kwargs):
    sql_cache_path = os.path.join(os.path.dirname(__file__), 'SQL_cache.txt')
    if os.path.exists(sql_cache_path):
        sql_cache = [line.strip() for line in open(sql_cache_path).readlines()]
        if kwargs["fsrar"] in sql_cache:
            return False
    else:
        with open(sql_cache_path, 'w') as file:
            for line in session.query(ORM.Shippers).all():
                file.write(line.fsrar + '\n')
        sql_cache = [line.strip() for line in open(sql_cache_path).readlines()]

    return sql_cache_path, sql_cache


def uniq_insert(**kwargs):
    sql_cache = check_sql_cache(**kwargs)
    if sql_cache:
        fsrar = session.query(ORM.Shippers).filter(ORM.Shippers.fsrar == kwargs["fsrar"]).first()
        if fsrar is None:
            # Если все аргументы True
            if len(kwargs) == len([v for k, v in kwargs.items() if v]):
                if kwargs["fsrar"] not in sql_cache:
                    session.add(ORM.Shippers(**kwargs))
                    open(sql_cache[0], 'a+').write(kwargs["fsrar"] + '\n')
        # else:
        #     SN.update(**kwargs)
        session.commit()


def send_shippers():
    ttnloads = ['/root/ttnload/TTN', '/root/ttnload2/TTN']
    for ttnload in ttnloads:
        if os.path.exists(ttnload):
            os.chdir(ttnload)
            for ttn in os.listdir():
                WB = os.path.join(ttn, "TTN/WayBill_v4.xml")
                if os.path.exists(WB):
                    with open(WB, 'r') as WB_file:
                        try:
                            soup = BeautifulSoup(WB_file.read(), "xml")
                            shipper_name = soup.find("Shipper").find("ShortName").text.strip()
                            shipper_fsrar = soup.find("Shipper").find("ClientRegId").text.strip()
                            shipper_inn = soup.find("Shipper").find("INN").text.strip()
                            if shipper_inn and shipper_fsrar and shipper_name:
                                uniq_insert(name=shipper_name, inn=shipper_inn, fsrar=shipper_fsrar)
                        except Exception as ex:
                            print(ex)


def main():
    send_shippers()


if __name__ == "__main__":
    main()
