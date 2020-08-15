# coding:utf-8
import datetime

import requests
import sqlite3


def request_stock(self):
    now = datetime.datetime.now()
    stock_text = self.stock_lineEdit.text()
    response = requests.get('http://hq.sinajs.cn/list=%s' % stock_text)
    if response.status_code == 200:
        stock_list = response.text.split(';\n')
        result = []
        for stock in stock_list[:-1]:
            stock_code, stock_detail = stock.split('=')
            stock_code = stock_code.split('var ')[1].split('_')[-1]
            stock_detal_list = stock_detail.split(',')
            try:
                temp_list = [
                    stock_code,
                    stock_detal_list[0],
                    stock_detal_list[1],
                    stock_detal_list[2],
                    stock_detal_list[3],
                    stock_detal_list[4],
                    stock_detal_list[5],
                    stock_detal_list[30],
                    stock_detal_list[31]
                ]
                result.append(temp_list)
            except:
                pass