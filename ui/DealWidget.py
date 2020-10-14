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

from core.StockGetter import format_code_to_sina, request_stock, retrospect_to_date, format_code_to_163, \
    get_history_data


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
                u'买入价',
                u'追溯天数']

    def rowCount(self, parentIndex=QtCore.QModelIndex()):
        return len(self.source_data)

    def columnCount(self, parentIndex=QtCore.QModelIndex()):
        return len(self.header_data)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header_data[section]

    def flags(self, index):
        if index.isValid():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return
        row = index.row()
        column = index.column()
        key = self.header_data[column]
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            try:
                return self.source_data[row][column]
            except:
                return

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        row = index.row()
        column = index.column()
        key = self.header_data[column]
        if role == QtCore.Qt.EditRole:
            self.__source_data[row][column] = value
        self.dataChanged.emit(index, index)
        return True


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
                u'今日开盘价',
                u'昨日收盘价',
                u'当前价',
                u'最高价',
                u'最低价',
                u'浮盈比例',
                u'回吐比例',
                u'浮盈出场价格',
                u'止损价格',
                ]

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
            if isinstance(value, float) and column in [8, 9]:
                return '{:.2f}%'.format(value*100)
            return self.source_data[row][column]
        elif role == QtCore.Qt.BackgroundColorRole:
            flag = self.source_data[row][-3]
            if flag:
                return QtGui.QColor(flag)

    def update_source_data(self, source_data):
        self.beginResetModel()
        self.source_data = source_data
        self.endResetModel()


