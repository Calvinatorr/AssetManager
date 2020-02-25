# Import Qt libraries
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from Pyside2.QtOpenGL import *
except ImportError:
    try:
        from PySide.QtCore import *
        from PySide.QtGui import *
        from PySide.QtWidgets import *

        assert ("Failed to import PySide2, falling back to PySide")
    except ImportError:
        assert ("Failed to import PySide & PySide2")


def GetMainWindow():
    return None


def FormatDisplayKey(key=""):
    displayKey = ""
    for s in key.split("_"):
        s = s[0].upper() + s[1:]
        displayKey += s + " "

    return displayKey


def GetAssociationIconFromFile(path=""):
    icon = QFileIconProvider().icon(QFileInfo(path))
    return icon



class _GCProtector(object):
    widgets = []


class KeyDataLabel(QWidget):
    """ Key & data """

    def __init__(self, label="", data=None):
        super(KeyDataLabel, self).__init__()

        self.setLayout(QHBoxLayout())
        self.layout().setAlignment(Qt.AlignLeft)

        self.label = QLabel(label)
        self.data = QLabel(str(data))

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.data)


if __name__ == '__main__':
    print(FormatDisplayKey("hello_thereWorld_testing"))