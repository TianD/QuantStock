#!/usr/bin/env python
# coding=utf-8
# created by huiguoyu @ 2020/7/21 13:11
import datetime
import os

import requests
from PySide import QtCore
from PySide import QtGui
from playsound import playsound


class StockModel(QtCore.QAbstractTableModel):

    def __init__(self, source_data=None, parent=None):
        super(StockModel, self).__init__(parent)
        self.__source_data = source_data or []

    @property
    def source_data(self):
        return self.__source_data

    @source_data.setter
    def source_data(self, value):
        if isinstance(value, list):
            self.__source_data = value
        else:
            raise TypeError('expected a list object, but got a %s object.' % type(value).__name__)

    @property
    def header_data(self):
        return [u'股票名称',
                u'买入价',
                u'今日开盘价',
                u'昨日收盘价',
                u'当前价格',
                u'今日最高价',
                u'今日最低价',
                u'日期',
                u'时间']

    def rowCount(self, parentIndex=QtCore.QModelIndex()):
        return len(self.source_data)

    def columnCount(self, parentIndex=QtCore.QModelIndex()):
        return len(self.header_data)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header_data[section]

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return
        row = index.row()
        column = index.column()
        key = self.header_data[column]
        if role == QtCore.Qt.DisplayRole:
            return self.source_data[row][column]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        pass

    def update_source_data(self, source_data):
        self.beginResetModel()
        self.source_data = source_data
        self.endResetModel()


class MainWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)
        self.initData()
        self.bindFun()
        self.request_timer.start()

    def setupUi(self, parent):
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle('StockWatcher')
        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.stock_lineEdit = QtGui.QLineEdit()
        self.main_layout.addWidget(self.stock_lineEdit)
        self.stock_tableView = QtGui.QTableView()
        self.stock_model = StockModel()
        self.stock_tableView.setModel(self.stock_model)
        self.main_layout.addWidget(self.stock_tableView)
        #
        self.request_timer = QtCore.QTimer()
        self.request_timer.setInterval(1000)
        #
        self.audio_thread = QtCore.QThread()
        self.audio_thread.run = self.play_sound
        self.audio_thread.start()
        #
        self.strategy_thread = QtCore.QThread()
        self.strategy_thread.run = self.caculate
        self.strategy_thread.start()

    def bindFun(self):
        self.request_timer.timeout.connect(self.request_stock)

    def initData(self):
        self.stock_lineEdit.setText(self._read_list())

    def request_stock(self):
        now = datetime.datetime.now()
        stock_text = self.stock_lineEdit.text()
        response = requests.get('http://hq.sinajs.cn/list=%s' % stock_text)
        if response.status_code == 200:
            stock_list = response.text.split(';\n')
            result = []
            for stock in stock_list[:-1]:
                stock_code, stock_detail = stock.split('=')
                stock_code = stock_code.split('var ')[1]
                stock_detal_list = stock_detail.split(',')
                temp_list = [
                    stock_detal_list[0],
                    stock_detal_list[1],
                    stock_detal_list[2],
                    stock_detal_list[3],
                    stock_detal_list[4],
                    stock_detal_list[5],
                ]
                if now.strftime('%H') >= '15':
                    temp_list.append(stock_detal_list[-3])
                    temp_list.append(stock_detal_list[-2])
                else:
                    temp_list.append(stock_detal_list[-4])
                    temp_list.append(stock_detal_list[-3])
                result.append(temp_list)

        self.stock_model.update_source_data(result)

    def _read_list(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'StockList.txt')
        stock_list = []
        with open(file_path, 'r') as f:
            stock_list = f.readline()
        return stock_list

    def play_sound(self):
        mp3_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources/8487.mp3')
        playsound(mp3_path)
        playsound(mp3_path)
        playsound(mp3_path)
