# coding:utf-8
import datetime
import time

import requests
import sqlite3


def request_stock(query_datetime, stock_list):
    response = requests.get('http://hq.sinajs.cn/rn=%s&list=%s' % (query_datetime, stock_list))
    if response.status_code == 200:
        stock_list = response.text.split(';\n')
        result = []
        for stock in stock_list[:-1]:
            stock_code, stock_detail = stock.split('=')
            stock_code = stock_code.split('var ')[1].split('_')[-1]
            stock_detal_list = stock_detail.split(',')
            result.append([stock_code] + stock_detal_list)

    return result


def request_date_is_holiday(day):
    server_url = "http://timor.tech/api/holiday/info/%s" % day
    req = requests.get(server_url)
    data = req.json()
    is_not_holiday = data.get('holiday') == None
    is_workday = data.get('type').get('type') == 0
    if is_not_holiday and is_workday:
        return True
    return False

if __name__ == '__main__':
    day = '2020-08-12'
    query_time = time.strptime(day, '%Y-%m-%d')
    query_time = time.mktime(query_time)
    print(request_stock(query_time ,'sz002668'))
    print(request_date_is_holiday(day))