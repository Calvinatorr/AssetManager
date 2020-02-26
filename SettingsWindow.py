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
        #self.setMinimumHeight(250)

        # Set up column headers
        self.setHeaderLabels(self._headers)
        # self.header().setStretchLastSection(False)

        # Set column widths
        self.setColumnWidth(0, 126)

        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Never add a horizontal scrolling bar
        self.header().setSortIndicator(0, Qt.AscendingOrder)  # Always sort by ascending order, defaults to reverse
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.OpenContextMenu)

        DCCManager.LoadPathsFromSettings()
        for key, value in DCCManager.packages.items():
            self._AddPath(key, value)


    def GetPackagesData(self):
        packages = []
        for i in range(0, self.topLevelItemCount()):
            item = self.topLevelItem(i)
            DCC = str(item.data(0, 0))
            path = str(item.data(1, 0))
            if len(DCC) > 0:
                packages.append({DCC: path})
        return packages


    def UpdateSettingsJson(self):
        packages = self.GetPackagesData()
        settings = GetSettingsJson()
        settings["packages"] = packages
        UpdateSettingsJson(settings)


    def _AddPath(self, DCC="", path=""):
        item = QTreeWidgetItem(self, [DCC, path])
        item.setIcon(0, GetAssociationIconFromFile(path))
        item.setFlags(item.flags() | Qt.ItemIsEditable)


    def OpenContextMenu(self, position):
        self.cursorPosition = position
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

            # Create context menu
            self.menu = QMenu()

            search = QAction("Search for .exe", self)
            search.setIcon(QIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView)))
            search.triggered.connect(self._SearchForExe)
            self.menu.addAction(search)

            open = QAction("Open from .exe", self)
            open.setIcon(QIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton)))
            open.triggered.connect(self._OpenFromExe)
            self.menu.addAction(open)

            add = QAction("Add", self)
            add.setIcon(QIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder)))
            add.triggered.connect(self._AddRow)
            self.menu.addAction(add)

            remove = QAction("Remove", self)
            remove.setIcon(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)))
            remove.triggered.connect(self._RemoveRow)
            self.menu.addAction(remove)

            self.menu.exec_(self.viewport().mapToGlobal(self.cursorPosition))


    def _SearchForExe(self):
        item = self.itemAt(self.cursorPosition)
        file = QFileDialog.getOpenFileName(self, "Find exe", item.data(1,0) or QDir.currentPath(), "*.exe")[0]
        if file and os.path.isfile(file):
            item.setData(1, 0, str(os.path.normpath(file)))
            item.setIcon(0, GetAssociationIconFromFile(file))


    def _OpenFromExe(self):
        item = self.itemAt(self.cursorPosition)
        file = item.data(1, 0)
        if file and os.path.isfile(file):
            subprocess.Popen(file)


    def _AddRow(self):
        self._AddPath("", "")
        self.UpdateSettingsJson()

    def _RemoveRow(self):
        item = self.itemAt(self.cursorPosition)
        self.takeTopLevelItem(self.indexOfTopLevelItem(item))



class SettingsWindow(QDialog):
    """ Main window class - will generate PySide dialog & OpenGL context """

    def __init__(self, parent=GetMainWindow()):
        super(SettingsWindow, self).__init__(parent)

        # Window styling
        self.setWindowTitle("Settings")
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)  # Hide help
        self.setGeometry(600, 300, 450, 350)
        stdIcon = self.style().standardIcon
        self.setWindowIcon(QIcon(stdIcon(QStyle.SP_ComputerIcon)))
        self.show()  # Show early

        self.setLayout(QVBoxLayout())
        self.pathsToDCC = PathsToDCC()
        self.layout().addWidget(QLabel("Registered DCC paths"))
        self.layout().addWidget(self.pathsToDCC)



        # Buttons in row
        buttons = QWidget()
        buttons.setLayout(QHBoxLayout())
        self.layout().addWidget(buttons)

        # Save button
        self.saveButton = QPushButton()
        self.saveButton.setIcon(QIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton)))
        self.saveButton.setToolTip("Save settings to JSON settings file")
        self.saveButton.clicked.connect(self.UpdateSettingsJson)
        buttons.layout().addWidget(self.saveButton)

        # Reset button
        self.resetButton = QPushButton()
        self.resetButton.setIcon(QIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton)))
        self.resetButton.setToolTip("Reset settings to saved from JSON settings file")
        self.resetButton.clicked.connect(self.ResetSettings) # Reset UI & data in memory
        buttons.layout().addWidget(self.resetButton)


    def UpdateSettingsJson(self):
        self.pathsToDCC.UpdateSettingsJson()


    def ResetSettings(self):
        if QMessageBox.warning(self, "Warning", "Are you sure you want to reset current changes?", QMessageBox.Ok | QMessageBox.Cancel) is QMessageBox.Ok:
            self.ShowUI()


    @staticmethod
    def ShowUI(parent=None):
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