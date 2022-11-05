import cv2
import mediapipe as mp
import numpy
import qimage2ndarray as qimage2ndarray
from PyQt5 import QtWidgets, QtGui, QtCore
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsScene

from ui_class import Ui_MainWindow

from video_test import Ui_VideoWindow


class UiThread(QThread):
    trigger1 = pyqtSignal(str)
    trigger2 = pyqtSignal(str)

    def __init__(self):
        # 初始化函数
        super(UiThread, self).__init__()

    def run(self):
        for i in range(20):
            # 通过自定义信号把待显示的字符串传递给槽函数
            sleep(0.1)
            self.trigger1.emit(str(i))
            self.trigger2.emit(str(i))


class VideoThread(QThread):
    trigger = pyqtSignal(numpy.ndarray)

    def __init__(self):
        # 初始化函数
        super(VideoThread, self).__init__()
        self.cam = cv2.VideoCapture(0)
        if self.cam.isOpened():
            print("camera  is ready")
        else:
            print("camera  is not ready")
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def run(self):
        while True:
            ret, frame = self.cam.read()
            if not ret:
                continue
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.trigger.emit(frame)
            # cv2.imshow('mouse', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cam.release()
                cv2.destroyAllWindows()
                break


class MainWindowController(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()  # in python3, super(Class, self).xxx = super().xxx
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()
        self.counter = 0
        self.ui.pushButton.clicked.connect(self.buttonClicked)
        self.ui.pushButton_2.clicked.connect(self.buttonClicked)
        self.ui_thread = UiThread()
        self.ui_thread.trigger1.connect(self.display)
        self.ui_thread.trigger2.connect(self.display)

    def setup_control(self):
        self.ui.textEdit.setText('Happy World!')

    def buttonClicked(self):
        self.ui_thread.start()

    def display(self, temp):
        self.ui.textEdit.append(temp)


class VideoWindowController(QtWidgets.QMainWindow):
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(model_complexity=0,
                           max_num_hands=1,
                           min_detection_confidence=0.5,
                           min_tracking_confidence=0.5)

    def __init__(self):
        super().__init__()
        self.ui = Ui_VideoWindow()
        self.ui.setupUi(self)
        self.video_thread = VideoThread()
        self.video_thread.trigger.connect(self.display)
        self.ui.openCamButton.clicked.connect(self.openCam)

    def openCam(self):
        print(self.video_thread.started)
        self.video_thread.start()

    def display(self, frame):
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 將節點和骨架繪製到影像中
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())
        scene = QGraphicsScene(self)
        scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(frame)))
        self.ui.graphicsView.setScene(scene)
