# coding:utf-8
import datetime
import json
import time

import pandas as pd
import requests
import sqlite3
from StringIO import StringIO


def request_stock(stock_list):
    response = requests.get('http://hq.sinajs.cn/list=%s' % stock_list)
    if response.status_code == 200:
        stock_list = response.text.split(';\n')
        result = []
        for stock in stock_list[:-1]:
            stock_code, stock_detail = stock.split('=')
            stock_code = stock_code.split('var ')[1].split('_')[-1]
            stock_detal_list = stock_detail.split(',')
            result.append([stock_code] + stock_detal_list)

    return result


def request_date_is_tradeday(day):
    server_url = "http://timor.tech/api/holiday/info/%s" % day
    req = requests.get(server_url)
    data = req.json()
    is_not_holiday = data.get('holiday') == None
    is_workday = data.get('type').get('type') == 0
    if is_not_holiday and is_workday:
        return True
    return False

def retrospect_to_date(from_day, days):
    i = 0
    to_day = pd.to_datetime(from_day, format='%Y%m%d')
    while True:
        is_tradeday = request_date_is_tradeday(to_day.strftime('%Y-%m-%d'))
        if is_tradeday:
            i += 1
        if i >= days:
            return to_day.strftime('%Y%m%d')
        to_day = pd.to_datetime(to_day) - pd.Timedelta(1, 'day')

def format_code_to_163(stock_code):
    if stock_code.startswith('6'):
        stock_code = stock_code
    elif stock_code.startswith('0'):
        stock_code = '1'+stock_code
    else:
        pass
    return stock_code


def format_code_to_sina(stock_code):
    if stock_code.startswith('6'):
        stock_code = 'sh' + stock_code
    elif stock_code.startswith('0'):
        stock_code = 'sz' + stock_code
    else:
        pass
    return stock_code


def get_history_data(stock_code):
    url_template = "https://q.stock.sohu.com/hisHq?code=cn_{stock_code}&order=D&period=d"
    # formatted_stock_code = format_code_to_163(stock_code)
    server_url = url_template.format(stock_code=stock_code)
    req = requests.get(server_url)
    content = json.loads(req.content)
    return content[0].get('hq')


if __name__ == '__main__':
    day = '2020-08-12'
    # query_time = time.strptime(day, '%Y-%m-%d')
    # query_time = time.mktime(query_time)
    # print(request_stock(query_time, 'sz002668'))
    # print(request_date_is_tradeday(day))
    print(get_history_data('000858'))
    # print(retrospect_to_date(day, 5))