class DealWidget(QtGui.QWidget):

    custom_stock_signal = QtCore.Signal(object)
    playFlag = QtCore.Signal()
    code = u'交易追踪'

    def __init__(self, mute_flag, parent=None):
        super(DealWidget, self).__init__(parent)

        self.setupUi(self)
        self.initDataBefore()
        self.bindFun()
        self.initDataAfter()


    def setupUi(self, parent):
        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.view_layout = QtGui.QHBoxLayout()
        self.main_layout.addLayout(self.view_layout)
        self.stock_layout = QtGui.QVBoxLayout()
        self.view_layout.addLayout(self.stock_layout)
        self.stock_label = QtGui.QLabel(u'自选股')
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
        self.stock_tableView.setFixedWidth(300)
        self.strategy_tableView.setMinimumWidth(700)
        #
        self.request_timer = QtCore.QTimer()
        self.request_timer.setInterval(1000)
        #
        self.audio_thread = QtCore.QThread()
        self.audio_thread.run = self.play_sound
        #
        self.stock_tableView.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        del_option = QtGui.QAction(self.stock_tableView)
        del_option.setText(u'删除')
        del_option.triggered.connect(self.remove_stock)
        self.stock_tableView.addAction(del_option)

    def bindFun(self):
        self.request_timer.timeout.connect(self.request_stock)
        self.playFlag.connect(self.play)
        self.stock_model.dataChanged.connect(self.update_custom_view)

    def initDataBefore(self):
        # 读取配置
        config = self._read_config()
        custom_stock_list = []
        for key, value in config.items():
            code = key
            sina_code = format_code_to_sina(code)
            try:
                result = request_stock(sina_code)
            except:
                continue
            name = result[0][1]
            bid_price = value[0]
            try:
                retrospect_days = value[1]
            except:
                retrospect_days = 1
            history_data = get_history_data(code)[:retrospect_days]
            top_price = max([float(hd[6]) for hd in history_data])
            bottom_price = min([float(hd[5]) for hd in history_data])
            custom_stock_list.append([code, name, bid_price, retrospect_days, top_price, bottom_price])

        self.stock_model.update_source_data(custom_stock_list)
        self.stock_tableView.resizeColumnsToContents()

    def initDataAfter(self):
        # 获取最高价
        # 开始请求行情
        self.request_timer.start()

    def update_custom_view(self, index):
        self._save_config()

    def request_stock(self):
        now = datetime.datetime.now()
        sourcedata = self.stock_model.source_data
        stock_text = ','.join([format_code_to_sina(sd[0]) for sd in sourcedata])
        response = requests.get('http://hq.sinajs.cn/list=%s' % stock_text)
        if response.status_code == 200:
            stock_list = response.text.split(';\n')
            result = []
            for index, stock in enumerate(stock_list[:-1]):
                _, stock_detail = stock.split('=')
                stock_detal_list = stock_detail.split(',')
                stock_code = sourcedata[index][0]
                stock_name = stock_detal_list[0][1:]
                bid_price = sourcedata[index][2]
                today_open = stock_detal_list[1]
                last_close = stock_detal_list[2]
                current_price = float(stock_detal_list[3])
                today_top_price = float(stock_detal_list[4])
                today_bottom_price = float(stock_detal_list[5])
                top_price = max(sourcedata[index][-2], today_top_price)
                bottom_price = min(sourcedata[index][-1], today_bottom_price)
                current_date = stock_detal_list[30]
                current_time = stock_detal_list[31]
                gains, stop_price, line, giveup_price, flag = self.run_strategy(current_price, top_price, bid_price)
                try:
                    temp_list = [
                        stock_code,
                        stock_name,
                        bid_price,
                        today_open,
                        last_close,
                        current_price,
                        top_price,
                        bottom_price,
                        gains,
                        stop_price,
                        line,
                        giveup_price,
                        flag,
                        current_date,
                        current_time
                    ]
                    result.append(temp_list)
                except:
                    pass

        self.strategy_model.update_source_data(result)
        self.strategy_tableView.resizeColumnsToContents()

    def run_strategy(self, current, top, bid):
        gains = (top-bid)/bid if bid > 0 else 0 # 浮盈比例
        stop = self._get_stop(gains)    # 出场价格
        line = self._get_line(bid, gains, stop) if bid > 0 else 0
        giveup = bid*0.97
        if current and current <= line:
            flag = 'red'
            self.playFlag.emit()
        elif current < giveup:
            flag = 'green'
            self.playFlag.emit()
        else:
            flag = None
        return gains, stop, line, giveup, flag

    def _get_stop(self, value):
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

    def _get_line(self, bid, gains, stop):
        if not (bid and gains and stop):
            return 0
        if gains < 0.05:
            return bid*(1+0.002)
        else:
            return bid*(1+gains*(1-stop))

    def _read_config(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/StockList.yml')
        stock_dict = {}
        with open(file_path, 'r') as f:
            stock_dict = yaml.load(f)
        return stock_dict

    def _save_config(self):
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/StockList.yml')
        data = self.stock_model.source_data
        strategy_data = self.strategy_model.source_data
        result = {}
        for index, stock in enumerate(data):
            bid_price = stock[2]
            retrospect_days = stock[3]
            top = strategy_data[index][6]
            bottom = strategy_data[index][7]
            result.setdefault(stock[0], [bid_price, retrospect_days, top, bottom])
        with open(file_path, 'w') as f:
            f.write(yaml.dump(result))

    def play_sound(self):
        mp3_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources/8487.mp3')
        playsound(mp3_path)
        playsound(mp3_path)
        playsound(mp3_path)

    def play(self):
        if not self.audio_thread.isRunning():
            self.audio_thread.start()

    def closeEvent(self, event):
        self._save_config()
        # self.request_timer.stop()
        # self.audio_thread.terminate()

    def mute(self, flag):
        if flag:
            self.audio_thread.quit()
        else:
            self.audio_thread.start()

    def remove_stock(self):
        selected = self.stock_tableView.selectedIndexes()
        rows = [index.row() for index in selected]
        source_data = self.stock_model.source_data
        for row in sorted(rows)[::-1]:
            source_data.pop(row)
        self.stock_model.update_source_data(source_data)
        self.stock_tableView.resizeColumnsToContents()