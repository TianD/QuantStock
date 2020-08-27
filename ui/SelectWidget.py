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
        pass

    def initData(self):
        pass

    def bindFun(self):
        pass