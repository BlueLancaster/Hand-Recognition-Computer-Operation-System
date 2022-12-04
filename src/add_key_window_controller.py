from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

from UI.add_key_window import Ui_AddKeyWindow as AddKeyWindowUI


class AddKeyWindow(QtWidgets.QMainWindow):
    trigger_add_key = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.ui = AddKeyWindowUI()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.label_flag = [False, False, False]
        self.labels = [self.ui.label_2, self.ui.label_3, self.ui.label_4]
        self.special_key = {
            16777223: 'del',
            16777248: 'shift',
            16777235: 'up',
            16777237: 'down',
            16777234: 'left',
            16777236: 'right',
            16777249: 'ctrl',
            16777251: 'alt',
            32: 'space',
            16777217: 'tab',
            16777250: 'win',
            16777219: 'backspace',
            16777252: 'capslock',
            16777220: 'enter'
        }

        for i in range(3):
            self.labels[i].mouseDoubleClickEvent = lambda event: self.reset()

    def keyPressEvent(self, event):
        """
        Override the event for get the key
        :param event:QKeyEvent
        :return: None
        """
        text = None
        if event.key() == QtCore.Qt.Key_Escape:
            result_list = []
            for i in range(3):
                if self.labels[i].text() != '未設置' :
                    result_list.append(self.labels[i].text())
            self.trigger_add_key.emit(result_list)
            self.reset()
            self.close()
            return
        elif 16777264 <= event.key() <= 16777275:
            text = 'f' + str(event.key() - 16777263)
        elif self.special_key.get(event.key()):
            text = self.special_key.get(event.key())
        else:
            try:
                text = chr(event.key()).lower()
            except:
                return

        for i in range(3):
            if not self.label_flag[i]:
                self.labels[i].setText(text)
                self.label_flag[i] = True
                break

    def reset(self):
        for i in range(3):
            self.labels[i].setText('未設置')
            self.label_flag[i] = False
