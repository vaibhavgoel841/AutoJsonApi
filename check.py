import json
import os

from util import validString


class Checks:
    # Default Constructor
    def __init__(self, path):
        self.json_path = path

    # Loading json file
    def load_json(self):
        with open(self.json_path, 'r') as file:
            self.json_data = json.load(file)

    # Checking whether a json file exist to provided path or not
    def check_file_exists(self):
        return os.path.exists(self.json_path)

    # Checking the validity of keys provided in json by user
    def check_keys(self):
        for key in self.json_data.keys():
            if validString(key) == False:
                return False

        return True

    # Checking the validity of data-type of values provided in json by user
    def check_values(self):
        for value in self.json_data.values():
            if isinstance(value, dict) or isinstance(value, list):
                return False

        return True

    #!! DEPRECATED!!
    # def chkPythonVer():
    #     # Checks Python version
    #     getVersion = subprocess.Popen(
    #         "python3 --version",
    #         shell=True,
    #         stdout=subprocess.PIPE).stdout
    #     pyVer = getVersion.read()
    #     pyVerStr = pyVer.decode()[7:-1]
    #     print(pyVerStr)

    # def chkPipVer():
    #     # Checks Pip version
    #     getVersion = subprocess.Popen(
    #         "pip --version",
    #         shell=True,
    #         stdout=subprocess.PIPE).stdout
    #     pyPipVer = getVersion.read()
    #     pyPipVerStr = pyPipVer.decode()
    #     pyPipVerStr.split(" ")[1]
    #     print(pyPipVerStr.split(" ")[1])

    # def checkDjangoVersion():
    #     # Checks Django Version
    #     getVersion = subprocess.Popen(
    #         "django-admin --version",
    #         shell=True,
    #         stdout=subprocess.PIPE).stdout
    #     djVer = getVersion.read()
    #     djVerStr = djVer.decode()
    #     djVerStr = djVerStr[0:-1]
    #     if djVerStr == "4.1.2":
    #         return True
    #     else:
    #         return False
