import time

import PyQt5
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QTableWidgetItem

from UI.main_window import Ui_MainWindow as MainWindowUI
from UI.key_binding_caption import Ui_MainWindow as CaptionWindowUI
from utils.settings_provider import KeyBindingProvider, ArgumentProvider
from threads import VideoThread, CamThread


class MainController(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = MainWindowUI()  # set up UI
        self.ui.setupUi(self)  # initialize  ui and QtWidgets
        self.animation1 = None
        self.animation2 = None

        self.ui.stackedWidget.setCurrentIndex(0)

        self.arg_provider = ArgumentProvider()
        self.arg_provider.trigger_load_arg_list.connect(self.set_arg_comboBox)
        self.arg_provider.trigger_selected.connect(self.set_selected_arg)
        self.arg_provider.trigger_clear_list.connect(self.ui.arg_comboBox.clear)
        self.arg_provider.trigger_load_arg.connect(self.set_arg)
        self.arg_provider.start()

        self.key_binding_provider = KeyBindingProvider()
        self.key_binding_provider.trigger_load_profile_list.connect(self.set_profile_list)
        self.key_binding_provider.trigger_selected.connect(self.set_profile_list_selected_item)
        self.key_binding_provider.trigger_info.connect(self.set_profile_list_set_description)
        self.key_binding_provider.trigger_clear_profile_list.connect(lambda: self.ui.profile_list.clear())
        self.key_binding_provider.trigger_update_key_binding.connect(self.set_key_binding_table_row)
        self.key_binding_provider.trigger_clear_key_table.connect(lambda: self.ui.key_binding_table.clearContents())
        self.key_binding_provider.start()

        self.video_thread = VideoThread(self.arg_provider.settings)
        self.video_thread.trigger_display.connect(self.video_display)

        self.cam_thread = CamThread(self.key_binding_provider.settings, self.arg_provider.settings)
        self.cam_thread.trigger_display.connect(self.cam_display)
        self.cam_thread.trigger_show_left_hand.connect(self.ui.left_hand_result_label.setText)
        self.cam_thread.trigger_show_right_hand.connect(self.ui.right_hand_result_label.setText)
        self.cam_thread.trigger_show_func.connect(self.ui.func_result_label.setText)

        self.caption_window = QtWidgets.QMainWindow()

        self.ui.profile_list.clicked.connect(
            lambda: self.key_binding_provider.change_current_file(self.ui.profile_list.currentRow()))
        self.ui.side_menu.enterEvent = self.side_menu_animation  # when mouse enters,animation takes place
        self.ui.side_menu.leaveEvent = self.side_menu_animation  # when mouse leaves,animation takes place
        # when button clicked, changing the page the stackedWidget displays
        self.ui.home_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.profile_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.gesture_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.setting_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))

        self.ui.power_btn.clicked.connect(self.cam_thread.switching_state)

        self.ui.profile_save_btn.clicked.connect(
            lambda: self.key_binding_provider.save_json(self.ui.profile_name.toPlainText(),
                                                        self.ui.profile_description_context
                                                        .toPlainText()))
        self.ui.profile_apply_btn.clicked.connect(self.apply_profile)
        self.ui.add_btn.clicked.connect(self.key_binding_provider.create_json)
        self.ui.del_btn.clicked.connect(self.key_binding_provider.del_json)
        self.ui.copy_btn.clicked.connect(self.key_binding_provider.copy_json)
        self.ui.key_save_btn.clicked.connect(self.save_key_binding_setting)
        self.ui.del_key_btn.clicked.connect(self.del_key)
        self.ui.set_default_btn.clicked.connect(self.key_binding_provider.set_setting_default)
        self.ui.caption_btn.clicked.connect(self.open_caption_window)

        self.ui.arg_save_btn.clicked.connect(
            lambda: self.save_arg(self.ui.arg_comboBox.currentText(), self.get_arg()))
        self.ui.arg_comboBox.currentIndexChanged.connect(lambda: self.arg_provider.change_current_file(
            self.ui.arg_comboBox.currentIndex()))
        self.ui.arg_add_btn.clicked.connect(self.arg_provider.create_json)
        self.ui.arg_del_btn.clicked.connect(self.arg_provider.del_json)
        self.ui.arg_test_btn.clicked.connect(self.video_start)

    def save_arg(self, new_file_name, new_arg_settings):
        self.arg_provider.update_arg_file(new_file_name, new_arg_settings)
        self.cam_thread.update_arg_settings(new_arg_settings)

    def apply_profile(self):
        self.key_binding_provider.start()
        self.cam_thread.update_key_binding(self.key_binding_provider.settings)

    def get_arg(self):
        return {
            'model_complexity': self.ui.model_complex_checkBox.isChecked(),
            'min_detection_confidence': self.ui.detection_spinBox.value(),
            'min_tracking_confidence': self.ui.tracking_spinBox.value(),
            'smooth': self.ui.smooth_spinBox.value(),
            'min_cutoff': self.ui.min_cutoff_SpinBox.value(),
            'rate': self.ui.rate_spinBox.value()
        }

    def set_arg(self, settings):
        self.ui.smooth_spinBox.setValue(settings['smooth'])
        self.ui.min_cutoff_SpinBox.setValue(settings['min_cutoff'])
        self.ui.rate_spinBox.setValue(settings['rate'])
        self.ui.model_complex_checkBox.setChecked(settings['model_complexity'])
        self.ui.detection_spinBox.setValue(settings['min_detection_confidence'])
        self.ui.tracking_spinBox.setValue(settings['min_tracking_confidence'])

    def set_arg_comboBox(self, index, file_name):
        self.ui.arg_comboBox.insertItem(index, file_name)

    def set_selected_arg(self, index):
        self.ui.arg_comboBox.setCurrentIndex(index)

    def del_key(self):
        if self.ui.key_binding_table.currentColumn() == 1 or self.ui.key_binding_table.currentColumn() == 2:
            self.ui.key_binding_table.currentItem().setText('未設置')
        else:
            self.ui.key_binding_table.setCurrentItem(None)

    def save_key_binding_setting(self):
        new_settings = dict()
        new_settings['Description'] = self.key_binding_provider.settings['Description']
        for row in range(self.ui.key_binding_table.rowCount()):
            function_code = int(self.ui.key_binding_table.item(row, 0).text())
            left_hand = int((lambda text: text if text != '未設置' else '-1')
                            (self.ui.key_binding_table.item(row, 1).text()))
            right_hand = int((lambda text: text if text != '未設置' else '-1')
                             (self.ui.key_binding_table.item(row, 2).text()))
            new_settings[(left_hand, right_hand)] = function_code
        self.key_binding_provider.update_settings(new_settings)

    def set_profile_list(self, file_name):
        self.ui.profile_list.addItem(file_name)

    def set_profile_list_selected_item(self, index, file_name):
        self.ui.profile_list.setCurrentRow(index)
        self.ui.selected_profile.setText(file_name)
        self.ui.profile_seleted.setText(file_name)
        self.cam_thread.update_key_binding(self.key_binding_provider.settings)

    def set_key_binding_table_row(self, row, value):
        if row == self.ui.key_binding_table.rowCount():
            self.ui.key_binding_table.setRowCount(self.ui.key_binding_table.rowCount() + 1)
        for i in range(3):
            new_item = QTableWidgetItem((lambda: value[i] if int(value[i]) != -1 else '未設置')())
            new_item.setTextAlignment(4)
            self.ui.key_binding_table.setItem(row, i, new_item)

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

    def open_caption_window(self):
        ui = CaptionWindowUI()
        ui.setupUi(self.caption_window)
        self.caption_window.show()

    def video_start(self):
        args = self.get_arg()
        self.video_thread.update_arg_settings(args)
        self.video_thread.start()

    def video_display(self, scene):
        self.ui.video_graphicsView.setScene(scene)

    def cam_display(self, scene):
        self.ui.cam_graphicsView.setScene(scene)
