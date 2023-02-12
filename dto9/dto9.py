#usr/bin/python2.7
# -*- coding: utf-8 -*-

# import web
import sys
import os
import json
import logging

from conf import *  # загружаем настройки
import dto9fptr  # загружаем заголовки драйвера


def DeviceSetup(driver, params):
    driver.put_DeviceSingleSetting("Port", params["Port"])
    driver.put_DeviceSingleSetting("IPAddress", params["IPAddress"])
    driver.put_DeviceSingleSetting("IPPort", params["IPPort"])
    driver.put_DeviceSingleSetting("Model", params["Model"])
    driver.put_DeviceSingleSetting("Protocol", params["Protocol"])
    driver.put_DeviceSingleSetting("AccessPassword", params["AccessPassword"])
    driver.put_DeviceSingleSetting("UserPassword", params["UserPassword"])
    driver.put_DeviceSingleSetting("Protocol", params["Protocol"])
    driver.put_DeviceSingleSetting('SearchDir', os.path.dirname(DTO_LIB_NAME))
    driver.ApplySingleSettings()
    driver.put_DeviceEnabled(True)
    return 0


def GetCurrentParamDevice(driver):
    result = driver.GetStatus()
    if result[0] != 0:
        print(t_err + unicode(result[1]) + t_off)
        logging.info(result[1])
        exit(1)
    result = driver.get_DeviceSettings()
    print(t_mess + 'Текущие настройки: ' + t_off + str(result))
    if str(result) == "None":
        etxt = "Драйвер не подключился к устройству"
        print(t_err + etxt + t_off)
        logging.info(etxt)
        exit(1)
    return result


