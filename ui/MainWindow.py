# coding:utf-8
from functools import partial

from PySide import QtGui
from PySide import QtCore

from ui.CustomSelectDialog import CustomSelectDialog
from ui.DealWidget import DealWidget
from ui.QRCodeDialog import QRCodeDialog
from ui.SelectWidget import SelectWidget


class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.setupUi(self)
        self.initData()
        self.bindFun()

    def setupUi(self, parent):
        self.setWindowTitle('StockWatcher')
        self.setWindowIcon(QtGui.QIcon("resources/favicon.ico"))
        self.menu_bar = QtGui.QMenuBar()
        self.setMenuBar(self.menu_bar)
        self.view_menu = QtGui.QMenu('View')
        self.menu_bar.addMenu(self.view_menu)
        self.help_menu = QtGui.QMenu('Help')
        self.menu_bar.addMenu(self.help_menu)
        self.deal_action = QtGui.QAction(u'交易追踪', None)
        self.deal_action.setCheckable(True)
        self.view_menu.addAction(self.deal_action)
        self.select_action = QtGui.QAction(u'策略选股', None)
        self.select_action.setCheckable(True)
        self.view_menu.addAction(self.select_action)
        self.custom_select_action = QtGui.QAction(u'添加自选股', None)
        self.view_menu.addAction(self.custom_select_action)
        self.qrcode_action = QtGui.QAction(u'群二维码', None)
        self.help_menu.addAction(self.qrcode_action)
        self.tab_widget = QtGui.QTabWidget()
        self.deal_tab = DealWidget()
        self.tab_widget.addTab(self.deal_tab, u'交易追踪')
        self.select_tab = SelectWidget()
        self.setCentralWidget(self.tab_widget)

    def bindFun(self):
        self.deal_action.toggled.connect(partial(self.change_tab, self.deal_tab))
        self.select_action.toggled.connect(partial(self.change_tab, self.select_tab))
        self.custom_select_action.triggered.connect(partial(self.show_dialog, CustomSelectDialog))
        self.qrcode_action.triggered.connect(partial(self.show_dialog, QRCodeDialog))

    def initData(self):
        self.deal_action.setChecked(True)

    def change_tab(self, widget, checked):
        index = self.tab_widget.indexOf(widget)
        if checked and index == -1:
            new_index = self.tab_widget.addTab(widget, widget.code)
            self.tab_widget.setCurrentIndex(new_index)
        elif not checked and index > -1:
            self.tab_widget.removeTab(index)
        else:
            self.tab_widget.setCurrentIndex(index)

    def show_dialog(self, dialog_type):
        dialog = dialog_type.run(self)


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()