# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_key_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AddKeyWindow(object):
    def setupUi(self, AddKeyWindow):
        AddKeyWindow.setObjectName("AddKeyWindow")
        AddKeyWindow.resize(457, 325)
        self.centralwidget = QtWidgets.QWidget(AddKeyWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Adobe 黑体 Std R")
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label, 0, QtCore.Qt.AlignHCenter)
        self.verticalLayout.addWidget(self.frame)
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setFamily("Adobe 黑体 Std R")
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2, 0, QtCore.Qt.AlignHCenter)
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setFamily("Adobe 黑体 Std R")
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3, 0, QtCore.Qt.AlignHCenter)
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setFamily("Adobe 黑体 Std R")
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4, 0, QtCore.Qt.AlignHCenter)
        self.verticalLayout.addWidget(self.frame_2)
        AddKeyWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(AddKeyWindow)
        QtCore.QMetaObject.connectSlotsByName(AddKeyWindow)

    def retranslateUi(self, AddKeyWindow):
        _translate = QtCore.QCoreApplication.translate
        AddKeyWindow.setWindowTitle(_translate("AddKeyWindow", "AddKeyWindow"))
        self.label.setText(_translate("AddKeyWindow", "依照順序按下按鍵(最多三個)"))
        self.label_2.setText(_translate("AddKeyWindow", "未設置"))
        self.label_3.setText(_translate("AddKeyWindow", "未設置"))
        self.label_4.setText(_translate("AddKeyWindow", "未設置"))