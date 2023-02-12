# -*- coding: utf-8 -*-
import requests
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
from lib import CURL
import time
from collections import namedtuple


class UTM():
    def __init__(self, port, ip="localhost"):
        self.port = port
        self.ip = ip

    # Возвращает в dict (status, message)
    def parse_ticket_result(self, ticket):
        Response = namedtuple('Response', 'status message')
        ticket = requests.get(ticket).text
        tree = ET.fromstring(ticket)
        try:
            status = tree.find('*/*/*/{http://fsrar.ru/WEGAIS/Ticket}OperationResult').text
            message = tree.find('*/*/*/{http://fsrar.ru/WEGAIS/Ticket}OperationComment').text.strip()
        except:
            status = tree.find('*/*/*/{http://fsrar.ru/WEGAIS/Ticket}Conclusion').text
            message = tree.find('*/*/*/{http://fsrar.ru/WEGAIS/Ticket}Comments').text.strip()
        return Response(status, message)

    def wait_answer(self, url, timeout=15):
        max_time = 1500
        while max_time > 0:
            print("-- Ожидание ответа от: {}".format(url))
            opt_urls = BeautifulSoup(requests.get("http://" + self.ip + ":" + self.port + "/opt/out").text, 'xml').findAll("url")
            for opt_url in opt_urls:
                if opt_url.get('replyId') == url:
                    return opt_url.text
            max_time = 1500 - timeout
            time.sleep(timeout)

    def get_all_opt_URLS_text(self):
        return [url.text for url in BeautifulSoup(requests.get("http://" + self.ip + ":" + self.port + "/opt/out").text, 'xml').findAll("url")]

    def get_Waybill_and_FORM2REGINFO(self):
        """Возвращает [ссылку на FORM2REGINFO, ссылку на Waybill_v4, номер ттн егаис]"""
        URLS = self.get_all_opt_URLS_text()
        urls_form = [url for url in URLS if re.findall("FORM2REGINFO", url)]
        urls_wb = [url for url in URLS if re.findall("WayBill_v4", url)]
        if len(urls_form) == 0  and len(urls_wb) == 0:
            print("\033[31m{}\033[0m".format("Нету накладных"))
            exit()
        if len(urls_form) == 0:
            print("\033[31m{}\033[0m".format("Нету FORM2REGINFO"))
            exit()
        if len(urls_wb) == 0:
            print("\033[31m{}\033[0m".format("Нету Waybill_v4"))
            exit()
        ttns = []
        for url_form in urls_form:
            req = requests.get(url_form).text
            TTN = ET.fromstring(req).find('*/*/*/{http://fsrar.ru/WEGAIS/TTNInformF2Reg}WBRegId').text
            WBNUMBER = ET.fromstring(req).find('*/*/*/{http://fsrar.ru/WEGAIS/TTNInformF2Reg}WBNUMBER').text
            for url_wb in urls_wb:
                req = requests.get(url_wb).text
                NUMBER = ET.fromstring(req).find('*/*/*/{http://fsrar.ru/WEGAIS/TTNSingle_v4}NUMBER').text
                if NUMBER == WBNUMBER:
                    ttns.append("{} {} {}".format(url_form, url_wb, TTN).split())
        return ttns

    def send_QueryRests_v2(self):
        self.check_utm_error()
        files = {
            'xml_file': CURL.QueryRests_v2(self.get_fsrar())
        }
        response = requests.post('http://' + self.ip + ':' + self.port + '/opt/in/QueryRests_v2', files=files)
        if response.status_code == 200:
            request_id = BeautifulSoup(response.text, "xml").find("url").text
            print("\033[32m{}, request_id: {}\033[0m".format("QueryRests_v2 отправлен", request_id))
            return request_id
        else:
            print("\033[31m{}\033[0m".format("QueryRests_v2 не отправлен"))
            print("\033[31m{}\033[0m".format("HTTP code != 200 --- " + "status code = " + str(response.status_code)))
            exit(1)

    def send_QueryRestsShop_V2(self):
        self.check_utm_error()
        files = {
            'xml_file': CURL.QueryRestsShop_V2(self.get_fsrar())
        }
        response = requests.post('http://' + self.ip + ':' + self.port + '/opt/in/QueryRestsShop_V2', files=files)
        if response.status_code == 200:
            request_id = BeautifulSoup(response.text, "xml").find("url").text
            print("\033[32m{}, request_id: {}\033[0m".format("QueryRestsShop_V2 отправлен", request_id))
            return request_id
        else:
            print("\033[31m{}\033[0m".format("QueryRestsShop_V2 не отправлен"))
            print("\033[31m{}\033[0m".format("HTTP code != 200 --- " + "status code = " + str(response.status_code)))
            exit(1)

    def send_ActWriteOff_v3(self, QueryRests_v2_xml_string):
        self.check_utm_error()
        if QueryRests_v2_xml_string:
            result = []
            products = ET.fromstring(QueryRests_v2_xml_string).findall("*/*/*/{http://fsrar.ru/WEGAIS/ReplyRests_v2}StockPosition")
            for identity, product in enumerate(products, 1):
                body = """                <awr:Position>
                    <awr:Identity>{}</awr:Identity>
                    <awr:Quantity>{}</awr:Quantity>
                    <awr:InformF1F2>
                        <awr:InformF2>
                            <pref:F2RegId>{}</pref:F2RegId>
                        </awr:InformF2>
                    </awr:InformF1F2>
                </awr:Position>\n""".format(str(identity), product.find("{http://fsrar.ru/WEGAIS/ReplyRests_v2}Quantity").text,
                                            product.find("{http://fsrar.ru/WEGAIS/ReplyRests_v2}InformF2RegId").text)
                result.append(body)

            files = {
                'xml_file': CURL.ActWriteOff_v3(self.get_fsrar(), result)
            }
            response = requests.post('http://' + self.ip + ':' + self.port + '/opt/in/ActWriteOff_v3', files=files)
            if response.status_code == 200:
                request_id = BeautifulSoup(response.text, "xml").find("url").text
                print("\033[32m{}, request_id: {}\033[0m".format("ActWriteOff_v3 отправлен", request_id))
                return request_id
            else:
                print("\033[31m{}\033[0m".format("ActWriteOff_v3 не отправлен"))
                print("\033[31m{}\033[0m".format("HTTP code != 200 --- " + "status code = " + str(response.status_code)))
                exit(1)
        else:
            print("\033[31m{}\033[0m".format("QueryRests_v2_xml_string not True"))
            exit(1)

    def send_ActWriteOffShop_v2(self, QueryRestsShop_V2_xml_string):
        self.check_utm_error()
        if QueryRestsShop_V2_xml_string:
            result = []
            tree = ET.fromstring(QueryRestsShop_V2_xml_string)
            for count, el in enumerate(tree.findall('.//{http://fsrar.ru/WEGAIS/ReplyRestsShop_v2}ShopPosition'), 1):
                try:
                    Quantity = el.find('{http://fsrar.ru/WEGAIS/ReplyRestsShop_v2}Quantity').text
                    FullName = el.find('.//{http://fsrar.ru/WEGAIS/ProductRef_v2}FullName').text
                    AlcCode = el.find('.//{http://fsrar.ru/WEGAIS/ProductRef_v2}AlcCode').text
                    Capacity = el.find('.//{http://fsrar.ru/WEGAIS/ProductRef_v2}Capacity').text
                    UnitType = el.find('.//{http://fsrar.ru/WEGAIS/ProductRef_v2}UnitType').text
                    AlcVolume = el.find('.//{http://fsrar.ru/WEGAIS/ProductRef_v2}AlcVolume').text
                    ProductVCode = el.find('.//{http://fsrar.ru/WEGAIS/ProductRef_v2}ProductVCode').text
                    ClientRegId = el.find('.//{http://fsrar.ru/WEGAIS/ClientRef_v2}ClientRegId').text
                    INN = el.find('.//{http://fsrar.ru/WEGAIS/ClientRef_v2}INN').text
                    KPP = el.find('.//{http://fsrar.ru/WEGAIS/ClientRef_v2}KPP').text
                    FullName_UL = el.find('.//{http://fsrar.ru/WEGAIS/ClientRef_v2}FullName').text
                    ShortName = el.find('.//{http://fsrar.ru/WEGAIS/ClientRef_v2}ShortName').text
                    Country = el.find('.//{http://fsrar.ru/WEGAIS/ClientRef_v2}Country').text
                    RegionCode = el.find('.//{http://fsrar.ru/WEGAIS/ClientRef_v2}RegionCode').text
                    description = el.find('.//{http://fsrar.ru/WEGAIS/ClientRef_v2}description').text

                    position = """
                            <awr:Position>
                      <awr:Identity>{0}</awr:Identity>
                      <awr:Quantity>{1}</awr:Quantity>
                      <awr:Product>
                        <pref:FullName>{2}</pref:FullName>
                        <pref:AlcCode>{3}</pref:AlcCode>
                        <pref:Capacity>{4}</pref:Capacity>
                        <pref:UnitType>{5}</pref:UnitType>
                        <pref:AlcVolume>{6}</pref:AlcVolume>
                        <pref:ProductVCode>{7}</pref:ProductVCode>
                        <pref:Producer>
                          <oref:UL>
                            <oref:ClientRegId>{8}</oref:ClientRegId>
                            <oref:FullName>{9}"</oref:FullName>
                            <oref:ShortName>{10}</oref:ShortName>
                            <oref:INN>{11}</oref:INN>
                            <oref:KPP>{12}</oref:KPP>
                            <oref:address>
                              <oref:Country>{13}</oref:Country>
                              <oref:RegionCode>{14}</oref:RegionCode>
                              <oref:description>{15}</oref:description>
                            </oref:address>
                          </oref:UL>
                        </pref:Producer>
                      </awr:Product>
                    </awr:Position>
                    """.format(count, Quantity, FullName, AlcCode, Capacity, UnitType, AlcVolume, ProductVCode, ClientRegId, INN, KPP, FullName_UL, ShortName, Country,
                               RegionCode, description)
                    result.append(position)
                except Exception as e:
                    print(e)
            with open('test.xml', 'w', encoding='utf-8') as f:
                f.write(CURL.ActWriteOffShop_v2(self.get_fsrar(), result))
        #     files = {
        #         'xml_file': CURL.ActWriteOffShop_v2(self.get_fsrar(), result)
        #     }
        #     response = requests.post('http://' + self.ip + ':' + self.port + '/opt/in/ActWriteOffShop_v2', files=files)
        #     if response.status_code == 200:
        #         request_id = BeautifulSoup(response.text, "xml").find("url").text
        #         print("\033[32m{}, request_id: {}\033[0m".format("ActWriteOffShop_v2 отправлен", request_id))
        #         return request_id
        #     else:
        #         print("\033[31m{}\033[0m".format("ActWriteOffShop_v2 не отправлен"))
        #         print("\033[31m{}\033[0m".format("HTTP code != 200 --- " + "status code = " + str(response.status_code)))
        #         exit(1)
        # else:
        #     print("\033[31m{}\033[0m".format("QueryRests_v2_xml_string not True"))
        #     exit(1)

    def send_WayBillv4(self, TTN):
        """
        Отправляет акт приёма ТТН
        Принимает только одну накладную
        TTN = только цифры
        date = datetime.datetime
        port = порт на котором работает УТМ
        """
        self.check_utm_error()
        files = {
            'xml_file': CURL.WayBillAct_v4(TTN, self.get_fsrar())
        }
        response = requests.post('http://' + self.ip + ':' + self.port + '/opt/in/WayBillAct_v4', files=files)
        if response.status_code == 200:
            print("\033[32m{}\033[0m".format("Накладная " + str(TTN) + " отправлена"))
            print("request_id: " + BeautifulSoup(response.text, "xml").find("url").text)
        else:
            print("\033[31m{}\033[0m".format("Накладная " + str(TTN) + " не отправлена"))
            print("\033[31m{}\033[0m".format("HTTP code != 200 --- " + "status code = " + str(response.status_code)))

    def check_utm_error(self):
        try:
            status_UTM = requests.get('http://' + self.ip + ':' + self.port).ok
        except Exception as ex:
            print("\033[31m{}\033[0m".format(ex))
            status_UTM = False
        if not status_UTM:
            exit()

        request = requests.get('http://' + self.ip + ':' + self.port + "/home").text
        if re.findall("Проблемы с RSA", request):
            print("\033[31m{}\033[0m".format("Ошибка на УТМ " + self.port))
            exit()

    def get_accepted_ttn(self):
        """
        Отдаёт принятые ТТНки списком [[ttnNumber, ...]]
        """
        self.check_utm_error()
        urls = ET.fromstring(requests.get("http://" + self.ip + ":" + self.port + "/opt/out").text).findall("url")
        tickets = [line.text for line in urls if re.findall('Ticket', line.text)]
        result = []
        for tic in tickets:
            text = requests.get(tic).text
            if text:
                if re.findall('подтверждена', text):
                    ttn = re.findall('TTN-[0-9]+', text)[0]
                    result.append(re.findall('[0-9]+', ttn)[0])

        return result

    def get_ReplyNATTN(self):
        """
        Отдаёт ТТНки списком [[TTN, ttnNumber, %Y-%m-%d, shipperFsrar]]
        """
        self.check_utm_error()
        urls = BeautifulSoup(requests.get("http://" + self.ip + ":" + self.port + "/opt/out").text, 'xml').findAll("url")
        tickets = [line.text for line in urls if re.findall('ReplyNATTN', line.text)]
        for ticket in tickets:
            ReplyNATTN = BeautifulSoup(requests.get(ticket).text, 'xml')
            if tickets:
                try:
                    date_NATTN = ReplyNATTN.find("ReplyDate").text.split("T")[0]
                    if datetime.strftime(datetime.now(), "%Y-%m-%d") == date_NATTN:
                        TTNs = ReplyNATTN.findAll("WbRegID")
                        ttnNumber = ReplyNATTN.findAll("ttnNumber")
                        ttnDate = ReplyNATTN.findAll("ttnDate")
                        Shipper = ReplyNATTN.findAll("Shipper")

                        result = []
                        for index, ttn in enumerate(TTNs):
                            if re.findall("^0[5-9]", ttn.string.split("-")[1]):
                                ttn = ttn.string.split("-")[1] + " " + str(ttnNumber[index].text) + " " + str(
                                    ttnDate[index].text) + " " + str(Shipper[index].text)
                                result.append(ttn.split())
                        return result
                    else:
                        print("Дата ReplyNATTN больше суток " + date_NATTN)
                        exit()
                except Exception as ex:
                    print(ex)
                    return None
            else:
                print("Нету ReplyNATTN")
                exit()

        # return tickets #requests.get(tickets[0]).text

    def not_accepted_ttn(self):
        """
        Отдаёт ТТНки списком [[TTN, ttnNumber, %Y-%m-%d, shipperFsrar]]
        """
        self.check_utm_error()
        ReplyNATTN = self.get_ReplyNATTN()
        accepted_ttn = self.get_accepted_ttn()
        tickets_rejected_or_withdrawn = [ticket for ticket in self.get_all_opt_URLS_text() if re.findall('Ticket', ticket) if
                                         re.findall('отозвана|отказана', requests.get(ticket).text)]
        ttns_rejected_or_withdrawn = [re.findall('[0-9]+', self.parse_ticket_result(ttn).message)[0] for ttn in tickets_rejected_or_withdrawn]
        result = []
        if ReplyNATTN:
            for ttn in ReplyNATTN:
                if ttn[0] not in accepted_ttn and ttn[0] not in ttns_rejected_or_withdrawn:
                    result.append(ttn)

        return result

    def get_date_rutoken(self):
        self.check_utm_error()
        date_rutoken = json.loads(requests.get("http://" + self.ip + ":" + self.port + "/api/info/list").text)["gost"]["expireDate"].split("+")[0]
        date_rutoken = datetime.strptime(date_rutoken, "%Y-%m-%d %H:%M:%S ")
        return date_rutoken

    def get_name_rutoken(self):
        self.check_utm_error()
        name = json.loads(requests.get("http://" + self.ip + ":" + self.port + "/api/gost/orginfo").text)["cn"]
        return name

    def get_fsrar(self):
        self.check_utm_error()
        return BeautifulSoup(requests.get("http://" + self.ip + ":" + self.port + "/diagnosis").text, 'xml').find("CN").text

    def get_cash_info(self):
        """
        Возвращает JSON формат
        {ID, Owner_ID, Full_Name, Short_Name, INN, KPP, Country_Code, Region_Code, Dejure_Address, Fact_Address, isLicense, Version_ts, pass_owner_id}
        """
        self.check_utm_error()
        fsrar = self.get_fsrar()
        return [_ for _ in json.loads(requests.get("http://" + self.ip + ":" + self.port + "/api/rsa").text)["rows"] if _["Owner_ID"] == fsrar][0]


def main(port):
    utm = UTM(port="8082", ip="10.8.24.34")
    print(utm.get_Waybill_and_FORM2REGINFO())
    # tickets = [ticket for ticket in utm.get_all_opt_URLS_text() if re.findall('Ticket', ticket)]
    # for ticket in tickets:
    #     print(utm.parse_ticket_result(ticket))
    # RRSHOP = utm.wait_anwser(utm.send_QueryRestsShop_V2())
    # print(requests.get(RRSHOP).text)
    # utm.send_ActWriteOffShop_v2(requests.get("http://10.8.10.78:18082/opt/out/ReplyRestsShop_v2/43537").text)


if __name__ == "__main__":
    main("18082")
