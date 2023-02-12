#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import calendar

from bs4 import BeautifulSoup
import requests, os, re, sys
import datetime

sys.path.append(os.path.abspath("/root/ArturAuto"))
from lib.UTM import UTM


class Logger:
    def __init__(self, path, port, inn):
        self.path = path
        self.port = port
        self.inn = inn
        self.name = "-".join(os.uname()[1].split('-')[1:3])

    def message(self, message):
        with open(self.path, 'a+') as log:
            log.write("{} {} {} {} - {}\n".format(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S'), self.port, self.inn, self.name, message))


def delete_previous_docs(utm):
    docs = sorted([i for i in utm.get_all_opt_URLS_text() if re.findall('ReplyRests_v2', i)])
    if docs:
        for doc in docs[:-2]:
            requests.delete(doc)


def delete_notification_file(notification_file):
    if os.path.exists(notification_file):
        os.remove(notification_file)
        print("Удалил файл уведомления '{}'".format(notification_file))


def check_work_days_blackPClist():
    day_of_week = datetime.datetime.today().weekday()
    name = os.uname()[1].split("-")[1]
    current_hour = datetime.datetime.now().hour

    if name in ['1243', '72', '231', '37', '142', '270', '453', '499', '470', '321', '928', '653', '383', '495']:
        print("Комп в черном списке, уведомление не будет показано")
        return False

    if day_of_week in [5, 6] or current_hour >= 17 or current_hour < 9:
        print("Не рабочее время, уведомление не будет показано")
        return False

    return True


def ticket_answer(Response):
    if Response.status == "Accepted":
        print("\033[0;32mStatus: {}\n message: {}\033[0m".format(Response.status, Response.message))
    else:
        print("\033[0;31mStatus: {}\n message: {}\033[0m".format(Response.status, Response.message))


def get_time_maxReplyRest_and_lastReply(utm):
    ReplyRests = [url for url in utm.get_all_opt_URLS_text() if re.findall('ReplyRest', url)]
    if ReplyRests:
        last_reply = max(ReplyRests)
        date_text = BeautifulSoup(requests.get(last_reply).text, 'xml').find('RestsDate').text
        if re.findall('\.', date_text):
            ReplyRest_date = datetime.datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%S.%f")
        else:
            ReplyRest_date = datetime.datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%S")
    else:
        last_reply = False
        ReplyRest_date = False
    return ReplyRest_date, last_reply


# url = Ссылка на файл в УТМ, type_notification если 1 то конец квартала, если 2 то начало следующего квартала
def notification(url, notification_file, type_notification):
    logger = Logger('/linuxcash/net/server/server/logs/beerBalance.log', utm.port, utm.get_cash_info()['INN'])
    bottle_sum = sum(int(q.text.split('.')[0]) for q in BeautifulSoup(requests.get(url).text, 'xml').findAll('Quantity'))
    logger.message("Бутылок на пивных остатках: {}".format(bottle_sum))
    print("Бутылок на пивных остатках: {}".format(bottle_sum))

    if not check_work_days_blackPClist():
        return

    if bottle_sum > 100:  # or datetime.now()- timedelta(days=1) > time_create
        with open(notification_file, 'w+') as notification:
            if type_notification == 0:
                delete_notification_file(notification_file)
            if type_notification == 1:
                notification.write("У вас {} бутылок пивной продукции на ИП остатках. Подробности можете узнать позвонив на номер +7 905 319-28-49".format(bottle_sum))
            if type_notification == 2:
                notification.write("На {} на ИП остатках числится {} бутылок пивной продукции. Будьте внимательны при сдаче декларации. С 1 по 10 число.".format(
                    datetime.datetime.strftime(datetime.datetime.now(), '%d.%m'), bottle_sum))
    else:
        delete_notification_file(notification_file)


def dump_ReplyRest(url):
    current_date = datetime.datetime.now()
    monthrange = calendar.monthrange(current_date.year, current_date.month)[1]
    server_path_dir = os.path.join('/linuxcash/net/server/server/', 'balanceBeer', os.uname()[1].split('-')[1])
    local_dir = os.path.join(os.path.dirname(__file__), 'dumps')
    dump_file = "{}_{}.log".format(url.split("/")[5], url.split("/")[6])
    text_url = BeautifulSoup(requests.get(url).text, 'xml')

    if current_date.day == monthrange:
        if not os.path.exists(server_path_dir):
            os.makedirs(server_path_dir)
        with open(os.path.join(server_path_dir, dump_file), 'w+') as rr:
            rr.write(text_url.prettify())

    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    with open(os.path.join(local_dir, dump_file), 'w+') as rr:
        rr.write(text_url.prettify())


def main(utm, type_notification):
    """
    type_notification это вид сообщения, где
    0 - нету уведомления
    1 - конец квартала
    2 - начала следующего квартала
    """
    name = "{}-{}".format(os.uname()[1].split("-")[1], os.uname()[1].split("-")[2])
    inn = utm.get_cash_info()["INN"]
    notifications_file = '/root/notifications/beerBalance'

    print("Проверяю даты всех ReplyRest")
    last_replyrest = get_time_maxReplyRest_and_lastReply(utm)
    if last_replyrest[0]:
        if datetime.datetime.now() < last_replyrest[0] + datetime.timedelta(hours=1):
            time_replyrest = datetime.datetime.strftime(last_replyrest[0], '%H:%M:%S')
            bottle_sum = sum(int(q.text.split('.')[0]) for q in BeautifulSoup(requests.get(last_replyrest[1]).text, 'xml').findAll('Quantity'))
            print("Еще не прошел час с последнего ReplyRest. Время последнего ReplyRest {}".format(time_replyrest))
            print("Бутылок в последнем ReplyRest: {}".format(bottle_sum))
            exit(0)

    ReplyRest = utm.wait_answer(utm.send_QueryRests_v2())
    if re.findall('ReplyRests_v2', ReplyRest):
        delete_previous_docs(utm)
        notification(ReplyRest, notifications_file, type_notification)
        dump_ReplyRest(ReplyRest)
    elif re.findall('Ticket', ReplyRest):
        ticket_answer(utm.parse_ticket_result(ReplyRest))
    else:
        print("Неизвестный ответ '{}'".format(ReplyRest))


if __name__ == '__main__':
    dates_start_kvartal = ['04-01', '04-02', '04-03', '04-04', '04-05', '04-06', '04-07', '04-08', '04-09', '04-10', '07-01', '07-02', '07-03', '07-04', '07-05', '07-06',
                           '07-07', '07-08', '07-09', '07-10', '10-01', '10-02', '10-03', '10-04', '10-05', '10-06', '10-07', '10-08', '10-09', '10-10', '01-01', '01-02',
                           '01-03', '01-04', '01-05', '01-06', '01-07', '01-08', '01-09', '01-10']
    dates_end_kvartal = ['03-31', '03-30', '03-29', '03-28', '03-27', '03-26', '03-25', '03-24', '06-30', '06-29', '06-28', '06-27', '06-26', '06-25', '06-24', '06-23',
                         '09-30', '09-29', '09-28', '09-27', '09-26', '09-25', '09-24', '09-23', '12-31', '12-30', '12-29', '12-28', '12-27', '12-26', '12-25', '12-24']

    for port in ['8082', '18082']:
        utm = UTM(port=port)
        if not utm.get_cash_info()["KPP"]:
            try:
                current_date = datetime.datetime.strftime(datetime.datetime.now(), '%m-%d')
                if current_date in dates_start_kvartal:
                    main(utm, 1)
                elif current_date in dates_end_kvartal:
                    main(utm, 2)
                else:
                    main(utm, 0)
            except Exception as e:
                logger = Logger('/linuxcash/net/server/server/logs/beerBalance.log', utm.port, utm.get_cash_info()['INN'])
                logger.message(e)
