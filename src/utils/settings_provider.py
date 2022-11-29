import json
import os
from PyQt5.QtCore import QThread, pyqtSignal

"""
A class for managing json saving the dict which is about key binding or environment argument
"""


class SettingsProvider(QThread):
    """
    An abstract class for I/O file provider
    """
    def run(self):
        pass

    def update_settings(self, new_settings):
        self._settings = new_settings
        self.save_json()

    def read_json(self):
        """
        Read dict in the json file
        :return: None
        """
        with open(self._file_path + self._file_name + '.json') as f:
            self._settings = json.load(f)

    def create_json(self):
        pass

    def save_json(self):
        """
        Save the settings in the current json file
        :parameter: new_file_name:str
        :return: None
        """
        with open(self._file_path + self._file_name + '.json', "w") as f:
            json.dump(self._settings, f, indent=len(self._settings))
        self.start()

    def del_json(self):
        """
        Del the json file
        :return: None
        """
        os.remove(self._file_path + self._file_name + '.json')
        try:
            if self._file_name != self._file_list[0]:
                self._file_name = self._file_list[0]
            else:
                self._file_name = self._file_list[1]
            self.read_json()
        except IndexError:
            self.create_json()
        self.start()

    @property
    def settings(self):
        return self._settings

    def change_current_file(self, index):
        pass

    def read_file_list(self):
        """
        Get all filenames under the path
        :return:None
        """
        self._file_list = [os.path.splitext(filename)[0] for filename in os.listdir(self._file_path)]

    def __init__(self, file_path):
        """
        Create the file under the file path
        :parameter file_path:str
        """
        super(SettingsProvider, self).__init__()
        self._settings = dict()
        self._file_list = list()
        self._file_path = file_path
        self.read_file_list()
        self._file_name = str()


class KeyBindingProvider(SettingsProvider):
    """
    A provider and manager for key binding file
    """
    trigger_clear_profile_list = pyqtSignal(int)
    trigger_load_profile_list = pyqtSignal(str)
    trigger_selected = pyqtSignal(int, str)
    trigger_info = pyqtSignal(str, str)
    trigger_update_key_binding = pyqtSignal(int, tuple)
    trigger_clear_key_table = pyqtSignal(int)
    trigger_save = pyqtSignal(int)

    def run(self):
        """
        It is called by start(),and it will update UI
        :return: None
        """
        self.read_file_list()
        self.trigger_clear_profile_list.emit(1)
        self.trigger_clear_key_table.emit(1)
        for index, file_name in enumerate(self._file_list):
            self.trigger_load_profile_list.emit(file_name)
            if self._file_name == file_name:
                self.trigger_selected.emit(index, self._file_name)
                self.trigger_info.emit(self._file_name, self._settings['Description'])
        for row, key in enumerate(self._settings):
            if key != 'Description':
                self.trigger_update_key_binding.emit(row - 1, tuple(map(str, (self._settings[key], key[0], key[1]))))
        self.trigger_save.emit(1)

    def __get_converted_settings(self):
        """
        The key type convertor between str used in file and tuple used in program
        because tuple is not supported in json.This would modify the settings by popping and insert
        :return: None
        """
        settings = dict()
        index = 0
        if list(self._settings.keys())[0] == 'Description':
            index = 1
        if type(list(self._settings.keys())[index]) == str:
            for key in tuple(self._settings.keys()):
                if key != 'Description':
                    settings[tuple(map(int, key.split(',')))] = self._settings[key]
                else:
                    settings['Description'] = self._settings[key]
        elif type(list(self._settings.keys())[index]) == tuple:
            for key in tuple(self._settings.keys()):
                if key != 'Description':
                    settings[str(key[0]) + ',' + str(key[1])] = self._settings[key]
                else:
                    settings['Description'] = self._settings[key]
        return settings

    def change_current_file(self, index):
        """
        Change the current profile
        :param index: int
        :return: None
        """
        if index != self._file_list.index(self._file_name):
            self._file_name = self._file_list[index]
            self.read_json()
            self.trigger_info.emit(self._file_name, self._settings['Description'])
        self.trigger_save.emit(1)

    def create_json(self):
        """
        Create the json with default settings
        :return: None
        """
        self.__set_default()
        self._file_name = 'new default settings'
        temp = 1
        while self._file_name + str(temp) in self._file_list:
            temp += 1
        self._file_name = self._file_name + str(temp)
        with open(self._file_path + self._file_name + '.json', "w") as f:
            json.dump(self.__get_converted_settings(), f, indent=len(self._settings))
        self.start()

    def read_json(self):
        """
        Read dict in the json
        :return: None
        """
        super().read_json()
        self._settings = self.__get_converted_settings()

    def save_json(self, new_file_name=None, new_description=None):
        """
        Save the key binding settings and the description,modify the current filename
        :param new_file_name: str
        :param new_description: str
        :return:
        """
        if new_description is not None:
            self._settings['Description'] = new_description
        with open(self._file_path + self._file_name + '.json', "w") as f:
            json.dump(self.__get_converted_settings(), f, indent=len(self._settings))
        if new_file_name is not None:
            os.rename(self._file_path + self._file_name + '.json', self._file_path + new_file_name + '.json')
            self._file_name = new_file_name
        self.start()

    def copy_json(self):
        """
        Create a copy of the current file
        :return:
        """
        file_name = self._file_name
        temp = 1
        while file_name + ' [copy] ' + str(temp) in self._file_list:
            temp += 1
        file_name = self._file_name + ' [copy] ' + str(temp)
        with open(self._file_path + file_name + '.json', "w") as f:
            json.dump(self.__get_converted_settings(), f, indent=len(self._settings))
        self.start()

    def set_setting_default(self):
        """
        Set the key binding settings as default and Update the UI
        :return:None
        """
        self.__set_default()
        self.start()

    def __set_default(self):
        """
        Set the key binding settings as default
        :return: None
        """
        self._settings = {
            'Description': 'This is just a default settings profile',
            (-1, 1): 0,
            (1, -1): 0,
            (7, 7): 1,
            (-1, 6): 2,
            (6, -1): 2,
            (-1, 0): 3,
            (0, -1): 3,
            (2, 8): 8,
            (8, 2): 8,
            (0, 5): 9,
            (5, 0): 9,
            (2, 5): 10,
            (5, 2): 10,
            (1, 7): 12,
            (7, 1): 13,
            (-1, 7): 15,
            (7, -1): 15,
            (-1, 8): 16,
            (8, -1): 16,
            (2, 2): 17
        }

    def __init__(self):
        super(KeyBindingProvider, self).__init__('profiles/')
        try:
            self._file_name = self._file_list[0]
            self.read_json()
        except IndexError:
            self.create_json()
            self.read_file_list()


