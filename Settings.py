""" General settings helpers """

import sys, json


from Common import *


def OpenSettingsFile(mode="r"):
    file = None
    try:
        file = open("settings.json", mode)
    except IOError:
        pass
    return file


def GetSettingsJson():
    data = None
    with OpenSettingsFile() as file:
        data = json.load(file)
    file.close()
    return data


def UpdateSettingsJson(newData):
    data = {}
    with OpenSettingsFile() as file:
        data = json.load(file)

    data.update(newData)
    with OpenSettingsFile("w") as file:
        file.write(json.dumps(data, indent=4))

    file.close()


if __name__ == '__main__':
    settings = GetSettingsJson()
    print("settings", settings)
    #settings["packages"] = [{"Someotherstuff":"hello_world"}]
    print("updated", settings)
    UpdateSettingsJson(settings)