# coding:utf-8

from PySide import QtGui
from PySide import QtCore

from ui.DealWidget import DealWidget


class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.setupUi(self)
        self.bindFun()
        self.initData()
        
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
        self.view_menu.addAction(self.deal_action)
        self.select_action = QtGui.QAction(u'策略选股', None)
        self.view_menu.addAction(self.select_action)
        self.qrcode_action = QtGui.QAction(u'群二维码', None)
        self.help_menu.addAction(self.qrcode_action)
        self.tab_widget = QtGui.QTabWidget()
        self.deal_tab = DealWidget()
        self.tab_widget.addTab(self.deal_tab, u'交易追踪')
        self.setCentralWidget(self.tab_widget)

    def bindFun(self):
        pass

    def initData(self):
        pass


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()