from util import print_colored


class updateFiles:
    def __init__(self, backend, base):

        print_colored('Starting file modification', 'blue')
        self.backend = backend
        self.base = base
        directory = self.backend + "/" + self.backend + "/"
        self.settingsFilePath = directory + "settings.py"
        self.URLsFilePath = directory + "urls.py"
        self.tab = '\t'
        self.nextLine = '\n'

    # Write required INSTALLED_APPS in settings.py file of backend
    def updateSettingsFile(self):

        print_colored(f'Reading {self.settingsFilePath} file', 'blue')
        with open(self.settingsFilePath, 'r+') as file:
            settingsFileData = file.readlines()

        lineNo = None
        foundPosition = False
        for index, line in enumerate(settingsFileData):
            line = line.strip()
            if line == "INSTALLED_APPS = [":
                foundPosition = True
            if line == "]" and foundPosition:
                lineNo = index
                break

        if not foundPosition:
            print_colored(
                f'Error in {self.settingsFilePath}: Unable to find INSTALLED_APPS FIELD',
                'red')
            return

        restApp = "'rest_framework',"
        baseApp = "'" + self.base + ".apps." + self.base.title() + "Config',"

        settingsFileData.insert(lineNo, self.tab + restApp + self.nextLine)
        settingsFileData.insert(lineNo + 1, self.tab + baseApp + self.nextLine)

        print_colored(f'Writing to {self.settingsFilePath} file', 'blue')
        with open(self.settingsFilePath, 'w') as file:
            file.write(''.join(settingsFileData))
        print_colored(
            f'Writing successful in {self.settingsFilePath} file',
            'green')

    # Write required path in urls.py file of backend
    def updateURLsFile(self):

        print_colored(f'Reading {self.URLsFilePath} file', 'blue')
        with open(self.URLsFilePath, 'r+') as file:
            URLsFileData = file.readlines()

        includeLineNo = None
        pathLineNo = None
        foundIncludePosition = False
        foundPathPosition = False

        for index, line in enumerate(URLsFileData):
            line = line.strip()
            if line == "urlpatterns = [":
                foundIncludePosition = True
                includeLineNo = index
                break

        for index, line in enumerate(URLsFileData):
            line = line.strip()
            if line == "]":
                foundPathPosition = True
                pathLineNo = index
                break

        if foundIncludePosition == False or foundPathPosition == False:
            print_colored(
                'Error in {self.URLsFilePath}: Unable to find urlpatterns FIELD',
                'red')
            return

        if includeLineNo == 0:
            includeLineNo = 1

        importInclude = "from django.urls import include"
        includePath = "path('api/',include('" + self.base + ".urls')),"

        URLsFileData.insert(includeLineNo - 1, importInclude + self.nextLine)
        URLsFileData.insert(
            pathLineNo +
            1,
            self.tab +
            includePath +
            self.nextLine)

        print_colored(f'Writing to {self.URLsFilePath} file', 'blue')
        with open(self.URLsFilePath, 'w') as file:
            file.write(''.join(URLsFileData))
        print_colored(
            f'Writing successful in {self.URLsFilePath} file',
            'green')
