import os, subprocess, json

try:
    import winreg
except ImportError:
    import _winreg as winreg


class DCCManager:
    """ Manager for DCC packages """

    packages = {}

    @staticmethod
    def LoadPathsFromSettings():
        with open("settings.json", "r") as file:
            data = json.load(file)
            for d in data["packages"]:
                DCCManager.packages.update(d)


# Load from JSON file
DCCManager.LoadPathsFromSettings()


if __name__ == '__main__':

    for p in DCCManager.packages.items():
        print(p)

    exit(0)

    paths = os.environ['PATH'].split(';')
    for path in paths:
        print(path)

    exit(0)


    handle = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\excel.exe")
    #value = winreg.QueryValueEx(handle, "InstallPath")[0]
    num_values = winreg.QueryInfoKey(handle)[1]
    for i in range(num_values):
        print(winreg.EnumValue(handle, i))

    subprocess.Popen(winreg.EnumValue(handle, 0)[1])