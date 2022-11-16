import cv2
import time
import mediapipe as mp
import numpy as np
import pyautogui
import math
import win32api
import win32con
# ----moving variable----
wScr, hScr = pyautogui.size()   # 返回电脑屏幕的宽和高(1920.0, 1080.0)
wCam, hCam = 640, 480   # 视频显示窗口的宽和高
moving_range = [(5, 5), (581, 357)]
# [(8,65),(632,415)]
pt1, pt2 = moving_range[0], moving_range[1]   # 虚拟鼠标的移动范围，左上坐标pt1，右下坐标pt2
smoothening = 7
# ----moving variable----
# For webcam input:


def mouse_moving(results, previous_pos=[]):
    pastLocalation_x = previous_pos[0]
    pastLocalation_y = previous_pos[1]
    if results.multi_hand_landmarks is not None:
        # print(type(results.multi_hand_landmarks))
        # 获取食指指尖坐标

        landmark_eight = results.multi_hand_landmarks[0].landmark[6]
        # print(landmark_eight)
        x1 = landmark_eight.x*wCam
        y1 = landmark_eight.y*hCam
        x1 = np.interp(x1, (pt1[0], pt2[0]), (0, wScr))
        y1 = np.interp(y1, (pt1[1], pt2[1]), (0, hScr))

        # （5）检查哪个手指是朝上的

        # 开始移动时，在食指指尖画一个圆圈，看得更清晰一些
        # cv2.circle(image, (x1,y1), 15, (255,255,0), -1)  # 颜色填充整个圆

        # （6）确定鼠标移动的范围
        # 将食指的移动范围从预制的窗口范围，映射到电脑屏幕范围
        smoothen = 5000

        temp = np.array([x1, y1]) - \
            np.array([pastLocalation_x, pastLocalation_y])
        distance = math.hypot(temp[0], temp[1])

        temp[0] = temp[0]/2
        temp[1] = temp[1]/2

        if distance > 20:
            for i in range(smoothen):
                pastLocalation_x = pastLocalation_x + temp[0]/smoothen
                pastLocalation_y = pastLocalation_y + temp[1]/smoothen
                pos = (int(pastLocalation_x), int(pastLocalation_y))
                win32api.SetCursorPos(pos)

            previous_pos[0] = pastLocalation_x
            previous_pos[1] = pastLocalation_y
    return previous_pos


def mouse(landmark_eight_x, landmark_eight_y):
    pastLocalation_x, pastLocalation_y = win32api.GetCursorPos()
    # print(type(results.multi_hand_landmarks))
    # 获取食指指尖坐标
    x1 = landmark_eight_x*wCam
    y1 = landmark_eight_y*hCam
    x1 = np.interp(x1, (pt1[0], pt2[0]), (0, wScr))
    y1 = np.interp(y1, (pt1[1], pt2[1]), (0, hScr))

    # （5）检查哪个手指是朝上的

    # 开始移动时，在食指指尖画一个圆圈，看得更清晰一些
    # cv2.circle(image, (x1,y1), 15, (255,255,0), -1)  # 颜色填充整个圆

    # （6）确定鼠标移动的范围
    # 将食指的移动范围从预制的窗口范围，映射到电脑屏幕范围
    smoothen = 2000

    temp = np.array([x1, y1]) - \
        np.array([pastLocalation_x, pastLocalation_y])
    distance = math.hypot(temp[0], temp[1])

    temp[0] = temp[0]/smoothen
    temp[1] = temp[1]/smoothen

    for i in range(smoothen):
        pastLocalation_x = pastLocalation_x + temp[0]
        pastLocalation_y = pastLocalation_y + temp[1]
        pos = (int(pastLocalation_x), int(pastLocalation_y))
        win32api.SetCursorPos(pos)


def test(arg):
    for i in range(20000):
        print(i)


def left_down():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)


def left_up():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def left_click():
    pyautogui.click(button='left')
    return


def right_click():
    pyautogui.click(button='right')
    return


def get_moving_range():
    return moving_range
