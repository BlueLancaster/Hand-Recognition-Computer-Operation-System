import json
import os
from PyQt5.QtCore import QThread, pyqtSignal

"""
A class for managing json saving the dict which is about key binding or environment argument
"""


class SettingsProvider(QThread):
    trigger_update_profile_list = pyqtSignal(int)
    trigger_read_file = pyqtSignal(str)
    trigger_selected = pyqtSignal(int)
    trigger_info = pyqtSignal(str, str)

    def run(self):
        """
        It is called by start(),and it will update UI
        :return: None
        """
        self.read_file_list()
        self.trigger_update_profile_list.emit(1)
        for index, file_name in enumerate(self.__file_list):
            self.trigger_read_file.emit(file_name)
            if self.__file_name == file_name:
                self.trigger_selected.emit(index)
                self.trigger_info.emit(self.__file_name, self.settings['Description'])

    def get_converted_settings(self):
        """
        The key type convertor between str used in file and tuple used in program
        because tuple is not supported in json.This would modify self.settings by popping and insert
        :return: None
        """
        settings = dict()
        if type(list(self.settings.keys())[1]) == str:
            for key in tuple(self.settings.keys()):
                if key != 'Description':
                    settings[tuple(map(int, key.split(',')))] = self.settings[key]
                else:
                    settings['Description'] = self.settings[key]
        elif type(list(self.settings.keys())[1]) == tuple:
            for key in tuple(self.settings.keys()):
                if key != 'Description':
                    settings[str(key[0]) + ',' + str(key[1])] = self.settings.pop(key)
                else:
                    settings['Description'] = self.settings[key]
        return settings

    def change_current_settings_file(self, index):
        if index != self.__file_list.index(self.__file_name):
            self.__file_name = self.__file_list[index]
            self.read_json()
            self.trigger_info.emit(self.__file_name, self.settings['Description'])

    def get_default(self):
        """
        Get the default settings corresponding to self.__settings_type
        :return: dict
        """
        if self.__settings_type == 0:
            self.__file_name = 'default_env'
            default_settings = {
                "width": 640,
                "height": 480,
                "model_complexity": 1,
                "min_detection_confidence": 0.7,
                "min_tracking_confidence": 0.5
            }
        elif self.__settings_type == 1:
            self.__file_name = 'default_binding'
            default_settings = {
                'Description': 'This is just a default settings profile',
                '-1,2': 0,
                '2,-1': 0,
                '7,7': 1,
                '-1,6': 2,
                '6,-1': 2,
                '-1,1': 3,
                '1,-1': 3,
                '2,7': 8,
                '7,2': 8,
                '0,5': 9,
                '5,0': 9,
                '2,5': 10,
                '5,2': 10,
                '1,7': 12,
                '7,1': 13,
                '-1,3': 15,
                '3,-1': 15,
                '-1,4': 16,
                '4,-1': 16,
                '2,2': 17,
                '-1,0': -1
            }
        return default_settings

    def read_json(self):
        """
        Read dict in the json
        :return: None
        """
        with open(self.__file_path + self.__file_name + '.json') as f:
            self.settings = json.load(f)
        if self.__settings_type == 1:
            self.settings = self.get_converted_settings()

    def create_json(self):
        """
        Create the json with default settings
        :return: None
        """
        self.settings = self.get_default()

    def save_json(self, new_file_name=None, new_description=None):
        """
        If object would be deconstructed,the setting must be saved in json
        :parameter: new_file_name:str
        :return: None
        """
        if new_description is not None:
            self.settings['Description'] = new_description
        with open(self.__file_path + self.__file_name + '.json', "w") as f:
            if self.__settings_type == 1:
                json.dump(self.get_converted_settings(), f, indent=len(self.settings))
            else:
                json.dump(self.settings, f, indent=len(self.settings))
        if new_file_name is not None:
            os.rename(self.__file_path + self.__file_name + '.json', self.__file_path + new_file_name + '.json')
            self.__file_name = new_file_name
        self.start()

    def read_file_list(self):
        """
        get all filenames under the path
        :return:None
        """
        self.__file_list = [os.path.splitext(filename)[0] for filename in os.listdir(self.__file_path)]

    def __init__(self, provider_type):
        """
        Create the filename corresponding to the parameter called provider_type
        :parameter provider_type:int
        """
        super(SettingsProvider, self).__init__()
        self.__settings_type = provider_type
        self.settings = dict()
        self.__file_list = list()
        if provider_type == 0:
            self.__file_path = 'settings/'
            self.__file_name = 'env'
        elif provider_type == 1:
            self.__file_path = 'profiles/'
            self.__file_name = 'key_binding'
        try:
            self.read_json()
        except IOError:
            self.create_json()
