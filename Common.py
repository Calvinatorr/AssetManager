IMPORT_PYSIDE_MACRO = """
# Import Qt libraries
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except ImportError:
    try:
        from PySide.QtCore import *
        from PySide.QtGui import *
        from PySide.QtWidgets import *
        assert("Failed to import PySide2, falling back to PySide")
    except ImportError:
        assert("Failed to import PySide & PySide2")
"""


def GetMainWindow():
    return None


def FormatDisplayKey(key=""):
    displayKey = ""
    for s in key.split("_"):
        s = s[0].upper() + s[1:]
        displayKey += s + " "

    return displayKey


class _GCProtector(object):
    widgets = []

if __name__ == '__main__':
    print(FormatDisplayKey("hello_thereWorld_testing"))