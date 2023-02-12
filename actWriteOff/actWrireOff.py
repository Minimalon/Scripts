#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests, os, re, logging, sys

sys.path.append(os.path.abspath("/root/ArturAuto"))
from lib.UTM import UTM


def ticket_answer(response):
    if response.status == "Accepted":
        print("\033[0;32mStatus: {}\n message: {}\033[0m".format(response.status, response.message))
    else:
        print("\033[0;31mStatus: {}\n message: {}\033[0m".format(response.status, response.message))

    logging.info("Status: {}, message: {}".format(response.status, response.message))


def nullification_first_register(utm):
    reply_rests = [url for url in utm.get_all_opt_URLS_text() if re.findall('ReplyRests_v2', url)]
    print("Нахожу все ReplyRests_v2 {}".format(reply_rests))
    if reply_rests:
        reply_rest = requests.get(max(reply_rests))
        logging.info("Беру последний ReplyRests_v2 {}".format(max(reply_rests)))
        print("Беру последний ReplyRests_v2 {}".format(max(reply_rests)))
    else:
        print("\033[0;31m{}\033[0m".format("Нету ни одного ReplyRests_v2"))
        reply_rest = utm.wait_answer(utm.send_QueryRests_v2())
    ticket = requests.get(utm.wait_answer(utm.send_ActWriteOff_v3(reply_rest.text))).text
    ticket_answer(utm.parse_ticket_result(ticket))


def nullification_second_register(utm):
    reply_rests_shops = [url for url in utm.get_all_opt_URLS_text() if re.findall('ReplyRestsShop_v2', url)]
    print("Нахожу все ReplyRestsShop_v2 {}".format(reply_rests_shops))
    if reply_rests_shops:
        reply_rests_shop = requests.get(max(reply_rests_shops))
        logging.info("Беру последний ReplyRestsShop_v2 {}".format(max(reply_rests_shop)))
        print("Беру последний ReplyRestsShop_v2 {}".format(max(reply_rests_shop)))
    else:
        print("\033[0;31m{}\033[0m".format("Нету ни одного ReplyRestsShop_v2"))
        reply_rests_shop = utm.wait_answer(utm.send_QueryRestsShop_V2())
    ticket = requests.get(utm.wait_answer(utm.send_ActWriteOffShop_v2(reply_rests_shop.text))).text
    ticket_answer(utm.parse_ticket_result(ticket))


def main():
    name = os.uname()[1]
    ports = ['8082', '18082']
    for port in ports:
        try:
            utm = UTM(port=port)
            if not utm.get_cash_info()["KPP"]:
                logging.basicConfig(level=logging.INFO, filename="/linuxcash/net/server/server/logs/ActWriteOff.log",
                                    format="%(asctime)s " + port + " " + name + " - %(message)s")
                nullification_first_register(utm)
                nullification_second_register(utm)
        except Exception as e:
            print(e)
            logging.exception(e)

if __name__ == '__main__':
    main()
