from PyQt5 import QtWidgets
import sys
from controller import MainWindowController, VideoWindowController

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindowController()
    window2 = VideoWindowController()
    window.show()
    window2.show()
    sys.exit(app.exec_())
