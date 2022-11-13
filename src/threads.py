import cv2
import qimage2ndarray
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsScene
from utils.one_euro_filter import *


class VideoThread(QThread):
    trigger_display = pyqtSignal(QGraphicsScene)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands

    def __init__(self, arg_settings):
        # 初始化函数
        super(VideoThread, self).__init__()
        self.__video = cv2.VideoCapture('../video/test.mp4')
        if self.__video.isOpened():
            print("video is ready")
        else:
            print("video is not opened or existed")
        self.__video.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        self.__video.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        self.__hands = self.mp_hands.Hands()
        self.__hand_capture = HandCapture()
        self.update_arg_settings(arg_settings)

    def run(self):
        self.__video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while self.__video.isOpened():
            ret, frame = self.__video.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.__hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    pre_joints = self.__hand_capture.process(hand_landmarks)
                    for i, landmarks in enumerate(hand_landmarks.landmark):
                        landmarks.x = pre_joints[i][0]
                        landmarks.y = pre_joints[i][1]
                        landmarks.z = pre_joints[i][2]
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())
            scene = QGraphicsScene(self)
            scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(frame)))
            self.trigger_display.emit(scene)

    def update_arg_settings(self, settings):
        self.__hands = self.mp_hands.Hands(model_complexity=(lambda: 1 if settings['model_complexity'] else 0)(),
                                           max_num_hands=1,
                                           min_detection_confidence=settings['min_detection_confidence'],
                                           min_tracking_confidence=settings['min_tracking_confidence'])
        self.__hand_capture.update_filter_arg(settings['min_cutoff'], settings['rate'])


class CamThread(QThread):
    trigger_display = pyqtSignal(QGraphicsScene)
    trigger_show_func = pyqtSignal(str)
    trigger_show_left_hand = pyqtSignal(str)
    trigger_show_right_hand = pyqtSignal(str)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands

    def __init__(self, key_binding_setting, arg_settings):
        # 初始化函数
        super(CamThread, self).__init__()
        self.__cam = cv2.VideoCapture(0)
        if self.__cam.isOpened():
            print("cam is ready")
        else:
            print("cam is not opened or existed")
        self.__cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.__cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.__hands = self.mp_hands.Hands()
        self.hand_capture = HandCapture()
        self.update_arg_settings(arg_settings)
        self.key_binding = key_binding_setting

    def run(self):
        while self.__cam.isOpened():
            ret, frame = self.__cam.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.__hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    pre_joints = self.hand_capture.process(hand_landmarks)
                    for i, landmarks in enumerate(hand_landmarks.landmark):
                        landmarks.x = pre_joints[i][0]
                        landmarks.y = pre_joints[i][1]
                        landmarks.z = pre_joints[i][2]
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())
            scene = QGraphicsScene(self)
            scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(frame)))
            self.trigger_display.emit(scene)

    def update_arg_settings(self, settings):
        self.__hands = self.mp_hands.Hands(model_complexity=(lambda: 1 if settings['model_complexity'] else 0)(),
                                             max_num_hands=1,
                                             min_detection_confidence=settings['min_detection_confidence'],
                                             min_tracking_confidence=settings['min_tracking_confidence'])
        self.hand_capture.update_filter_arg(settings['min_cutoff'], settings['rate'])

    def update_key_binding(self, new_key_binding_settings):
        self.key_binding = new_key_binding_settings
