import cv2
import qimage2ndarray
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsScene
from utils.one_euro_filter import *


class VideoThread(QThread):
    trigger = pyqtSignal(QGraphicsScene)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    def __init__(self, settings):
        # 初始化函数
        super(VideoThread, self).__init__()
        self.video = cv2.VideoCapture('../video/test.mp4')
        if self.video.isOpened():
            print("video is ready")
        else:
            print("video is not opened or existed")
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(model_complexity=0,
                                         max_num_hands=1,
                                         min_detection_confidence=0.5,
                                         min_tracking_confidence=0.5)
        self.hand_capture = HandCapture()

    def run(self):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while self.video.isOpened():
            ret, frame = self.video.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
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
            self.trigger.emit(scene)

    def update_settings(self, settings):
        self.hands = self.mp_hands.Hands(model_complexity=(lambda: 1 if settings['model_complexity'] else 0)(),
                                         max_num_hands=1,
                                         min_detection_confidence=settings['min_detection_confidence'],
                                         min_tracking_confidence=settings['min_tracking_confidence'])
