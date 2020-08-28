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
        self.mute_action = QtGui.QAction(u'静音', None)
        self.mute_action.setCheckable(True)
        self.view_menu.addAction(self.mute_action)
        self.help_action = QtGui.QAction(u'帮助', None)
        self.help_menu.addAction(self.help_action)
        self.tab_widget = QtGui.QTabWidget()
        self.deal_tab = DealWidget(mute_flag=False)
        self.tab_widget.addTab(self.deal_tab, u'交易追踪')
        self.select_tab = SelectWidget()
        self.setCentralWidget(self.tab_widget)

    def bindFun(self):
        self.deal_action.toggled.connect(partial(self.change_tab, self.deal_tab))
        self.select_action.toggled.connect(partial(self.change_tab, self.select_tab))
        self.custom_select_action.triggered.connect(partial(self.show_dialog, CustomSelectDialog))
        self.help_action.triggered.connect(partial(self.show_dialog, QRCodeDialog))
        self.mute_action.toggled.connect(self.deal_tab.mute)

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
        flag, dialog = dialog_type.run(self)
        if isinstance(dialog, CustomSelectDialog) and flag:
            result = dialog.get_stock_detail()
            source_data = self.deal_tab.stock_model.source_data
            if result[0] in [sd[0] for sd in source_data]:
                return
            source_data.append(result)
            self.deal_tab.stock_model.update_source_data(source_data)
            self.deal_tab.stock_tableView.resizeColumnsToContents()

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()