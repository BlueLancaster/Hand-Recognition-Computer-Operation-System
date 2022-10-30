import time

import PyQt5
from PyQt5 import QtWidgets, QtCore

from UI.MainWindow import Ui_MainWindow


class MainController(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()  # 設定ui介面
        self.ui.setupUi(self)  # 將ui和QtWidgets初始化
        self.animation1 = None
        self.animation2 = None

        self.ui.side_menu.enterEvent = self.side_menu_animation  # 當滑鼠進入觸發
        self.ui.side_menu.leaveEvent = self.side_menu_animation  # 當滑鼠離開觸發
        # 按鍵綁定切換頁面
        self.ui.home_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.profile_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.gesture_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.setting_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))

    def side_menu_animation(self, event):
        # 目錄開關動畫
        max_size = 150
        min_size = 50
        self.animation1 = QtCore.QPropertyAnimation(self.ui.side_menu, b"maximumWidth")
        self.animation1.setDuration(500)
        self.animation2 = QtCore.QPropertyAnimation(self.ui.side_menu, b"minimumWidth")
        self.animation2.setDuration(500)
        print(event)
        if isinstance(event, PyQt5.QtGui.QEnterEvent):   # 有滑鼠進入事件則展開Menu
            self.animation1.setStartValue(min_size)
            self.animation1.setEndValue(max_size)
            self.animation2.setStartValue(min_size)
            self.animation2.setEndValue(max_size)
        elif isinstance(event, PyQt5.QtCore.QEvent):  # 有滑鼠離開事件則展開Menu則展開Menu
            self.animation1.setStartValue(max_size)
            self.animation1.setEndValue(min_size)
            self.animation2.setStartValue(max_size)
            self.animation2.setEndValue(min_size)
        # 開始動畫
        self.animation1.start()
        self.animation2.start()
        time.sleep(0.2)
