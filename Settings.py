""" General settings GUI """

import sys

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



from Common import *
from DCC import *


class PathsToDCC(QTreeWidget):
    """ List view for all assets """

    _headers = ["DCC", "Path"]

    def GetLastColumnIndex(self):
        return len(self._headers) - 1

    def __init__(self):
        super(PathsToDCC, self).__init__()

        # Table styling
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setMinimumHeight(250)

        # Set up column headers
        self.setHeaderLabels(self._headers)
        # self.header().setStretchLastSection(False)

        # Set column widths
        self.setColumnWidth(0, 126)

        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Never add a horizontal scrolling bar
        self.header().setSortIndicator(0, Qt.AscendingOrder)  # Always sort by ascending order, defaults to reverse


        self.setEditTriggers(QAbstractItemView.DoubleClicked)

        #for item in {"Maya", "3ds Max", "Blender", "Modo", "Houdini"}:
        for key, value in DCCManager.packages.items():
            item = QTreeWidgetItem(self, [key, value])
            item.setIcon(0, GetAssociationIconFromFile(value))
            item.setFlags(item.flags() | Qt.ItemIsEditable)



class SettingsWindow(QDialog):
    """ Main window class - will generate PySide dialog & OpenGL context """

    def __init__(self, parent=GetMainWindow()):
        super(SettingsWindow, self).__init__(parent)

        # Window styling
        self.setWindowTitle("Settings")
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)  # Hide help
        self.setGeometry(600, 300, 450, 350)
        stdIcon = self.style().standardIcon
        self.show()  # Show early

        self.setLayout(QVBoxLayout())

        self.pathsToDCC = PathsToDCC()
        self.layout().addWidget(self.pathsToDCC)


    @staticmethod
    def ShowUI():
        global ex
        try:
            ex.close()
        except:
            pass
        ex = SettingsWindow()
        return ex


if __name__ == '__main__':
    global ex
    try:
        ex.close()
    except:
        pass

    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside2"))

    app.setStyle(QStyleFactory.create("fusion"))

    darktheme = QPalette()
    darktheme.setColor(QPalette.Window, QColor(45, 45, 45))
    darktheme.setColor(QPalette.WindowText, QColor(222, 222, 222))
    darktheme.setColor(QPalette.Button, QColor(45, 45, 45))
    darktheme.setColor(QPalette.ButtonText, QColor(222, 222, 222))
    darktheme.setColor(QPalette.AlternateBase, QColor(222, 222, 222))
    darktheme.setColor(QPalette.ToolTipBase, QColor(222, 222, 222))
    darktheme.setColor(QPalette.Highlight, QColor(45, 45, 45))
    # Define the pallet color
    # Then set the pallet color

    app.setPalette(darktheme)

    ex = SettingsWindow()
    sys.exit(app.exec_())