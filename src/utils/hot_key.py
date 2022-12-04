import os
import time
import win32api
import win32con
import win32gui
import win32ui
import pyautogui
import math
import numpy as np

import googletrans
import pyperclip  # 用于将识别出的文字放置到剪切板中方便直接粘贴
import pytesseract
from PIL import ImageGrab
from plyer import notification


def screenShot():
    pyautogui.keyDown('shift')
    pyautogui.keyDown('winleft')
    pyautogui.press('s')
    pyautogui.keyUp('winleft')
    pyautogui.keyUp('shift')
    return


def paste():
    pyautogui.hotkey('ctrl', 'v')


"""funtion mode
0: move_mouse
1: left click
2: right click



"""


def OCR():
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # 按ctrl+c后才执行下面的语句
    # ctrl+c保存截图至剪切板， ImageGrab从剪切板读取图片
    try:
        img1 = ImageGrab.grabclipboard()
        data = pytesseract.image_to_string(img1, lang="eng")
        pyperclip.copy(data)
    except Exception:
        return 'screenshot is not existed'
    return 'success'


def translate():
    try:
        data = pyperclip.paste()
        translator = googletrans.Translator()
        results = translator.translate(data, dest='zh-tw', src='en')
        pyperclip.copy(results.text)
    except Exception as e:
        return None
    return data


def scroll_up():
    pyautogui.scroll(100)


def scroll_down():
    pyautogui.scroll(-100)


def adjust_size(distance, past_distance):
    if distance / past_distance < 0.95:
        win32api.keybd_event(17, 0, 0, 0)  # 按下Ctrl鍵
        win32api.keybd_event(187, 0, 0, 0)  # 按下s鍵
        win32api.keybd_event(187, 0, win32con.KEYEVENTF_KEYUP, 0)  # 釋放Ctrl鍵
        win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)
    elif distance / past_distance > 1.05:
        win32api.keybd_event(17, 0, 0, 0)  # 按下Ctrl鍵
        win32api.keybd_event(189, 0, 0, 0)  # 按下s鍵
        win32api.keybd_event(189, 0, win32con.KEYEVENTF_KEYUP, 0)  # 釋放Ctrl鍵
        win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)


def back_desktop():
    pyautogui.keyDown('winleft')
    pyautogui.press('d')
    pyautogui.keyUp('winleft')


def PPT_next_page():
    pyautogui.press('right')


def PPT_previous_page():
    pyautogui.press('left')


def PPT_razer():
    pyautogui.keyDown('ctrl')
    pyautogui.press('l')
    pyautogui.keyUp('ctrl')


def PPT_full_screen():
    pyautogui.press('alt')
    pyautogui.press('s')
    pyautogui.press('b')


def copy_mode():
    pyautogui.keyDown('ctrl')
    pyautogui.press('v')
    pyautogui.keyUp('ctrl')


def paste():
    pyautogui.keyDown('ctrl')
    pyautogui.press('c')
    pyautogui.keyUp('ctrl')


def press(key):
    pyautogui.press(key)


def hot_key_press(key1, key2):
    pyautogui.keyDown(key1)
    pyautogui.press(key2)
    pyautogui.keyUp(key1)


def rotate_clockwise():
    pyautogui.keyDown('alt')
    for i in range(6):
        pyautogui.press('right')
    pyautogui.keyUp('alt')


def split_screen_left():
    pyautogui.keyDown('winleft')
    pyautogui.press('left')
    time.sleep(0.2)
    pyautogui.press('left')
    pyautogui.keyUp('winleft')


def split_screen_right():
    pyautogui.keyDown('winleft')
    pyautogui.press('right')
    pyautogui.press('right')
    pyautogui.keyUp('winleft')


def custom_hot_key(key_str: str):
    key_list = key_str.split(sep='/')
    key_amount = len(key_list)
    if key_amount == 1:
        pyautogui.press(key_list[0])
    elif key_amount == 2:
        pyautogui.keyDown(key_list[0])
        pyautogui.press(key_list[1])
        pyautogui.keyUp(key_list[0])
    elif key_amount == 3:
        pyautogui.keyDown(key_list[0])
        pyautogui.keyDown(key_list[1])
        pyautogui.press(key_list[2])
        pyautogui.keyUp(key_list[1])
        pyautogui.keyUp(key_list[0])
