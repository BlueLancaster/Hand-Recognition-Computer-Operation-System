from PyQt5 import QtWidgets, QtCore, QtGui
from UI.add_key_window import Ui_AddKeyWindow as AddKeyWindowUI


class AddKeyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = AddKeyWindowUI()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.label_flag = [False, False, False]
        self.label = [self.ui.label_2, self.ui.label_3, self.ui.label_4]
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
            16777252: 'capslock'
        }

    def keyPressEvent(self, event):
        """
        Override the event for get the key
        :param event:QKeyEvent
        :return: None
        """
        text = None
        if event.key() == QtCore.Qt.Key_Escape:
            self.reset()
            self.close()
        elif event.key() == QtCore.Qt.Key_Enter:
            pass
        elif 16777264 <= event.key() <= 16777275:
            text = 'f' + str(event.key() - 16777263)
        elif self.special_key.get(event.key()):
            text = self.special_key.get(event.key())
        else:
            text = chr(event.key()).lower()

        for i in range(3):
            if not self.label_flag[i]:
                self.label[i].setText(text)
                self.label_flag[i] = True
                break

    def reset(self):

        self.label[1].setText('未設置')
        self.label_flag[1] = False
