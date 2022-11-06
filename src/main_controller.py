import time

import PyQt5
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem

from UI.MainWindow import Ui_MainWindow
from utils.settings_provider import SettingsProvider


class MainController(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()  # set up UI
        self.ui.setupUi(self)  # initialize  ui and QtWidgets
        self.animation1 = None
        self.animation2 = None
        self.setting_provider = SettingsProvider(1)
        self.setting_provider.trigger_read_file.connect(self.set_profile_list)
        self.setting_provider.trigger_selected.connect(self.set_profile_list_selected_item)
        self.setting_provider.trigger_info.connect(self.set_profile_list_set_description)
        self.setting_provider.trigger_update_profile_list.connect(lambda num: self.ui.profile_list.clear())
        self.setting_provider.trigger_update_key_binding.connect(self.set_key_binding_table_row)
        self.setting_provider.start()

        self.ui.profile_list.clicked.connect(
            lambda: self.setting_provider.change_current_settings_file(self.ui.profile_list.currentRow()))
        self.ui.side_menu.enterEvent = self.side_menu_animation  # when mouse enters,animation takes place
        self.ui.side_menu.leaveEvent = self.side_menu_animation  # when mouse leaves,animation takes place
        # when button clicked, changing the page the stackedWidget displays
        self.ui.home_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.profile_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.gesture_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.setting_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
        self.ui.apply_btn.clicked.connect(lambda: self.setting_provider.save_json(self.ui.profile_name.toPlainText(),
                                                                                  self.ui.profile_description_context.toPlainText()))
        self.ui.add_btn.clicked.connect(self.setting_provider.create_json)
        self.ui.del_btn.clicked.connect(self.setting_provider.del_json)
        self.ui.copy_btn.clicked.connect(self.setting_provider.copy_json)

    def set_profile_list(self, file_name):
        self.ui.profile_list.addItem(file_name)

    def set_profile_list_selected_item(self, index, file_name):
        self.ui.profile_list.setCurrentRow(index)
        self.ui.selected_profile.setText(file_name)

    def set_key_binding_table_row(self, row, function_code, gesture):
        self.ui.key_binding_table.setRowCount(self.ui.key_binding_table.rowCount() + 1)
        self.ui.key_binding_table.setItem(row, 0, QTableWidgetItem(str(function_code)))
        self.ui.key_binding_table.setItem(row, 1, QTableWidgetItem(str(gesture[0])))
        self.ui.key_binding_table.setItem(row, 2, QTableWidgetItem(str(gesture[1])))

    def set_profile_list_set_description(self, profile_name, description):
        self.ui.profile_name.setPlainText(profile_name)
        self.ui.profile_description_context.setPlainText(description)

    def side_menu_animation(self, event):
        """
        the animation of the side_menu_animation
        :param event:the event is triggered by the mouse
        :return:
        """
        # the size of the buttons
        max_size = 150
        min_size = 50
        self.animation1 = QtCore.QPropertyAnimation(self.ui.side_menu, b"maximumWidth")
        self.animation1.setDuration(500)
        self.animation2 = QtCore.QPropertyAnimation(self.ui.side_menu, b"minimumWidth")
        self.animation2.setDuration(500)
        if isinstance(event, PyQt5.QtGui.QEnterEvent):  # when mouse enters, the menu opens
            self.animation1.setStartValue(min_size)
            self.animation1.setEndValue(max_size)
            self.animation2.setStartValue(min_size)
            self.animation2.setEndValue(max_size)
        elif isinstance(event, PyQt5.QtCore.QEvent):  # when mouse enters, the menu closes
            self.animation1.setStartValue(max_size)
            self.animation1.setEndValue(min_size)
            self.animation2.setStartValue(max_size)
            self.animation2.setEndValue(min_size)
        # start the animations
        self.animation1.start()
        self.animation2.start()
        time.sleep(0.2)