def print_check(driver, check_data):
    res = 0
    mess = "check_data: " + str(check_data)

    print(t_mess + mess + t_off)
    logging.info(mess)

    result = driver.put_DeviceEnabled(True)
    logging.info("put device enabled: " + repr(result).decode("unicode_escape"))
    result_code = driver.get_ResultCode()
    result_description = driver.get_ResultDescription()
    if result_code != 0:
        logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
        logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
        print(t_err + str(result_code) + t_off)
        print(t_err + result_description + t_off)
        exit(1)
    print(t_ok + result_description + t_off)

    print(t_mess + "- переводим ККМ в режим регистрации" + t_off)
    result = driver.put_Mode(1)
    logging.info("put mode 1:" + repr(result).decode("unicode_escape"))
    result_code = driver.get_ResultCode()
    result_description = driver.get_ResultDescription()
    if result_code != 0:
        logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
        logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
        print(t_err + str(result_code) + t_off)
        print(t_err + result_description + t_off)
    print(t_ok + result_description + t_off)

    print(t_mess + "- создаем новый документ" + t_off)
    result = driver.NewDocument()
    logging.info("new document:" + repr(result).decode("unicode_escape"))
    result_code = driver.get_ResultCode()
    result_description = driver.get_ResultDescription()
    if result_code == -3822:
        logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
        logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
        logging.error("  trying close shift...")
        print(t_err + str(result_code) + t_off)
        print(t_err + result_description + t_off)
        exit(1)
    print(t_ok + result_description + t_off)

    print(t_mess + "- выставляем что тип чека - продажа" + t_off)
    result = driver.put_CheckType(1)
    logging.info("put check type:" + repr(result).decode("unicode_escape"))
    result_code = driver.get_ResultCode()
    result_description = driver.get_ResultDescription()
    if result_code != 0:
        logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
        logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
        print(t_err + str(result_code) + t_off)
        print(t_err + result_description + t_off)
        exit(1)
    print(t_ok + result_description + t_off)

    print(t_mess + "- открываем чек" + t_off)
    result = driver.OpenCheck()
    logging.info("open check:" + repr(result).decode("unicode_escape"))
    result_code = driver.get_ResultCode()
    result_description = driver.get_ResultDescription()
    if result_code != 0:
        logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
        logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
        print(t_err + str(result_code) + t_off)
        print(t_err + result_description + t_off)
        exit(1)
    print(t_ok + result_description + t_off)

    print(t_mess + "- регистрация позиций" + t_off)
    logging.info("registering positions...")

    for position in check_data:
        print("--- №:" + str(position["num"]))
        print("--- Дата:" + str(position["docdate"]))
        print("--- Всего:" + str(position["summdoc"]))
        for goods in position["goods"]:
            print("---- Товар:" + str(goods["name"]))
            result = driver.put_Name(goods["name"].decode('utf8'))
            print("---- Цена:" + str(goods["price"]))
            result = driver.put_Price(goods["price"])
            print("---- Количество:" + str(goods["quiantity"]))
            result = driver.put_Quantity(goods["quiantity"])
            result = driver.put_TaxNumber(3)
            print("---- Сумма:" + str(goods["summ"]))
            result_code = driver.put_PositionSum(goods["summ"])
            print("---- Регистрация позиции:")
            result_code = driver.Registration()
            if result_code[0] != 0:
                logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
                logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
                print(t_err + str(result_code) + t_off)
                print(t_err + result_description + t_off)
                exit(1)

        print(t_mess + "- прием оплаты" + t_off)
        result = driver.put_TypeClose(1)  # Тип оплаты - Платежная карта
        logging.info("put type close:" + repr(result).decode("unicode_escape"))
        result_code = driver.get_ResultCode()
        result_description = driver.get_ResultDescription()
        if result_code != 0:
            logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
            logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
            print(t_err + str(result_code) + t_off)
            print(t_err + result_description + t_off)
            exit(1)

        print(t_mess + "- сумма оплаты" + t_off)
        result = driver.put_Summ(position["summdoc"])
        logging.info("put summ:" + repr(result).decode("unicode_escape"))
        result_code = driver.get_ResultCode()
        result_description = driver.get_ResultDescription()
        if result_code != 0:
            logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
            logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
            print(t_err + str(result_code) + t_off)
            print(t_err + result_description + t_off)
            exit(1)

        print(t_mess + "- регистрация платежа" + t_off)
        result = driver.Payment()
        logging.info("pyment:" + repr(result).decode("unicode_escape"))
        result_code = driver.get_ResultCode()
        result_description = driver.get_ResultDescription()
        if result_code != 0:
            logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
            logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
            print(t_err + str(result_code) + t_off)
            print(t_err + result_description + t_off)
            exit(1)

        print(t_mess + "- проверка фиксации " + t_off)
        result = driver.get_ResultCode()
        logging.info("payment result code:" + repr(result).decode("unicode_escape"))
        result_code = driver.get_ResultCode()
        result_description = driver.get_ResultDescription()
        if result_code != 0:
            logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
            logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
            print(t_err + str(result_code) + t_off)
            print(t_err + result_description + t_off)
            exit(1)

    print(t_mess + "- закрытие чека " + t_off)
    result = driver.CloseCheck()
    logging.info("close check:" + repr(result).decode("unicode_escape"))
    result_code = driver.get_ResultCode()
    result_description = driver.get_ResultDescription()
    if result_code != 0:
        logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
        logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
        print(t_err + str(result_code) + t_off)
        print(t_err + result_description + t_off)
        exit(1)

    print(t_mess + "- получение номера чека " + t_off)
    result = driver.get_CheckNumber()
    logging.info("check number:" + repr(result).decode("unicode_escape"))
    result_code = driver.get_ResultCode()
    result_description = driver.get_ResultDescription()
    if result_code != 0:
        logging.error("  result code:" + repr(result_code).decode("unicode_escape"))
        logging.error("  result description:" + repr(result_description).decode("unicode_escape"))
        print(t_err + str(result_code) + t_off)
        print(t_err + result_description + t_off)
        exit(1)

    exit(1)
    return res


os.environ['LD_LIBRARY_PATH'] = os.path.dirname(os.path.abspath('/linuxcash/net/server/server/All/Artur/'))
# logging.info(os.path.dirname(os.path.realpath(__file__)))
# logging.info(os.environ)

# print(t_mess + "Фискализация чеков v 1.0 (c) 2018 by Pavel Gribov http://грибовы.рф" + t_off)

DTO_LIB_NAME = '/opt/ATOL/drivers9/bin/libfptr.so'
VERSION = 15
driver = dto9fptr.Fptr(DTO_LIB_NAME, VERSION)

print(t_mess + "Драйвер:" + t_off + str(driver))
print(t_mess + "Параметры:" + t_off + str(params))

# устанавливаем параметры соединения
DeviceSetup(driver, params)
# Читаем текущие настройки
cursettings = GetCurrentParamDevice(driver)
# печатаем чек
# check_data = []
#
# goodsa = []
# goodsa.append({"name": "Телематические услуги связи 1", "price": 0.01, "quiantity": 1, "summ": 0.01});
# goodsa.append({"name": "Телематические услуги связи 2", "price": 0.01, "quiantity": 1, "summ": 0.01});
#
# check_data.append({"num": "1", "docdate": "07.05.2018", "summdoc": 0.02, "goods": goodsa});
#
# print(check_data)
# print_check(driver, check_data)

driver.Beep()

# Закончили работу
driver.put_DeviceEnabled(False)
del driver
