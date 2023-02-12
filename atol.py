#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.orm import *
from bs4 import BeautifulSoup

import os, sys, re
import logging
from lib import ORM
import pprint

sys.path.append(os.path.abspath("/usr/lib/fptr10/langs/python/"))
from libfptr10 import IFptr

engine = create_engine("mysql+pymysql://progress:progress@10.8.16.18:3306/progress?charset=utf8mb4")
session = Session(bind=engine)
logging.basicConfig(level=logging.INFO, filename="/linuxcash/logs/current/ATOLconnect.log",
                    format="%(asctime)s %(funcName)s %(levelname)s - %(message)s")


def insert(**kwargs):
    SN = session.query(ORM.AtolInfo).filter(ORM.AtolInfo.serialNumber == kwargs["serialNumber"]).first()
    if SN is None:
        # Если все аргументы True
        if len(kwargs) == len([v for k, v in kwargs.items() if v]):
            SN = ORM.AtolInfo(**kwargs)
            logging.info("Inserting {}".format(kwargs))
            session.add(SN)
        else:
            logging.error("Insert failed {}".format(kwargs))
    else:
        logging.info("serialNumber already in database")
        SN.update(**kwargs)
    session.commit()


def get_atol_files(path):
    atols = [file for file in os.listdir(path) if re.findall('hw::AtolFiscalRegister_', file)]
    logging.info("Find atol: {}".format(atols))
    return atols


def get_usb_object(xml_paths, driver_path):
    objects = []
    for xml in xml_paths:
        xml = open(os.path.join(driver_path, xml), 'r').read()
        soup = BeautifulSoup(xml, 'lxml')
        check_five_atol = [_.text for _ in soup.findAll('property') if re.findall('Атол 5.0', _.text)]
        if check_five_atol:
            object = soup.find('ref')['object']
            file = [os.path.join(driver_path, file) for file in os.listdir(driver_path) if re.findall(object, file)][0]
            objects.append(file)
    logging.info("Find objects: {}".format(objects))
    return objects


def get_usbPath(usb_object_path):
    usbs = []
    for object in usb_object_path:
        object = open(object, 'r').read()
        soup = BeautifulSoup(object, 'lxml')
        usb_path = [_.text.strip() for _ in soup.findAll('property') if re.findall('hub', _['name'])][0]
        usbs.append(usb_path)
    logging.info("Find usbs: {}".format(usbs))
    return usbs


