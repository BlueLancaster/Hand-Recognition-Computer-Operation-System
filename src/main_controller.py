import time

import PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui

from PyQt5.QtWidgets import QTableWidgetItem
from plyer import notification

from UI.main_window import Ui_MainWindow as MainWindowUI
from UI.key_binding_caption import Ui_MainWindow as CaptionWindowUI
from utils.settings_provider import KeyBindingProvider, ArgumentProvider
from threads import VideoThread, CamThread, ScreenShooter


class MainController(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = MainWindowUI()  # Set up UI
        self.ui.setupUi(self)  # Initialize  ui and QtWidgets
        self.animation1 = None
        self.animation2 = None
        self.powerBtn_state = False
        self.profile_info_state = True
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

        self.screen_shooter = ScreenShooter()
        self.cam_thread = CamThread(self.key_binding_provider.settings, self.arg_provider.settings)
        self.cam_thread_connect_init()

        # Initialize the events binding of side_menu and each page in StackedWidget
        # The events are clickEvent,enterEvent,...etc
        self.side_menu_connect_init()
        self.home_page_init()
        self.profile_page_connect_init()
        self.key_binding_page_connect_init()
        self.argument_page_connect_init()
        self.caption_window = QtWidgets.QMainWindow()

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

    def save_arg(self, new_file_name, new_arg_settings):
        """
        Update the argument's setting in file and cam_thread
        :param new_file_name: str
        :param new_arg_settings: dict
        :return: None
        """
        self.arg_provider.update_arg_file(new_file_name, new_arg_settings)
        self.cam_thread.update_arg_settings(new_arg_settings)

    def get_arg(self):
        """
        Get the value from the UI
        :return: dict
        """
        return {
            'model_complexity': self.ui.model_complex_checkBox.isChecked(),
            'min_detection_confidence': self.ui.detection_spinBox.value(),
            'min_tracking_confidence': self.ui.tracking_spinBox.value(),
            'min_cutoff': self.ui.min_cutoff_SpinBox.value(),
            'rate': self.ui.rate_spinBox.value()
        }

    def set_arg(self, settings):
        """
        Set up the UI with the settings
        :param settings: dict
        :return: None
        """
        self.ui.min_cutoff_SpinBox.setValue(settings['min_cutoff'])
        self.ui.rate_spinBox.setValue(settings['rate'])
        self.ui.model_complex_checkBox.setChecked(settings['model_complexity'])
        self.ui.model_complex_checkBox.setText((lambda: '狀態:開' if settings['model_complexity'] else '狀態:關')())
        self.ui.detection_spinBox.setValue(settings['min_detection_confidence'])
        self.ui.tracking_spinBox.setValue(settings['min_tracking_confidence'])

    def set_arg_comboBox(self, index, file_name):
        """
        Add the filename in the index of the argument comboBox
        :param index:int
        :param file_name:str
        :return:
        """
        self.ui.arg_comboBox.insertItem(index, file_name)

    def set_selected_arg(self, index):
        """
        Set the selected file in comboBox
        :param index:int - the order of the file list
        :return: None
        """
        self.ui.arg_comboBox.setCurrentIndex(index)

    def del_key(self):
        """
        Set the key as default in the selected item in the key binding table
        :return: None
        """
        if self.ui.key_binding_table.currentColumn() == 1 or self.ui.key_binding_table.currentColumn() == 2:
            self.ui.key_binding_table.currentItem().setText('未設置')
        else:
            self.ui.key_binding_table.item(self.ui.key_binding_table.currentRow(), 1).setText('未設置')
            self.ui.key_binding_table.item(self.ui.key_binding_table.currentRow(), 2).setText('未設置')

    def save_key_binding_setting(self):
        """
        Save the key binding
        :return: None
        """
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
        """
        Add the filename in the profile list
        :param file_name: str
        :return: None
        """
        self.ui.profile_list.addItem(file_name)

    def profile_info_state_unsaved(self):
        self.ui.profile_info_state.setText('尚未儲存')
        self.ui.profile_info_state_box.setStyleSheet('background-color:rgb(255, 85, 0)')

    def profile_info_state_saved(self):
        self.ui.profile_info_state.setText('已儲存')
        self.ui.profile_info_state_box.setStyleSheet('')

    def set_profile_list_selected_item(self, index, file_name):
        """
        Set up the selected filename in UI
        :param index: int
        :param file_name: str
        :return: None
        """
        self.ui.profile_list.setCurrentRow(index)
        self.ui.selected_profile.setText(file_name)
        self.ui.profile_seleted.setText(file_name)
        self.cam_thread.update_key_binding(self.key_binding_provider.settings)

    def set_profile_list_set_description(self, profile_name, description):
        """
        Set up the filename and it's description in UI
        :param profile_name:
        :param description:
        :return:
        """
        self.ui.profile_name.setPlainText(profile_name)
        self.ui.profile_description_context.setPlainText(description)

    def set_key_binding_table_row(self, row, value):
        """
        Set up key binding in the table
        :param row: int
        :param value: int
        :return: None
        """
        if row == self.ui.key_binding_table.rowCount():
            self.ui.key_binding_table.setRowCount(self.ui.key_binding_table.rowCount() + 1)
        for i in range(3):
            new_item = QTableWidgetItem((lambda: value[i] if int(value[i]) != -1 else '未設置')())
            new_item.setTextAlignment(4)
            self.ui.key_binding_table.setItem(row, i, new_item)

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

    def open_caption_window(self):
        """
        Open the caption window
        :return: None
        """
        ui = CaptionWindowUI()
        ui.setupUi(self.caption_window)
        self.caption_window.show()

    def video_start(self):
        """
        Update the argument settings in video thread and play the video, show how the mediapipe works in these settings
        :return: None
        """
        args = self.get_arg()
        self.video_thread.update_arg_settings(args)
        self.video_thread.start()

    def video_display(self, scene):
        """
        Update the frame in the graphicsView
        :param scene: QGraphicsScene
        :return: None
        """
        self.ui.video_graphicsView.setScene(scene)

    def cam_display(self, scene):
        """
        Update the frame in the graphicsView
        :param scene: QGraphicsScene
        :return: None
        """
        self.ui.cam_graphicsView.setScene(scene)

    def cam_not_working(self):
        self.ui.power_btn.setStyleSheet('background-color: rgb(230, 0, 0);'
                                        'border-radius:25px')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/icons/icons/' + 'warning' + '.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ui.power_btn.setIcon(icon)
        self.ui.power_btn.setEnabled(False)

    def argument_provider_connect_init(self):
        self.arg_provider.trigger_load_arg_list.connect(self.set_arg_comboBox)
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
        self.cam_thread.trigger_show_func.connect(self.ui.func_result_label.setText)
        self.cam_thread.trigger_OCR.connect(self.screen_shooter.start)
        self.screen_shooter.trigger_OCR.connect(lambda result: notification.notify(
            # title of the notification,
            title="OCR Result",
            # the body of the notification
            message=result,
            # creating icon for the notification
            # we need to download a icon of ico file format
            # the notification stays for 50sec
            timeout=5
        ))

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
        self.ui.del_key_btn.clicked.connect(self.del_key)
        self.ui.set_default_btn.clicked.connect(self.key_binding_provider.set_setting_default)
        self.ui.caption_btn.clicked.connect(self.open_caption_window)

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
