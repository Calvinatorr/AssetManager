""" Base Asset class """

#from abc import ABC, ABCMeta, abstractmethod, abstractproperty
import sys, os, datetime

class Asset(object):
    """ Abstract base class for all assets """

    extensions = {}

    def __init__(self, filename=""):
        if type(self) is Asset:
            raise Exception("Abstract class 'Asset'")

        self.data = {}
        self.filename = ""

        self.ImportData(filename)


    def ImportData(self, filename=""):
        """ Import all data from file """

        self.filename = filename
        try:
            file = open(filename, "r+")
            self.data.update({
                "size" : str(round(os.path.getsize(filename)/1024, 2)) + " mb",
                "created" : self._FormatTimeStamp(os.path.getctime(filename)),
                "modified" : self._FormatTimeStamp(os.path.getmtime(filename)),
                "accessed" : self._FormatTimeStamp(os.path.getatime(filename))
            })

            file.close()
        except IOError:
            pass


    def _FormatTimeStamp(self, timestamp):
        d = datetime.datetime.fromtimestamp(timestamp)
        return d


    def GetData(self):
        return self.data


    def GetBaseName(self):
        s = os.path.basename(self.filename)
        s = os.path.splitext(s)[0]
        return s


    def GetFileType(self):
        return os.path.splitext(self.filename)[-1][1:].lower()


class Texture(Asset):
    """ Texture implementation """

    extensions = {"png", "jpeg", "jpg", "exr", "hdr"}

    def __init__(self, filename=""):
        super(Texture, self).__init__(filename)


class Model(Asset):
    """ Model implementation """

    extensions = {"fbx", "obj", "abc"}

    def __init__(self, filename=""):
        super(Model, self).__init__(filename)


class AssetManager:
    """ Manage assets """

    assets = []

    @staticmethod
    def FindAsset(filename=""):
        """ Find asset in list """

        try:
            for a in AssetManager.assets:
                if filename == a.filename:
                    return a
        except:
            pass

        return None


    @staticmethod
    def ImportFromDirectory(directory):
        """ Import assets from directory """

        dir = "E:\Documents\PostUniversity\ProjectLPLateV2\Art\Environment\City\\"
        for filename in os.listdir(dir):
            fullname = os.path.join(dir, filename)
            if os.path.isfile(fullname):
                AssetManager.ImportFromFile(fullname)


    @staticmethod
    def ImportFromFile(filename):
        """ Import asset from file """

        if AssetManager.FindAsset(filename) == None and os.path.isfile(filename):
            # Separate out extension
            ext = os.path.splitext(filename)[-1]
            ext = ext[1:].lower()

            # Wrangle type from extension
            a = None
            if ext in Model.extensions:
                a = Model(filename)
            elif ext in Texture.extensions:
                a = Texture(filename)

            if a != None:
                AssetManager.assets.append(a)


AssetManager.ImportFromDirectory("E:\Documents\PostUniversity\ProjectLPLateV2\Art\Environment\City\\")


if __name__ == '__main__':


    for a in AssetManager.assets:
        print("Asset", a.GetData())