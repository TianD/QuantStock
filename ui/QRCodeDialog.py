#!/usr/bin/env python
# coding=utf-8
# Copyright (c) 2019 MoreVFX. All rights reserved.
# created by huiguoyu @ 2020/8/27 20:30

from PySide import QtGui
from PySide import QtCore


class QRCodeDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(QRCodeDialog, self).__init__(parent)

        self.setupUi(self)
        self.initData()
        self.bindFun()

    def setupUi(self, parent):
        self.setWindowTitle(u'帮助')
        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.help1 = QtGui.QLabel(u'红色: 已经达到浮动止盈线.')
        self.main_layout.addWidget(self.help1)
        self.help2 = QtGui.QLabel(u'绿色: 已经跌破止损线.')
        self.main_layout.addWidget(self.help2)
        self.help3 = QtGui.QLabel(u'当出现红色或者绿色时, 会有鸣笛声提醒.')
        self.main_layout.addWidget(self.help3)
        self.help4 = QtGui.QLabel(u'更多股票咨询请微信搜素: “对韭当割”财经交流群.')
        self.main_layout.addWidget(self.help4)

    def initData(self):
        pass

    def bindFun(self):
        pass

    @classmethod
    def run(cls, parent):
        obj = cls(parent)
        obj.exec_()
        return True, obj