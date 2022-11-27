import copy
import csv
import itertools
import math

import numpy as np
import cv2 as cv


def read_labels(path):
    with open(path, encoding='utf-8-sig') as f:
        labels = csv.reader(f)
        labels = [
            row[0] for row in labels
        ]
    return labels


def get_distance(results, cam_width, cam_height):
    landmark_zero = results.multi_hand_landmarks[0].landmark[0]
    landmark_five = results.multi_hand_landmarks[0].landmark[5]

    x1 = landmark_zero . x * cam_width
    y1 = landmark_zero . y * cam_height
    x2 = landmark_five . x * cam_width
    y2 = landmark_five . y * cam_height

    temp = np.array([x1, y1]) - np.array([x2, y2])
    distance = math.hypot(temp[0], temp[1])
    return distance


def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)
    return [x, y, x + w, y + h]


def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y, landmark_z])

    return landmark_point


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)
    # landmark_list 為int且為在圖片上座標
    # Convert to relative coordinates
    base_x, base_y, base_z = 0, 0, 0

    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y, base_z = landmark_point[0], landmark_point[1], landmark_point[2]
        temp_landmark_list[index][0] = (temp_landmark_list[index][0] - base_x)
        temp_landmark_list[index][1] = (temp_landmark_list[index][1] - base_y)
        temp_landmark_list[index][2] = temp_landmark_list[index][2] - base_z

    def length(landmarks):
        return math.sqrt(landmarks[0] * landmarks[0] + landmarks[1] * landmarks[1])

    max_value = max(list(map(length, temp_landmark_list)))

    for index, landmark_point in enumerate(temp_landmark_list):
        temp_landmark_list[index][0] = temp_landmark_list[index][0]/max_value
        temp_landmark_list[index][1] = temp_landmark_list[index][1]/max_value

    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    return temp_landmark_list


def pre_process_point_history(image, point_history):
    image_width, image_height = image.shape[1], image.shape[0]

    temp_point_history = copy.deepcopy(point_history)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, point in enumerate(temp_point_history):
        if index == 0:
            base_x, base_y = point[0], point[1]

        temp_point_history[index][0] = (temp_point_history[index][0] -
                                        base_x) / image_width
        temp_point_history[index][1] = (temp_point_history[index][1] -
                                        base_y) / image_height

    # Convert to a one-dimensional list
    temp_point_history = list(
        itertools.chain.from_iterable(temp_point_history))

    return temp_point_history


def record(number, mode):
    if mode == 3 and (0 <= number <= 9):
        return True, 40, number
    return False, 0, -1

