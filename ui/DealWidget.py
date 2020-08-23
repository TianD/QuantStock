#!/usr/bin/env python
# coding=utf-8
# created by huiguoyu @ 2020/7/21 13:11
import os
import datetime
import yaml

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
        return [u'股票代码',
                u'股票名称',
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

    def update_source_data(self, source_data):
        self.beginResetModel()
        self.source_data = source_data
        self.endResetModel()


class StrategyModel(QtCore.QAbstractTableModel):

    def __init__(self, source_data=None, parent=None):
        super(StrategyModel, self).__init__(parent)
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
        return [u'股票代码',
                u'股票名称',
                u'买入价',
                u'浮盈比例',
                u'回吐比例',
                u'今日最高价',
                u'浮盈出场价格']

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
            value = self.source_data[row][column]
            if isinstance(value, float) and column in [3, 4]:
                return '{:.2f}%'.format(value*100)
            return self.source_data[row][column]
        elif role == QtCore.Qt.BackgroundColorRole:
            flag = self.source_data[row][-1]
            if flag:
                return QtGui.QColor(flag)

    def update_source_data(self, source_data):
        self.beginResetModel()
        self.source_data = source_data
        self.endResetModel()


class DealWidget(QtGui.QWidget):

    playFlag = QtCore.Signal()

    def __init__(self, parent=None):
        super(DealWidget, self).__init__(parent)

        self.setupUi(self)
        self.initData()
        self.bindFun()
        self.request_timer.start()

    def setupUi(self, parent):
        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.stock_lineEdit = QtGui.QLineEdit()
        self.main_layout.addWidget(self.stock_lineEdit)
        self.view_layout = QtGui.QHBoxLayout()
        self.main_layout.addLayout(self.view_layout)
        self.stock_layout = QtGui.QVBoxLayout()
        self.view_layout.addLayout(self.stock_layout)
        self.stock_label = QtGui.QLabel(u'行情')
        self.stock_layout.addWidget(self.stock_label)
        self.stock_tableView = QtGui.QTableView()
        self.stock_layout.addWidget(self.stock_tableView)
        self.stock_model = StockModel()
        self.stock_tableView.setModel(self.stock_model)
        self.strategy_layout = QtGui.QVBoxLayout()
        self.view_layout.addLayout(self.strategy_layout)
        self.strategy_label = QtGui.QLabel(u'浮动止盈策略')
        self.strategy_layout.addWidget(self.strategy_label)
        self.strategy_tableView = QtGui.QTableView()
        self.strategy_model = StrategyModel()
        self.strategy_tableView.setModel(self.strategy_model)
        self.strategy_layout.addWidget(self.strategy_tableView)
        self.stock_tableView.setFixedWidth(640)
        self.strategy_tableView.setFixedWidth(450)
        #
        self.request_timer = QtCore.QTimer()
        self.request_timer.setInterval(1000)
        #
        self.audio_thread = QtCore.QThread()
        self.audio_thread.run = self.play_sound

    def bindFun(self):
        self.request_timer.timeout.connect(self.request_stock)
        self.request_timer.timeout.connect(self.run_strategy)
        self.playFlag.connect(self.play)
        self.strategy_tableView.doubleClicked.connect(self.edit_bid)

    def initData(self):
        self.config_data = self._read_config() or {}
        stock_text = ','.join(self.config_data.keys()) if self.config_data else ''
        self.stock_lineEdit.setText(stock_text)

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

        self.stock_model.update_source_data(result)
        self.stock_tableView.resizeColumnsToContents()

    def run_strategy(self):
        stock_list = self.stock_model.source_data
        strategy_list = []
        for index, stock in enumerate(stock_list):
            code = stock[0]
            name = stock[1]
            current = float(stock[4])
            top = float(stock[5])
            bid = float(self.config_data.get(code) or 0)
            gains = (top-bid)/bid if bid > 0 else 0
            giveup = self._get_giveup(gains)
            line = self._get_line(bid, gains, giveup) if bid > 0 else 0
            if current and current <= line:
                flag = 'red'
                self.playFlag.emit()
            if current < bid*0.97:
                flag = 'green'
                self.playFlag.emit()
            else:
                flag = None
            strategy_list.append([
                code,
                name,
                bid,
                gains,
                giveup,
                top,
                line,
                flag
            ])
        self.strategy_model.update_source_data(strategy_list)
        self.strategy_tableView.resizeColumnsToContents()

    def _get_giveup(self, value):
        if value < 0.05:
            return 0.0
        elif value >=0.05 and value < 0.10:
            return 0.5
        elif value >=0.10 and value < 0.15:
            return 0.4
        elif value >=0.15 and value < 0.20:
            return 0.3
        elif value >=0.20 and value < 0.30:
            return 0.2
        elif value >=0.3:
            return 0.1

    def _get_line(self, bid, gains, giveup):
        if not (bid and gains and giveup):
            return 0
        if gains < 0.05:
            return bid*(1+0.002)
        else:
            return bid*(1+gains*(1-giveup))

    def _read_config(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/StockList.yml')
        stock_dict = {}
        with open(file_path, 'r') as f:
            stock_dict = yaml.load(f)
        return stock_dict

    def play_sound(self):
        mp3_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources/8487.mp3')
        playsound(mp3_path)
        playsound(mp3_path)
        playsound(mp3_path)

    def play(self):
        if not self.audio_thread.isRunning():
            self.audio_thread.start()

    def closeEvent(self, event):
        strategy_list = self.strategy_model.source_data
        stock_dict = {strategy[0]: strategy[2] for strategy in strategy_list}
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/StockList.yml')
        with open(file_path, 'w') as f:
            f.write(yaml.dump(stock_dict))

    def edit_bid(self, index):
        if not index.isValid():
            return
        row = index.row()
        column = index.column()
        strategy_list = self.strategy_model.source_data
        name = strategy_list[row][1]
        code = strategy_list[row][0]
        dlg = QtGui.QDialog(self)
        dlg.setWindowTitle(u'编辑买入价')
        layout = QtGui.QVBoxLayout()
        dlg.setLayout(layout)
        label = QtGui.QLabel(name)
        layout.addWidget(label)
        edit = QtGui.QLineEdit()
        layout.addWidget(edit)
        btn = QtGui.QPushButton(u'确定')
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        result = dlg.exec_()
        if result:
            self.config_data.update({code: float(edit.text())})