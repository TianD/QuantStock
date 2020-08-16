# coding:utf-8
import datetime
import time

import pandas as pd
import requests
import sqlite3
from StringIO import StringIO


def request_stock(query_datetime, stock_list):
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


def request_date_is_holiday(day):
    server_url = "http://timor.tech/api/holiday/info/%s" % day
    req = requests.get(server_url)
    data = req.json()
    is_not_holiday = data.get('holiday') == None
    is_workday = data.get('type').get('type') == 0
    if is_not_holiday and is_workday:
        return True
    return False


def format_code_to_163(stock_code):
    if stock_code.starts_with('6'):
        stock_code = '0'+stock_code
    elif stock_code.starts_with('0'):
        stock_code = '1'+stock_code
    else:
        pass
    return stock_code


def format_code_to_sina(stock_code):
    if stock_code.starts_with('6'):
        stock_code = 'sh' + stock_code
    elif stock_code.starts_with('0'):
        stock_code = 'sz' + stock_code
    else:
        pass
    return stock_code


def get_history_data(stock_code, start_date, end_date):
    url_template = "http://quotes.money.163.com/service/chddata.html?code={formatted_stock_code}&start={start_date}&end={end_date}&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP"
    formatted_stock_code = format_code_to_163(stock_code)
    server_url = url_template.format(formatted_stock_code=formatted_stock_code, start_date=start_date,end_date=end_date)
    req = requests.get(server_url)
    content = req.content.decode('GBK')
    data = StringIO(content)
    return pd.read_csv(data, sep=",")


if __name__ == '__main__':
    day = '2020-08-12'
    query_time = time.strptime(day, '%Y-%m-%d')
    query_time = time.mktime(query_time)
    print(request_stock(query_time, 'sz002668'))
    print(request_date_is_holiday(day))
    print(get_history_data())