from PyQt5 import QtWidgets
import sys
from main_controller import MainController


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_controller = MainController()
    main_controller.show()
    sys.exit(app.exec_())

