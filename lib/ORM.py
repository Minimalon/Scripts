#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

engine = create_engine("mysql+pymysql://progress:progress@10.8.16.18:3306/progress?charset=utf8mb4")
Base = declarative_base()


class Shippers(Base):
    __tablename__ = 'shippers'
    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(255), nullable=False, )
    inn = Column(String(255), nullable=False)
    fsrar = Column(String(255), nullable=False)


class CashInfo(Base):
    __tablename__ = 'cash_info'
    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(255), nullable=False)
    inn = Column(String(255), nullable=False)
    kpp = Column(String(255), nullable=False)
    fsrar = Column(String(255))
    fsrar2 = Column(String(255))
    address = Column(String(255), nullable=False)
    ooo_name = Column(String(255))
    ip_name = Column(String(255))
    ip = Column(String(255))



class AtolInfo(Base):
    __tablename__ = 'atol_info'
    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(255), nullable=False)
    firmware = Column(String(255), nullable=False)
    configuration = Column(String(255), nullable=False)
    templates = Column(String(255), nullable=False)
    controlUnit = Column(String(255), nullable=False)
    boot = Column(String(255), nullable=False)
    serialNumber = Column(String(255), nullable=False)
    inn = Column(String(45), nullable=False)


    def __init__(self, name, firmware, configuration, templates, controlUnit, boot, serialNumber, inn):
        self.name = name
        self.firmware = firmware
        self.configuration = configuration
        self.templates = templates
        self.controlUnit = controlUnit
        self.boot = boot
        self.serialNumber = serialNumber
        self.inn = inn

    def update(self, **kwargs):
        print(kwargs)
        print(self.inn, kwargs['inn'])
        if self.name != kwargs['name']:
            self.name = kwargs['name']
        if self.firmware != kwargs['firmware']:
            self.firmware = kwargs['firmware']
        if self.configuration != kwargs['configuration']:
            self.configuration = kwargs['configuration']
        if self.templates != kwargs['templates']:
            self.templates = kwargs['templates']
        if self.controlUnit != kwargs['controlUnit']:
            self.controlUnit = kwargs['controlUnit']
        if self.boot != kwargs['boot']:
            self.boot = kwargs['boot']
        if self.serialNumber != kwargs['serialNumber']:
            self.serialNumber = kwargs['serialNumber']
        if self.inn != kwargs['inn']:
            self.inn = kwargs['inn']

    def __repr__(self):
        return self.serialNumber


class Bottles_info(Base):
    __tablename__ = 'bottles_info'
    id = Column(Integer, nullable=False, primary_key=True)
    Type = Column(String(255), nullable=False)
    FullName = Column(String(255), nullable=False)
    AlcCode = Column(String(255), nullable=False)
    AlcVolume = Column(String(255), nullable=False)
    ProductVCode = Column(String(255), nullable=False)
    UnitType = Column(String(255), nullable=False)
    Price = Column(String(255), nullable=False)


    def __init__(self, Type, FullName, AlcCode, AlcVolume, ProductVCode, UnitType, Price):
        self.Type = Type
        self.FullName = FullName
        self.AlcCode = AlcCode
        self.AlcVolume = AlcVolume
        self.ProductVCode = ProductVCode
        self.UnitType = UnitType
        self.Price = Price

    def __repr__(self):
        return self.FullName


Base.metadata.create_all(engine)