class ArgumentProvider(SettingsProvider):
    """
    A provider and manager for argument file
    """
    trigger_load_arg_list = pyqtSignal(int, str)
    trigger_update_arg = pyqtSignal(dict)
    trigger_selected = pyqtSignal(int)
    trigger_clear_list = pyqtSignal(int)
    trigger_load_arg = pyqtSignal(dict)

    def run(self):
        """
        Update the UI
        :return: None
        """
        self.read_file_list()
        self.trigger_clear_list.emit(1)
        for index, file_name in enumerate(self._file_list):
            self.trigger_load_arg_list.emit(index, file_name)
            if file_name == self._file_name:
                self.trigger_selected.emit(index)
        self.trigger_load_arg.emit(self._settings)

    def set_setting_default(self):
        """
        Set the arguments as default and Update the UI
        :return:
        """
        self.__get_default_argument()
        self.start()

    def __get_default_argument(self):
        """
        Set the arguments as default
        """
        self._settings = {
            'model_complexity': True,
            'min_detection_confidence': 0.7,
            'min_tracking_confidence': 0.5,
            'smooth': 5000,
            'min_cutoff': 2.0,
            'rate': 1.0
        }

    def update_arg_file(self, new_file_name,  new_settings):
        """
        Update the argument file
        :param new_file_name: str
        :param new_settings: str
        :return: None
        """
        if self._file_name != new_file_name:
            os.rename(self._file_path + self._file_name + '.json', self._file_path + new_file_name + '.json')
            self._file_name = new_file_name
        self._settings = new_settings
        self.save_json()

    def change_current_file(self, index):
        """
        Change the current file
        :param index: int
        :return: None
        """
        if index != -1:
            self._file_name = self._file_list[index]
            self.read_json()
            self.trigger_load_arg.emit(self._settings)

    def create_json(self):
        """
        Create the json with default settings
        :return: None
        """
        self.__get_default_argument()
        self._file_name = 'new argument settings'
        temp = 1
        while self._file_name + str(temp) in self._file_list:
            temp += 1
        self._file_name = self._file_name + str(temp)
        with open(self._file_path + self._file_name + '.json', "w") as f:
            json.dump(self._settings, f, indent=len(self._settings))
        self.start()

    def __init__(self):
        super(ArgumentProvider, self).__init__('arguments/')
        try:
            self._file_name = self._file_list[0]
            self.read_json()
        except IndexError:
            self.create_json()