for usb in get_usbPath(get_usb_object(get_atol_files('/linuxcash/cash/conf/drivers'), '/linuxcash/cash/conf/drivers')):
    logging.info("Connect to USB: {}".format(str(usb)))
    logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w", format="%(asctime)s %(filename)s %(levelname)s %(message)s")

    fptr = IFptr('')
    logging.info("Версия {}".format(fptr.version()))
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_MODEL, str(IFptr.LIBFPTR_MODEL_ATOL_AUTO))
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_USB))
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_USB_DEVICE_PATH, usb)
    result = fptr.applySingleSettings()
    try:
        fptr.open()
        isOpened = fptr.isOpened()
        if isOpened == 0:
            logging.error("ATOL is not opened {}".format(usb))
            continue

        logging.info("ATOL opened {}".format(usb))
        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_STATUS)
        fptr.queryData()

        operatorID = fptr.getParamInt(IFptr.LIBFPTR_PARAM_OPERATOR_ID)
        logicalNumber = fptr.getParamInt(IFptr.LIBFPTR_PARAM_LOGICAL_NUMBER)
        shiftState = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_STATE)
        model = fptr.getParamInt(IFptr.LIBFPTR_PARAM_MODEL)
        mode = fptr.getParamInt(IFptr.LIBFPTR_PARAM_MODE)
        submode = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SUBMODE)
        receiptNumber = fptr.getParamInt(IFptr.LIBFPTR_PARAM_RECEIPT_NUMBER)
        documentNumber = fptr.getParamInt(IFptr.LIBFPTR_PARAM_DOCUMENT_NUMBER)
        shiftNumber = fptr.getParamInt(IFptr.LIBFPTR_PARAM_SHIFT_NUMBER)
        receiptType = fptr.getParamInt(IFptr.LIBFPTR_PARAM_RECEIPT_TYPE)
        lineLength = fptr.getParamInt(IFptr.LIBFPTR_PARAM_RECEIPT_LINE_LENGTH)
        lineLengthPix = fptr.getParamInt(IFptr.LIBFPTR_PARAM_RECEIPT_LINE_LENGTH_PIX)

        isFiscalDevice = fptr.getParamBool(IFptr.LIBFPTR_PARAM_FISCAL)
        isFiscalFN = fptr.getParamBool(IFptr.LIBFPTR_PARAM_FN_FISCAL)
        isFNPresent = fptr.getParamBool(IFptr.LIBFPTR_PARAM_FN_PRESENT)
        isInvalidFN = fptr.getParamBool(IFptr.LIBFPTR_PARAM_INVALID_FN)
        isCashDrawerOpened = fptr.getParamBool(IFptr.LIBFPTR_PARAM_CASHDRAWER_OPENED)
        isPaperPresent = fptr.getParamBool(IFptr.LIBFPTR_PARAM_RECEIPT_PAPER_PRESENT)
        isPaperNearEnd = fptr.getParamBool(IFptr.LIBFPTR_PARAM_PAPER_NEAR_END)
        isCoverOpened = fptr.getParamBool(IFptr.LIBFPTR_PARAM_COVER_OPENED)
        isPrinterConnectionLost = fptr.getParamBool(IFptr.LIBFPTR_PARAM_PRINTER_CONNECTION_LOST)
        isPrinterError = fptr.getParamBool(IFptr.LIBFPTR_PARAM_PRINTER_ERROR)
        isCutError = fptr.getParamBool(IFptr.LIBFPTR_PARAM_CUT_ERROR)
        isPrinterOverheat = fptr.getParamBool(IFptr.LIBFPTR_PARAM_PRINTER_OVERHEAT)
        isDeviceBlocked = fptr.getParamBool(IFptr.LIBFPTR_PARAM_BLOCKED)

        dateTime = fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_DATE_TIME)

        serialNumber = fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER)
        modelName = fptr.getParamString(IFptr.LIBFPTR_PARAM_MODEL_NAME)
        firmware = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)

        fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_REG_INFO)
        fptr.fnQueryData()

        inn = fptr.getParamInt(1018)
        ffdVersion = fptr.getParamInt(1209)
        fnsUrl = fptr.getParamString(1060)
        organizationAddress = fptr.getParamString(1009)
        organizationVATIN = fptr.getParamString(1018)
        organizationName = fptr.getParamString(1048)
        organizationEmail = fptr.getParamString(1117)
        paymentsAddress = fptr.getParamString(1187)
        registrationNumber = fptr.getParamString(1037)
        machineNumber = fptr.getParamString(1036)
        ofdVATIN = fptr.getParamString(1017)
        ofdName = fptr.getParamString(1046)

        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_UNIT_VERSION)
        fptr.setParam(IFptr.LIBFPTR_PARAM_UNIT_TYPE, IFptr.LIBFPTR_UT_FIRMWARE)
        fptr.queryData()
        firmware = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)

        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_UNIT_VERSION)
        fptr.setParam(IFptr.LIBFPTR_PARAM_UNIT_TYPE, IFptr.LIBFPTR_UT_CONFIGURATION)
        fptr.queryData()
        configuration = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)
        releaseVersion = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_RELEASE_VERSION)

        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_UNIT_VERSION)
        fptr.setParam(IFptr.LIBFPTR_PARAM_UNIT_TYPE, IFptr.LIBFPTR_UT_TEMPLATES)
        fptr.queryData()
        templates = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)

        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_UNIT_VERSION)
        fptr.setParam(IFptr.LIBFPTR_PARAM_UNIT_TYPE, IFptr.LIBFPTR_UT_CONTROL_UNIT)
        fptr.queryData()
        controlUnit = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)

        fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_UNIT_VERSION)
        fptr.setParam(IFptr.LIBFPTR_PARAM_UNIT_TYPE, IFptr.LIBFPTR_UT_BOOT)
        fptr.queryData()
        boot = fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)

        fptr.getRemoteServerInfo()

        serverVersion = fptr.getParamString(IFptr.LIBFPTR_PARAM_RPC_SERVER_VERSION)
        driverVersion = fptr.getParamString(IFptr.LIBFPTR_PARAM_RPC_DRIVER_VERSION)
        OS = fptr.getParamString(IFptr.LIBFPTR_PARAM_RPC_SERVER_OS)
        fptr.close()

        # "----------------------------------------------------"

        with open('/linuxcash/logs/current/ATOL5_info_' + usb, 'w+') as log:
            log.write('-' * 5 + 'INT' + '-' * 5 + '\n')
            log.write('operatorID: ' + str(operatorID) + '\n')
            log.write('logicalNumber: ' + str(logicalNumber) + '\n')
            log.write('shiftState: ' + str(shiftState) + '\n')
            log.write('model: ' + str(model) + '\n')
            log.write('mode: ' + str(mode) + '\n')
            log.write('submode: ' + str(submode) + '\n')
            log.write('receiptNumber: ' + str(receiptNumber) + '\n')
            log.write('documentNumber: ' + str(documentNumber) + '\n')
            log.write('shiftNumber: ' + str(shiftNumber) + '\n')
            log.write('receiptType: ' + str(receiptType) + '\n')
            log.write('lineLength: ' + str(lineLength) + '\n')
            log.write('lineLengthPix: ' + str(lineLengthPix) + '\n\n')
            log.write('inn: ' + str(inn) + '\n\n')

            log.write('-' * 5 + 'BOOL' + '-' * 5 + '\n')
            log.write('isFiscalDevice: ' + str(isFiscalDevice) + '\n')
            log.write('isFiscalFN: ' + str(isFiscalFN) + '\n')
            log.write('isFNPresent: ' + str(isFNPresent) + '\n')
            log.write('isInvalidFN: ' + str(isInvalidFN) + '\n')
            log.write('isCashDrawerOpened: ' + str(isCashDrawerOpened) + '\n')
            log.write('isPaperPresent: ' + str(isPaperPresent) + '\n')
            log.write('isPaperNearEnd: ' + str(isPaperNearEnd) + '\n')
            log.write('isCoverOpened: ' + str(isCoverOpened) + '\n')
            log.write('isPrinterConnectionLost: ' + str(isPrinterConnectionLost) + '\n')
            log.write('isPrinterError: ' + str(isPrinterError) + '\n')
            log.write('isCutError: ' + str(isCutError) + '\n')
            log.write('isPrinterOverheat: ' + str(isPrinterOverheat) + '\n')
            log.write('isDeviceBlocked: ' + str(isDeviceBlocked) + '\n\n')

            # log.write('-'*5 + 'DATETIME' + '-'*5 +'\n')
            # log.write(dateTime)

            log.write('-' * 5 + 'STRING' + '-' * 5 + '\n')
            log.write('serialNumber: ' + serialNumber + '\n')
            log.write('modelName: ' + modelName + '\n')
            log.write('firmware: ' + firmware + '\n')

            log.write('\n' + '-' * 5 + 'REGISTRATION' + '-' * 5 + '\n')
            log.write('ffdVersion: ' + str(ffdVersion) + '\n')
            log.write('fnsUrl: ' + str(fnsUrl) + '\n')
            log.write('organizationAddress: ' + str(organizationAddress) + '\n')
            log.write('organizationVATIN: ' + str(organizationVATIN) + '\n')
            log.write('organizationName: ' + str(organizationName) + '\n')
            log.write('organizationEmail: ' + str(organizationEmail) + '\n')
            log.write('paymentsAddress: ' + str(paymentsAddress) + '\n')
            log.write('registrationNumber: ' + str(registrationNumber) + '\n')
            log.write('machineNumber: ' + str(machineNumber) + '\n')
            log.write('ofdVATIN: ' + str(ofdVATIN) + '\n')
            log.write('ofdName: ' + str(ofdName) + '\n')

            log.write('\n' + '-' * 5 + 'SEREGA' + '-' * 5 + '\n')
            log.write('Прошивка: ' + str(firmware) + '\n')
            log.write('Версия конфигурации: ' + str(configuration) + '\n')
            log.write('releaseVersion: ' + str(releaseVersion) + '\n')
            log.write('Движок шаблонов: ' + str(templates) + '\n')
            log.write('Блок управления: ' + str(controlUnit) + '\n')
            log.write('Загрузчик: ' + str(boot) + '\n')

            # log.write('\n' + '-' * 5 + 'REMOTE' + '-' * 5 + '\n')
            # log.write('serverVersion: ' + str(serverVersion) + '\n')
            # log.write('driverVersion: ' + str(driverVersion) + '\n')
            # log.write('OS: ' + str(OS) + '\n')

        name = os.uname()[1]
        insert(name=name, firmware=firmware, configuration=configuration, templates=templates, controlUnit=controlUnit, boot=boot,
               serialNumber=serialNumber, inn=organizationVATIN)
    except Exception as e:
        fptr.close()
        logging.exception(e)
        sys.exit(1)
