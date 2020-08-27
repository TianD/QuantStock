#!/usr/bin/env python
# coding=utf-8
# Copyright (c) 2019 MoreVFX. All rights reserved.
# created by huiguoyu @ 2020/8/27 20:30

from PySide import QtGui
from PySide import QtCore


class CustomSelectDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        super(CustomSelectDialog, self).__init__(parent)

        self.setupUi(self)
        self.initData()
        self.bindFun()

    def setupUi(self, parent):
        pass

    def initData(self):
        pass

    def bindFun(self):
        pass

    @classmethod
    def run(cls, parent):
        obj = cls(parent)
        obj.exec_()
        return obj