#!/usr/bin/env python
# coding=utf-8
# Copyright (c) 2019 MoreVFX. All rights reserved.
# created by huiguoyu @ 2020/8/27 20:23
import os
import datetime
import yaml

import requests
from PySide import QtCore
from PySide import QtGui


class SelectWidget(QtGui.QWidget):

    code = u'策略选股'

    def __init__(self, parent=None):
        super(SelectWidget, self).__init__(parent)

        self.setupUi(self)
        self.initData()
        self.bindFun()


    def setupUi(self, parent):
        self.setWindowTitle(u'策略选股')
        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.label = QtGui.QLabel(u'敬请期待')
        self.main_layout.addWidget(self.label)

    def initData(self):
        pass

    def bindFun(self):
        pass