import copy
import multiprocessing
import time
from collections import deque, Counter

import cv2 as cv
import qimage2ndarray
import mediapipe as mp
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsScene

from model.double_hands_classifier.double_hands_classifier import DoubleHandsClassifier
from model.single_hand_classifier.single_hand_classifier import SingleHandClassifier
from model.landmark_eight_history_classifier.landmark_eight_history_classifier import LandmarkEightHistoryClassifier
from utils.cam_thread_tool import read_labels, calc_bounding_rect, calc_landmark_list, pre_process_landmark, \
    pre_process_point_history, get_distance
from utils.cvfpscalc import CvFpsCalc
from utils.drawing import draw_info_text, draw_bounding_rect, draw_moving_range, draw_point_history, draw_info
from utils.hot_key import PPT_full_screen, back_desktop, adjust_size, scroll_down, scroll_up, paste, copy_mode, \
    PPT_razer
from utils.mouseController import left_up, mouse, mouse_moving, left_down, right_click
from utils.one_euro_filter import HandCapture
from utils.textshot import screenshot1


class VideoThread(QThread):
    """
    a thread for playing the video in order to test the effect of the arguments and mediapipe
    """
    trigger_display = pyqtSignal(QGraphicsScene)
    trigger_left_gesture = pyqtSignal(str)
    trigger_right_gesture = pyqtSignal(str)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands

    def __init__(self, arg_settings):
        super(VideoThread, self).__init__()
        self.__video = cv.VideoCapture('../video/test.mp4')
        if self.__video.isOpened():
            print("video is ready")
        else:
            print("video is not opened or existed")
        self.__video.set(cv.CAP_PROP_FRAME_WIDTH, 480)
        self.__video.set(cv.CAP_PROP_FRAME_HEIGHT, 360)
        self.__hands = self.mp_hands.Hands()
        self.__hand_capture = HandCapture()
        self.update_arg_settings(arg_settings)

    def run(self):
        self.__video.set(cv.CAP_PROP_POS_FRAMES, 0)
        while self.__video.isOpened():
            ret, frame = self.__video.read()
            if not ret:
                break
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            results = self.__hands.process(cv.cvtColor(frame, cv.COLOR_BGR2RGB))
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
        # init
        super(CamThread, self).__init__()
        self.switch_state = False
        # <---cap settings --->
        self.__cam = cv.VideoCapture(0)
        if self.__cam.isOpened():
            print("cam is ready")
        else:
            print("cam is not opened or existed")
        self.__cam.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        self.__cam.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        self.flip_mode = 1  # 0: vertical, 1: horizon, -1: both, 2: not flip
        self.fps_cal = CvFpsCalc(buffer_len=10)

        # <--- gesture recognition settings --->
        self.__hands = self.mp_hands.Hands()
        self.left_hand_capture = HandCapture()
        self.right_hand_capture = HandCapture()
        self.update_arg_settings(arg_settings)
        self.key_binding = key_binding_setting
        self.use_rect = True

        # <--- single hand gesture history --->
        self.landmark_eight_history = deque(maxlen=16)
        self.dynamic_gesture_history = deque(maxlen=16)
        self.last_execution_time = 0
        self.right_single_hand_history = deque(maxlen=8)
        self.left_single_hand_history = deque(maxlen=8)
        self.last_two_handID = [-1, -1]
        self.most_common_left_handID = 0
        self.most_common_right_handID = 0

        # <--- double hands gesture history --->
        self.double_hands_history_length = 32
        self.double_hands_history = deque(maxlen=self.double_hands_history_length)
        self.pre_processed_double_hands_history_list = []
        self.landmark_eight_left = [0, 0]
        self.landmark_eight_right = [0, 0]

        # <---model setting--->
        self.single_hand_classifier = SingleHandClassifier()
        self.point_history_classifier = LandmarkEightHistoryClassifier()
        self.double_hands_classifier = DoubleHandsClassifier()
        self.single_hand_classifier_labels = read_labels(
            'model/single_hand_classifier/single_hand_classifier_label.csv')
        self.point_history_classifier_labels = read_labels(
            'model/landmark_eight_history_classifier/landmark_eight_history_classifier_label.csv')
        self.double_hands_classifier_labels = read_labels(
            'model/double_hands_classifier/double_hands_classifier_label.csv')

        # <--- variables for mouse --->
        self.previous_pos = [0, 0]
        self.past_distance = 1

    def run(self):
        print('run start')
        sub_process = multiprocessing.Process(target=screenshot1)
        while self.__cam.isOpened() and self.switch_state:
            fps = self.fps_cal.get()
            success, frame = self.__cam.read()
            if not success:
                print("Ignoring empty camera frame.")
                break
            if self.flip_mode != 2:
                frame = cv.flip(frame, self.flip_mode)  # Mirror display
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            debug_frame = copy.deepcopy(frame)
            frame.flags.writeable = False
            results = self.__hands.process(frame)
            frame.flags.writeable = True
            two_handID = [-1, -1]
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    # preprocessing filter
                    if handedness.classification[0].label == 'Left':
                        pre_joints = self.left_hand_capture.process(hand_landmarks)
                        for i, landmarks in enumerate(hand_landmarks.landmark):
                            landmarks.x = pre_joints[i][0]
                            landmarks.y = pre_joints[i][1]
                            landmarks.z = pre_joints[i][2]
                    elif handedness.classification[0].label == 'Right':
                        pre_joints = self.right_hand_capture.process(hand_landmarks)
                        for i, landmarks in enumerate(hand_landmarks.landmark):
                            landmarks.x = pre_joints[i][0]
                            landmarks.y = pre_joints[i][1]
                            landmarks.z = pre_joints[i][2]
                    # Bounding box calculation
                    rect = calc_bounding_rect(debug_frame, hand_landmarks)
                    # Landmark calculation
                    landmark_list = calc_landmark_list(debug_frame, hand_landmarks)
                    # Conversion to relative coordinates / normalized coordinates
                    pre_processed_landmark_list = pre_process_landmark(landmark_list)
                    pre_processed_point_history_list = pre_process_point_history(
                        debug_frame, self.landmark_eight_history)
                    # Hand sign classification
                    hand_sign_id = self.single_hand_classifier(pre_processed_landmark_list)
                    # single most setting
                    if len(results.multi_hand_landmarks) == 2:
                        self.pre_processed_double_hands_history_list = pre_process_point_history(debug_frame,
                                                                                                 self.double_hands_history)
                    if handedness.classification[0].label == 'Left':
                        self.left_single_hand_history.append(hand_sign_id)
                        self.most_common_left_handID = Counter(self.left_single_hand_history).most_common(1)[0][0]
                        two_handID[0] = self.most_common_left_handID
                        self.landmark_eight_left = [
                            landmark_list[8][0], landmark_list[8][1]]

                    else:
                        self.right_single_hand_history.append(hand_sign_id)
                        self.most_common_right_handID = Counter(self.right_single_hand_history).most_common(1)[0][0]
                        two_handID[1] = self.most_common_right_handID
                        self.landmark_eight_right = [
                            landmark_list[8][0], landmark_list[8][1]]

                    # Drawing part
                    debug_frame = draw_bounding_rect(self.use_rect, debug_frame, rect)
                    self.mp_drawing.draw_landmarks(
                        debug_frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style())

                    draw_info_text(
                        debug_frame,
                        rect,
                        handedness,
                        self.single_hand_classifier_labels[
                            (lambda: self.most_common_left_handID
                            if handedness.classification[0].label == 'Left'
                            else self.most_common_right_handID)()],
                        "",
                    )

                    # update UI gesture result and function called
                    if handedness.classification[0].label == 'Left':
                        self.trigger_show_left_hand.emit(self.
                                                         single_hand_classifier_labels[self.most_common_left_handID])
                    else:
                        self.trigger_show_right_hand.emit(self.
                                                          single_hand_classifier_labels[self.most_common_right_handID])
                # get the function binding on keys
                function_mode = self.key_binding.get(tuple(two_handID))
                self.trigger_show_func.emit(self.function_label(function_mode))

                # do  something corresponding to function code
                if function_mode == 0:  # Point gesture
                    left_up()
                    mouse(results.multi_hand_landmarks[0].landmark[6].x,
                          results.multi_hand_landmarks[0].landmark[6].y)

                elif function_mode == 17:  # two hand dynamic
                    self.double_hands_history.append(self.landmark_eight_left)
                    self.double_hands_history.append(self.landmark_eight_right)
                    # print(double_hands_history)
                    if len(self.pre_processed_double_hands_history_list) == (self.double_hands_history_length * 2):
                        double_hands_id = self.double_hands_classifier(self.pre_processed_double_hands_history_list)
                        if double_hands_id == 0:
                            print(00)
                            PPT_full_screen()
                        elif double_hands_id == 1:
                            print(11)
                            back_desktop()

                if time.time() - self.last_execution_time < 0.1:
                    pass
                else:
                    distance = get_distance(
                        results, 640, 480)
                    if function_mode == 1:
                        if sub_process.is_alive():
                            print('sub process is alive')
                        else:
                            sub_process.start()
                    elif function_mode == 2:
                        pass
                        # translate()
                    elif function_mode == 3 and self.key_binding.get(tuple(self.last_two_handID)) == 3:
                        adjust_size(distance, self.past_distance)
                    elif function_mode == 8:
                        PPT_razer()
                    elif function_mode == 9:
                        copy_mode()
                    elif function_mode == 10:
                        paste()
                    elif function_mode == 12:
                        scroll_up()
                    elif function_mode == 13:
                        scroll_down()
                    elif function_mode == 15:
                        self.previous_pos = mouse_moving(results, self.previous_pos)
                        if self.key_binding.get(tuple(self.last_two_handID)) != 15:
                            left_down()
                    elif function_mode == 16:
                        right_click()
                    self.last_execution_time = time.time()
                    self.past_distance = distance
                    self.last_two_handID = two_handID

            else:
                self.dynamic_gesture_history.append([0, 0])
                self.double_hands_history.append([0, 0])
                self.double_hands_history.append([0, 0])
            # debug_frame = draw_moving_range(debug_frame, get_moving_range())
            debug_frame = draw_point_history(debug_frame, self.dynamic_gesture_history)
            debug_frame = draw_info(debug_frame, fps, 0, 0)

            # update UI graphic_view
            scene = QGraphicsScene(self)
            scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(debug_frame)))
            self.trigger_display.emit(scene)

    def update_arg_settings(self, settings):
        self.__hands = self.mp_hands.Hands(model_complexity=(lambda: 1 if settings['model_complexity'] else 0)(),
                                           max_num_hands=2,
                                           min_detection_confidence=settings['min_detection_confidence'],
                                           min_tracking_confidence=settings['min_tracking_confidence'])
        self.left_hand_capture.update_filter_arg(settings['min_cutoff'], settings['rate'])
        self.right_hand_capture.update_filter_arg(settings['min_cutoff'], settings['rate'])

    def update_key_binding(self, new_key_binding_settings):
        self.key_binding = new_key_binding_settings

    def switching_state(self):
        if self.switch_state:
            self.switch_state = False
        else:
            self.switch_state = True
            self.start()

    @staticmethod
    def function_label(code):
        if code == 0:
            return "操作滑鼠模式"
        elif code == 1:
            return "截圖文字辨識"
        elif code == 2:
            return "文字翻譯"
        elif code == 3:
            return "放大縮小"
        elif code == 4:
            return "全螢幕"
        elif code == 5:
            return "返回桌面"
        elif code == 6:
            return "下一頁"
        elif code == 7:
            return "上一頁"
        elif code == 8:
            return "PPT 雷射筆"
        elif code == 9:
            return "複製"
        elif code == 10:
            return "貼上"
        elif code == 11:
            return "順時針旋轉90度"
        elif code == 12:
            return "向上滑"
        elif code == 13:
            return "向下滑"
        elif code == 14:
            return "螢幕截圖"
        elif code == 15:
            return "滑鼠左鍵單點"
        elif code == 16:
            return "滑鼠右鍵單點"
        elif code == 17:
            return "進入雙手動態模式"
