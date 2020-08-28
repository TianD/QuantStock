#!/usr/bin/env python
# coding=utf-8
# Copyright (c) 2019 MoreVFX. All rights reserved.
# created by huiguoyu @ 2020/8/27 20:30
import requests
from PySide import QtGui
from PySide import QtCore

from core.StockGetter import format_code_to_sina, get_history_data


class CustomSelectDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(CustomSelectDialog, self).__init__(parent)

        self.setupUi(self)
        self.initData()
        self.bindFun()

    def setupUi(self, parent):
        self.setWindowTitle(u'添加自选股')
        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.stock_layout = QtGui.QHBoxLayout()
        self.stock_label = QtGui.QLabel(u'股票代码')
        self.stock_layout.addWidget(self.stock_label)
        self.stock_edit = QtGui.QLineEdit()
        self.stock_layout.addWidget(self.stock_edit)
        self.stock_name_label = QtGui.QLabel('')
        self.stock_layout.addWidget(self.stock_name_label)
        self.main_layout.addLayout(self.stock_layout)
        
        self.bid_layout = QtGui.QHBoxLayout()
        self.bid_label = QtGui.QLabel(u'买入价')
        self.bid_layout.addWidget(self.bid_label)
        self.bid_edit = QtGui.QLineEdit()
        self.bid_layout.addWidget(self.bid_edit)
        self.main_layout.addLayout(self.bid_layout)

        self.ok_btn = QtGui.QPushButton('ok')
        self.main_layout.addWidget(self.ok_btn)

    def initData(self):
        pass

    def bindFun(self):
        self.stock_edit.textChanged.connect(self.get_stock_name)
        self.ok_btn.clicked.connect(self.accept)

    def get_stock_name(self, code):
        stock_name = ''
        sina_code = format_code_to_sina(code)
        response = requests.get('http://hq.sinajs.cn/list=%s' % sina_code)
        if response.status_code == 200:
            stock_list = response.text.split(';\n')
            result = []
            for index, stock in enumerate(stock_list[:-1]):
                _, stock_detail = stock.split('=')
                stock_detal_list = stock_detail.split(',')
                stock_name = stock_detal_list[0][1:]
        self.stock_name_label.setText(stock_name)

    def get_stock_detail(self):
        code = self.stock_edit.text()
        name = self.stock_name_label.text()
        bid_price = float(self.bid_edit.text())
        retrospect_days = 1
        history_data = get_history_data(code)[:retrospect_days]
        top_price = max([float(hd[6]) for hd in history_data])
        bottom_price = min([float(hd[5]) for hd in history_data])
        return [code, name, bid_price, retrospect_days, top_price, bottom_price]

    @classmethod
    def run(cls, parent):
        obj = cls(parent)
        flag = obj.exec_()
        return flag, obj