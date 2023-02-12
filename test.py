#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.orm import *
from bs4 import BeautifulSoup

import os, sys, re
from lib import ORM
import pprint

import pymysql

engine = create_engine("mysql+pymysql://progress:progress@10.8.16.18:3306/progress?charset=utf8mb4")
session = Session(bind=engine)



def insert(**kwargs):
    SN = session.query(ORM.AtolInfo).filter(ORM.AtolInfo.serialNumber == kwargs["serialNumber"]).first()
    if SN is None:
        # Если все аргументы True
        if len(kwargs) == len([v for k, v in kwargs.items() if v]):
            SN = ORM.AtolInfo(**kwargs)
            session.add(SN)
    else:
        print(SN)
        SN.update(**kwargs)
    session.commit()




if __name__ == '__main__':
    insert(name='111', firmware='333', configuration='333', templates='444', controlUnit='555', boot='666',
           serialNumber="00106705866909")