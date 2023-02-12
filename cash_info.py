#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import *
from sqlalchemy.orm import *
import re, os
from lib import ORM, UTM

engine = create_engine("mysql+pymysql://progress:progress@10.8.16.18:3306/progress?charset=utf8mb4")
session = Session(bind=engine)


def get_ip_address(name):
    return os.popen('ip addr show ' + name + ' | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()


def check_and_insert(name, inn, kpp, fsrar, fsrar2, address, ooo_name, ip_name, ip):
    cash = session.query(ORM.CashInfo).filter(ORM.CashInfo.name == name).first()
    if cash is None:
        cash = ORM.CashInfo(name=name, inn=inn, kpp=kpp, fsrar=fsrar, fsrar2=fsrar2, address=address, ooo_name=ooo_name, ip_name=ip_name, ip=ip)
        session.add(cash)

    # region Проверяю на изменение инфы
    if cash.name != name and name:
        cash.name = name
    if cash.inn != inn and inn:
        cash.inn = inn
    if cash.kpp != kpp and kpp:
        cash.kpp = kpp
    if cash.fsrar != fsrar and fsrar:
        cash.fsrar = fsrar
    if cash.fsrar2 != fsrar2 and fsrar2:
        cash.fsrar2 = fsrar2
    if cash.address != address and address:
        cash.address = address
    if cash.ooo_name != ooo_name and ooo_name:
        cash.ooo_name = ooo_name
    if cash.ip_name != ip_name and ip_name:
        cash.ip_name = ip_name
    if cash.ip != ip and ip:
        cash.ip = ip
    # endregion
    session.commit()


def main():
    name = os.uname()[1]
    inn = [re.findall('[0-9]+', line) for line in open('/linuxcash/cash/conf/ncash.ini', 'r') if re.match('inn', line)][0][0]
    kpp = [re.findall('[0-9]+', line) for line in open('/linuxcash/cash/conf/ncash.ini', 'r') if re.match('kpp', line)][0][0]
    address = [line.split('=')[1].strip().replace('"', '') for line in open('/linuxcash/cash/conf/ncash.ini', 'r') if re.match('address', line)][0]
    # region try/catch
    try:
        fsrar = UTM.UTM(port="8082").get_fsrar()
    except:
        fsrar = None
    try:
        fsrar2 = UTM.UTM(port="18082").get_fsrar()
    except:
        fsrar2 = None
    try:
        ooo_name = UTM.UTM(port="8082").get_name_rutoken()
    except:
        ooo_name = None
    try:
        ip_name = UTM.UTM(port="18082").get_name_rutoken()
    except:
        ip_name = None
    try:
        ip = get_ip_address("tun0")
    except:
        ip = None
    # endregion

    check_and_insert(name, inn, kpp, fsrar, fsrar2, address, ooo_name, ip_name, ip)


if __name__ == '__main__':
    main()
