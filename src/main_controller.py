import time

import PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui

from PyQt5.QtWidgets import QTableWidgetItem, QComboBox, QGraphicsScene
from plyer import notification

from UI.main_window import Ui_MainWindow as MainWindowUI
from UI.key_binding_caption import Ui_MainWindow as CaptionWindowUI
from add_key_window_controller import AddKeyWindow
from utils.settings_provider import KeyBindingProvider, ArgumentProvider
from threads import VideoThread, CamThread, ScreenShooter


class MainController(QtWidgets.QMainWindow):
    """
    The controller of the Main Window and the interface between the front end and back end
    """

    def __init__(self):
        super().__init__()
        self.ui = MainWindowUI()  # Set up UI
        self.ui.setupUi(self)  # Initialize  ui and QtWidgets
        self.animation1 = None
        self.animation2 = None
        self.powerBtn_state = False  # for controlling the state of the
        self.profile_info_state = True
        self.function_mode_duration = 0
        # Initialize main_window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.ui.stackedWidget.setCurrentIndex(0)
        # Initialize each provider and each thread
        self.arg_provider = ArgumentProvider()
        self.argument_provider_connect_init()
        self.key_binding_provider = KeyBindingProvider()
        self.key_binding_provider_connect_init()

        self.video_thread = VideoThread(self.arg_provider.settings)
        self.video_thread_connect_init()
        self.screen_shooter = ScreenShooter()  # avoid the screenshot blocking the cam thread
        self.cam_thread = CamThread(self.key_binding_provider.settings, self.arg_provider.settings)
        self.cam_thread_connect_init()
        self.add_key_window = AddKeyWindow()
        self.caption_window = QtWidgets.QMainWindow()
        # Initialize the events binding of side_menu and each page in StackedWidget
        # The events are clickEvent,enterEvent,...etc
        self.side_menu_connect_init()
        self.home_page_init()
        self.profile_page_connect_init()
        self.key_binding_page_connect_init()
        self.argument_page_connect_init()
        # for moving the main window
        self.moveFlag = False
        self.movePosition = None

    def mousePressEvent(self, event):
        """
        Override the event for moving the window
        :param event:QMouseEvent
        :return: None
        """
        if event.button() == QtCore.Qt.LeftButton:
            self.moveFlag = True
            self.movePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        """
        Override the event for moving the window
        :param event:QMouseEvent
        :return: None
        """
        if QtCore.Qt.LeftButton and self.moveFlag:
            self.move(event.globalPos() - self.movePosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        """
        Override the event for moving the window
        :param event:QMouseEvent
        :return: None
        """
        self.moveFlag = False

    def keyPressEvent(self, event):
        """
        Override the event for closing the window
        :param event:QMouseEvent
        :return: None
        """
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        elif event.key() == QtCore.Qt.Key_F1:
            self.showMinimized()

    def apply_profile(self):
        """
        Update the UI and the key binding settings in cam_thread
        :return: None
        """
        self.key_binding_provider.start()
        self.cam_thread.update_key_binding(self.key_binding_provider.settings)

    def set_profile_list(self, file_name):
        """
        Add the filename in the profile list
        :param file_name: the file name
        :return: None
        """
        self.ui.profile_list.addItem(file_name)

    def profile_info_state_unsaved(self):
        """
        Change the stylesheet of the info state
        :return: None
        """
        self.ui.profile_info_state.setText('尚未儲存')
        self.ui.profile_info_state_box.setStyleSheet('background-color:rgb(255, 85, 0)')

    def profile_info_state_saved(self):
        """
        Change the stylesheet of the info state
        :return: None
        """
        self.ui.profile_info_state.setText('已儲存')
        self.ui.profile_info_state_box.setStyleSheet('')

    def set_profile_list_selected_item(self, index, file_name):
        """
        Set up the selected filename in UI
        :param index: the index of the file in the file list
        :param file_name: the file name
        :return: None
        """
        self.ui.profile_list.setCurrentRow(index)
        self.ui.selected_profile.setText(file_name)
        self.ui.profile_seleted.setText(file_name)
        self.cam_thread.update_key_binding(self.key_binding_provider.settings)

    def set_profile_list_set_description(self, profile_name, description):
        """
        Set up the file name, and it's description in UI
        :param profile_name: the file name
        :param description: the  of the file
        :return:
        """
        self.ui.profile_name.setPlainText(profile_name)
        self.ui.profile_description_context.setPlainText(description)

    def set_key_binding_table_row(self, row: int, key_binding_list: list):
        """
        Set up key binding in the table
        :param row: int
        :param key_binding_list: list
        :return: None
        """
        if row == self.ui.key_binding_table.rowCount():
            self.ui.key_binding_table.setRowCount(self.ui.key_binding_table.rowCount() + 1)
        for i in range(3):
            if i == 0:
                new_item = QTableWidgetItem(key_binding_list[i])
                new_item.setTextAlignment(4)
                self.ui.key_binding_table.setItem(row, i, new_item)
            else:
                new_item = GestureComboBox(key_binding_list[i])
                new_item.currentIndexChanged.connect(self.check_key_binding)
                self.ui.key_binding_table.setCellWidget(row, i, new_item)

    def del_item(self):
        """
        Set the gesture as default or remove the custom hot key in the selected item in the key binding table according
        to the current item
        :return: None
        """
        if self.ui.key_binding_table.currentColumn() == 1 or self.ui.key_binding_table.currentColumn() == 2:
            self.ui.key_binding_table.cellWidget(self.ui.key_binding_table.currentRow(),
                                                 self.ui.key_binding_table.currentColumn()).setCurrentIndex(0)
        else:
            self.ui.key_binding_table.removeRow(self.ui.key_binding_table.currentRow())

    def save_key_binding_setting(self):
        """
        Save the key binding.According to the type of the function code,determine how to convert the values
        :return: None
        """
        new_settings = dict()
        new_settings['Description'] = self.key_binding_provider.settings['Description']
        # Avoid the same gesture combine of the custom hot key when the two hands are set to 0
        function_code_list = set()
        for row in range(self.ui.key_binding_table.rowCount()):
            if self.ui.key_binding_table.item(row, 0).text().isdigit():
                function_code_list.add(int(self.ui.key_binding_table.item(row, 0).text()))
        for row in range(self.ui.key_binding_table.rowCount()):
            if self.ui.key_binding_table.item(row, 0).text().isdigit():  # normal function mode
                function_code = int(self.ui.key_binding_table.item(row, 0).text())
                if self.ui.key_binding_table.cellWidget(row, 1).currentText() == '未設置' \
                        and self.ui.key_binding_table.cellWidget(row, 2).currentText() == '未設置':
                    left_hand = int((lambda text: text if text != '未設置' else str(-function_code))
                                    (self.ui.key_binding_table.cellWidget(row, 1).currentText()))
                    right_hand = int((lambda text: text if text != '未設置' else str(-function_code))
                                     (self.ui.key_binding_table.cellWidget(row, 2).currentText()))
                else:
                    left_hand = int((lambda text: text if text != '未設置' else -1)
                                    (self.ui.key_binding_table.cellWidget(row, 1).currentText()))
                    right_hand = int((lambda text: text if text != '未設置' else -1)
                                     (self.ui.key_binding_table.cellWidget(row, 2).currentText()))
                new_settings[(left_hand, right_hand)] = function_code
            else:  # custom hot key
                function_code = self.ui.key_binding_table.item(row, 0).text()
                temp_function_code = row
                while temp_function_code in function_code_list:
                    temp_function_code += 1
                if self.ui.key_binding_table.cellWidget(row, 1).currentText() == '未設置' \
                        and self.ui.key_binding_table.cellWidget(row, 2).currentText() == '未設置':
                    left_hand = int((lambda text: text if text != '未設置' else -temp_function_code)
                                    (self.ui.key_binding_table.cellWidget(row, 1).currentText()))
                    right_hand = int((lambda text: text if text != '未設置' else -temp_function_code)
                                     (self.ui.key_binding_table.cellWidget(row, 2).currentText()))
                else:
                    left_hand = int((lambda text: text if text != '未設置' else -1)
                                    (self.ui.key_binding_table.cellWidget(row, 1).currentText()))
                    right_hand = int((lambda text: text if text != '未設置' else -1)
                                     (self.ui.key_binding_table.cellWidget(row, 2).currentText()))
                new_settings[(left_hand, right_hand)] = function_code
        self.key_binding_provider.update_settings(new_settings)

    def check_key_binding(self):
        """
        Check if the gesture combine of the current row is legal or not.If not, set the index of the gesture to 0
        :return: None
        """
        current_row = self.ui.key_binding_table.currentRow()
        current_col = self.ui.key_binding_table.currentColumn()
        left_hand = self.ui.key_binding_table.cellWidget(current_row, 1).currentIndex()
        right_hand = self.ui.key_binding_table.cellWidget(current_row, 2).currentIndex()
        flag_same = False
        if current_col != 0 and (left_hand != 0 or right_hand != 0):
            for i in range(self.ui.key_binding_table.rowCount()):
                if self.ui.key_binding_table.cellWidget(i, 1).currentIndex() == left_hand \
                        and self.ui.key_binding_table.cellWidget(i,
                                                                 2).currentIndex() == right_hand and i != current_row:
                    flag_same = True
                    break
            if flag_same:
                self.ui.key_binding_table.cellWidget(current_row, 1).setCurrentIndex(0)
                self.ui.key_binding_table.cellWidget(current_row, 2).setCurrentIndex(0)

    def add_custom_key(self, key_list: list):
        """
        Add the new row for the custom hot key.Change it to a string and append a new row in the key binding table
        :param key_list: the list of custom keys
        :return: None
        """
        if key_list:
            new_row = self.ui.key_binding_table.rowCount()
            self.ui.key_binding_table.setRowCount(self.ui.key_binding_table.rowCount() + 1)
            key = ''
            for i in range(len(key_list)):
                key += key_list[i]
                if i != len(key_list) - 1:
                    key += '/'
            new_item = QTableWidgetItem(key)
            new_item.setTextAlignment(4)
            self.ui.key_binding_table.setItem(new_row, 0, new_item)
            for i in range(1, 3):
                new_item = GestureComboBox(-self.ui.key_binding_table.rowCount())
                new_item.currentIndexChanged.connect(self.check_key_binding)
                self.ui.key_binding_table.setCellWidget(new_row, i, new_item)

    def save_arg(self, new_file_name: str, new_arg_settings: dict):
        """
        Update the argument's setting in file and cam_thread
        :param new_file_name: the  new file name
        :param new_arg_settings: the new argument settings
        :return: None
        """
        self.arg_provider.update_arg_file(new_file_name, new_arg_settings)
        self.cam_thread.update_arg_settings(new_arg_settings)

    def get_arg(self):
        """
        Get the values of the arguments from the UI
        :return: dict
        """
        return {
            'model_complexity': self.ui.model_complex_checkBox.isChecked(),
            'min_detection_confidence': self.ui.detection_spinBox.value(),
            'min_tracking_confidence': self.ui.tracking_spinBox.value(),
            'min_cutoff': self.ui.min_cutoff_SpinBox.value(),
            'rate': self.ui.rate_spinBox.value()
        }

    def set_arg(self, settings: dict):
        """
        Set up the UI with the settings
        :param settings: the argument settings
        :return: None
        """
        self.ui.min_cutoff_SpinBox.setValue(settings['min_cutoff'])
        self.ui.rate_spinBox.setValue(settings['rate'])
        self.ui.model_complex_checkBox.setChecked(settings['model_complexity'])
        self.ui.model_complex_checkBox.setText((lambda: '狀態:開' if settings['model_complexity'] else '狀態:關')())
        self.ui.detection_spinBox.setValue(settings['min_detection_confidence'])
        self.ui.tracking_spinBox.setValue(settings['min_tracking_confidence'])

    def set_arg_list(self, index: int, file_name: str):
        """
        Insert the filename in the index of the argument comboBox
        :param index: the index of the file
        :param file_name: the file name
        :return:
        """
        self.ui.arg_comboBox.insertItem(index, file_name)

    def set_selected_arg(self, index: int):
        """
        Set the selected file in comboBox
        :param index: the order of the file in the file list
        :return: None
        """
        self.ui.arg_comboBox.setCurrentIndex(index)

    def side_menu_animation(self, event):
        """
        The animation of the side_menu_animation
        :param event:the event is triggered by the mouse
        :return:None
        """
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

    def powerBtn_state_changed(self):
        """
        When the powerBtn is pressed,change its styleSheet and icon
        :return: None
        """
        if not self.powerBtn_state:
            self.ui.power_btn.setStyleSheet('background-color: rgb(250, 185, 65);'
                                            'border-radius:25px')
            icon_name = 'stop'
        else:
            self.ui.power_btn.setStyleSheet('background-color: rgb(94, 252, 141);'
                                            'border-radius:25px')
            icon_name = 'play'
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/icons/icons/' + icon_name + '.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.power_btn.setIcon(icon)
        self.powerBtn_state = not self.powerBtn_state

    def show_function_mode(self, result: str, duration: int = 1):
        """
        Show the function with duration
        :param result: the label of the function mode
        :param duration: the lasting based on fps
        :return: None
        """
        if self.function_mode_duration <= 0:
            self.ui.func_result_label.setText(result)
            self.function_mode_duration = duration
        else:
            self.function_mode_duration -= 1

    def open_caption_window(self):
        """
        Open the caption window
        :return: None
        """
        ui = CaptionWindowUI()
        ui.setupUi(self.caption_window)
        self.caption_window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.caption_window.show()

    def video_start(self):
        """
        Update the argument settings in video thread and play the video, show how the mediapipe works in these settings
        :return: None
        """
        args = self.get_arg()
        self.video_thread.update_arg_settings(args)
        self.video_thread.start()

    def video_display(self, scene: QGraphicsScene):
        """
        Update the frame from the video thread in the graphicsView of video
        :param scene: the result frame
        :return: None
        """
        self.ui.video_graphicsView.setScene(scene)

    def cam_display(self, scene: QGraphicsScene):
        """
        Update the frame from the cam thread in the graphicsView of cam
        :param scene: the result frame
        :return: None
        """
        self.ui.cam_graphicsView.setScene(scene)

    def cam_not_working(self):
        """
        When the cam is not detected, change the stylesheet of the powerBtn
        :return: None
        """
        self.ui.power_btn.setStyleSheet('background-color: rgb(230, 0, 0);'
                                        'border-radius:25px')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/icons/icons/' + 'warning' + '.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.power_btn.setIcon(icon)
        self.ui.power_btn.setEnabled(False)

    @staticmethod
    def show_notification(title: str, content: str):
        """
        Show the system notification
        :param title: the title of the notification
        :param content: the content of the notification
        :return: None
        """
        notification.notify(title=title, message=content, timeout=2)

    def argument_provider_connect_init(self):
        self.arg_provider.trigger_load_arg_list.connect(self.set_arg_list)
        self.arg_provider.trigger_selected.connect(self.set_selected_arg)
        self.arg_provider.trigger_clear_list.connect(self.ui.arg_comboBox.clear)
        self.arg_provider.trigger_load_arg.connect(self.set_arg)
        self.arg_provider.start()

    def key_binding_provider_connect_init(self):
        self.key_binding_provider.trigger_load_profile_list.connect(self.set_profile_list)
        self.key_binding_provider.trigger_selected.connect(self.set_profile_list_selected_item)
        self.key_binding_provider.trigger_info.connect(self.set_profile_list_set_description)
        self.key_binding_provider.trigger_clear_profile_list.connect(lambda: self.ui.profile_list.clear())
        self.key_binding_provider.trigger_update_key_binding.connect(self.set_key_binding_table_row)
        self.key_binding_provider.trigger_clear_key_table.connect(lambda: self.ui.key_binding_table.clearContents())
        self.key_binding_provider.trigger_save.connect(self.profile_info_state_saved)
        self.key_binding_provider.start()

    def video_thread_connect_init(self):
        self.video_thread.trigger_display.connect(self.video_display)

    def cam_thread_connect_init(self):
        self.cam_thread.trigger_warning.connect(self.cam_not_working)
        self.cam_thread.trigger_display.connect(self.cam_display)
        self.cam_thread.trigger_show_left_hand.connect(self.ui.left_hand_result_label.setText)
        self.cam_thread.trigger_show_right_hand.connect(self.ui.right_hand_result_label.setText)
        self.cam_thread.trigger_show_func.connect(self.show_function_mode)
        self.cam_thread.trigger_OCR.connect(self.screen_shooter.start)
        self.screen_shooter.trigger_OCR.connect(lambda result: self.show_notification('OCR Result', result))
        self.cam_thread.trigger_notify.connect(self.show_notification)

    def side_menu_connect_init(self):
        self.ui.side_menu.enterEvent = self.side_menu_animation
        self.ui.side_menu.leaveEvent = self.side_menu_animation
        self.ui.home_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.profile_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.key_binding_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.argument_btn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))

    def home_page_init(self):
        self.ui.power_btn.clicked.connect(self.cam_thread.switching_state)
        self.ui.power_btn.clicked.connect(self.powerBtn_state_changed)

    def profile_page_connect_init(self):
        self.ui.profile_list.clicked.connect(
            lambda: self.key_binding_provider.change_current_file(self.ui.profile_list.currentRow()))
        self.ui.profile_save_btn.clicked.connect(lambda: self.key_binding_provider.save_json(
            self.ui.profile_name.toPlainText(), self.ui.profile_description_context.toPlainText()))
        self.ui.profile_apply_btn.clicked.connect(self.apply_profile)
        self.ui.profile_list_add_btn.clicked.connect(self.key_binding_provider.create_json)
        self.ui.profile_list_del_btn.clicked.connect(self.key_binding_provider.del_json)
        self.ui.profile_list_copy_btn.clicked.connect(self.key_binding_provider.copy_json)
        self.ui.profile_description_context.textChanged.connect(self.profile_info_state_unsaved)

    def key_binding_page_connect_init(self):
        self.ui.key_save_btn.clicked.connect(self.save_key_binding_setting)
        self.ui.del_key_btn.clicked.connect(self.del_item)
        self.ui.set_default_btn.clicked.connect(self.key_binding_provider.set_setting_default)
        self.ui.caption_btn.clicked.connect(self.open_caption_window)
        self.ui.add_key_btn.clicked.connect(self.add_key_window.show)
        self.add_key_window.trigger_add_key.connect(self.add_custom_key)

    def argument_page_connect_init(self):
        self.ui.arg_save_btn.clicked.connect(
            lambda: self.save_arg(self.ui.arg_comboBox.currentText(), self.get_arg()))
        self.ui.arg_comboBox.currentIndexChanged.connect(lambda: self.arg_provider.change_current_file(
            self.ui.arg_comboBox.currentIndex()))
        self.ui.arg_add_btn.clicked.connect(self.arg_provider.create_json)
        self.ui.arg_del_btn.clicked.connect(self.arg_provider.del_json)
        self.ui.arg_test_btn.clicked.connect(self.video_start)
        self.ui.model_complex_checkBox.clicked.connect(lambda: self.ui.model_complex_checkBox.setText(
            (lambda: '狀態:開' if self.ui.model_complex_checkBox.isChecked() else '狀態:關')()))


class GestureComboBox(QComboBox):
    """
    A comboBox class for gesture
    """

    def __init__(self, current: str):
        super(GestureComboBox, self).__init__()
        self.addItem('未設置')
        for i in range(9):
            self.addItem(str(i))
        self.setCurrentIndex(int(current) + 1 if int(current) > -1 else 0)
        self.setMaximumWidth(80)
