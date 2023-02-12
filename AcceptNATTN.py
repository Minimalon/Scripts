#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os

from sqlalchemy import create_engine
from sqlalchemy.orm import *
sys.path.append(os.path.abspath("/root/ArturAuto"))
from lib import UTM, ORM

engine = create_engine("mysql+pymysql://progress:progress@10.8.16.18:3306/progress?charset=utf8mb4")
session = Session(bind=engine)



def main(port):
    utm = UTM.UTM(port=port)
    ttn_NATTN = utm.get_ReplyNATTN()
    accepted_ttn = utm.get_accepted_ttn()

    if not ttn_NATTN:
        print("\033[0;32m{}\033[0m".format("Нету накладных в ReplyNATTN"))
        sys.exit()

    print("\033[1;33mВыберите накладные\033[0m")
    print("\033[0;35m1: \033[0;33mПринять все накладные\033[0m")
    for index, ttn in enumerate(ttn_NATTN):
        index += 2
        shipper = session.query(ORM.Shippers).filter(ORM.Shippers.fsrar == ttn[3]).first()
        if ttn[0] in accepted_ttn:
            fullname_ttn = "\033[0;35m{0}: \033[1;36m{1} \033[1;37m{2} \033[1;36m{3} \033[1;37m{4} \033[1;33m{5}\033[0m". \
                            format(str(index), shipper.name, str(ttn[1]), str(ttn[2]), str(ttn[0]), "Уже принята")
        else:
            fullname_ttn = "\033[0;35m{0}: \033[1;36m{1} \033[1;37m{2} \033[1;36m{3} \033[1;37m{4}\033[0m". \
                            format(str(index), shipper.name, str(ttn[1]), str(ttn[2]), str(ttn[0]))
        print(fullname_ttn)
    answer = int(input("Введите строку: "))
    idnex_answer = answer - 2
    if answer == 1:
        for ttn in ttn_NATTN:
            utm.send_WayBillv4(ttn[0])
    elif answer == 0:
        print("\033[0;31m{}\033[0m".format("Недопустимое число 0"))
    elif answer > len(ttn_NATTN) + 1:
        print("\033[0;31m{0} {1}\033[0m".format("Недопустимое число", str(answer)))
    else:
        answer_ttn = ttn_NATTN[idnex_answer]
        ttn = answer_ttn[0]
        utm.send_WayBillv4(ttn)


if len(sys.argv) == 2:
    main(sys.argv[1])
else:
    print("Укажите один аргумент в виде порта УТМ")
