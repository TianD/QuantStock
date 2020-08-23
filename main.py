#!/usr/bin/env python
# coding=utf-8
# created by huiguoyu @ 2020/7/21 10:22
import sys
from PySide import QtGui
from ui.DealWidget import MainWindow


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()