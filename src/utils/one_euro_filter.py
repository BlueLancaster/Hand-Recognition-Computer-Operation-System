import numpy as np


class LowPassFilter:
    """
    main filter that use exponential smoothing
    """
    def __init__(self):
        self.prev_raw_value = None
        self.prev_filtered_value = None

    def process(self, value, alpha):
        if self.prev_raw_value is None:
            s = value
        else:
            s = alpha * value + (1.0 - alpha) * self.prev_filtered_value
        self.prev_raw_value = value
        self.prev_filtered_value = s
        return s


class OneEuroFilter:
    """
    Initialize the one euro filter.
    """
    def __init__(self, min_cutoff=1.0, beta=0.0, d_cutoff=1.0, freq=30):
        self.freq = freq
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_filter = LowPassFilter()
        self.dx_filter = LowPassFilter()

    def compute_alpha(self, cutoff):
        te = 1.0 / self.freq
        tau = 1.0 / (2 * np.pi * cutoff)
        return 1.0 / (1.0 + tau / te)

    def process(self, x):
        prev_x = self.x_filter.prev_raw_value
        dx = 0.0 if prev_x is None else (x - prev_x) * self.freq
        edx = self.dx_filter.process(dx, self.compute_alpha(self.d_cutoff))
        cutoff = self.min_cutoff + self.beta * np.abs(edx)
        return self.x_filter.process(x, self.compute_alpha(cutoff))


class HandCapture:
    """
    compute the smoothing factor
    """
    def __init__(self):
        self.point_filter = OneEuroFilter(4.0, 0.0)
        self.pre_joints = list()

    def update_filter_arg(self, min_cutoff, beta_rate):
        self.point_filter = OneEuroFilter(min_cutoff, beta_rate)

    def process(self, hand_landmarks):
        """
        dx : The rate of change
        edx : The filtered rate of change
        cutoff : The cutoff frequency
        """
        self.pre_joints = list()
        for index, landmark in enumerate(hand_landmarks.landmark):
            self.pre_joints.append([landmark.x, landmark.y, landmark.z])
        self.pre_joints = np.array(self.pre_joints)
        self.pre_joints = self.point_filter.process(
            self.pre_joints)  # filter the jitter joints
        return self.pre_joints
