""" Main assset manager window """

import sys, weakref, subprocess
import qdarkstyle


try:
    from Common import *
except ImportError:
    assert ("Failed to import Common.py")

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


import json

from Asset import *
from AssetViewer import *
from Settings import *
from SettingsWindow import *
from DCC import *


class AssetListView(QTreeWidget):
    """ List view for all assets """

    _headers = ["Asset", "Type", "File Type", "Size", "Created", "Modified", "$weakref"]

    def GetLastColumnIndex(self):
        return len(self._headers)-1


    def __init__(self, assets=[]):
        super(AssetListView, self).__init__()

        self._assetWeakRefDict = weakref.WeakValueDictionary()
        
        # Table styling
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setMinimumHeight(250)

        # Set up column headers
        self.setHeaderLabels(self._headers)
        #self.header().setStretchLastSection(False)

        # Set column widths
        self.setColumnWidth(0, 256)
        for i in range(1, self.GetLastColumnIndex()):
            self.setColumnWidth(i, 64)

        #self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Never add a horizontal scrolling bar
        self.header().setSortIndicator(0, Qt.AscendingOrder)    # Always sort by ascending order, defaults to reverse
        self.hideColumn(self.GetLastColumnIndex())              # Hide ref column

        # Add selected nodes
        self.AddAssets(assets) # We also sort the table within this function

        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        #self.setSelectionMode(QTreeWidget.ExtendedSelection)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.OpenContextMenu)


    def OpenContextMenu(self, position):
        self.cursorPosition = position
        item = self.itemAt(self.cursorPosition)
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

            # Create context menu
            self.menu = QMenu()

            open = QAction("Open file", self)
            open.setIcon(GetAssociationIconFromFile(self.GetAssetFromItem(item).filename))
            open.triggered.connect(self._OpenFile)
            self.menu.addAction(open)

            openInExplorer = QAction("Open in explorer", self)
            openInExplorer.setIcon(QIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton)))
            openInExplorer.triggered.connect(self._OpenInExplorer)
            self.menu.addAction(openInExplorer)

            self.menu.exec_(self.viewport().mapToGlobal(self.cursorPosition))


    def _OpenFile(self):
        item = self.itemAt(self.cursorPosition)
        asset = self.GetAssetFromItem(item)
        os.system(asset.filename)

    def mouseDoubleClickEvent(self, event:QMouseEvent):
        self.cursorPosition = event.pos()
        self._OpenFile()

    def _OpenInExplorer(self):
        item = self.itemAt(self.cursorPosition)
        asset = self.GetAssetFromItem(item)
        subprocess.Popen(r'explorer /select,"{}"'.format(os.path.normpath(asset.filename)))


    def GetAssetFromItem(self, item):
        id = int(item.data(self.GetLastColumnIndex(), 0))
        return self._assetWeakRefDict[id]


    def GetSelected(self):
        assets = []
        for item in self.selectedItems():
            assets.append(self.GetAssetFromItem(item))
        return assets


    def AddAsset(self, asset):
        """ Add asset to list view """

        #if not type(asset) is Asset or not issubclass(asset, Asset):
        #    return

        data = asset.GetSimpleData()
        item = QTreeWidgetItem(self, data)
        icon = QIcon()
        self._assetWeakRefDict[id(asset)] = asset
        item.setIcon(0, GetAssociationIconFromFile(asset.filename))


    def AddAssets(self, assets=[], clear=False):
        """ Add list of assets to list view (update) """

        if clear:
            self.ClearAssets()

        if len(assets) <= 0:
            return

        for a in assets:
            self.AddAsset(a)


    def ClearAssets(self):
        self.clear()
        self._assetWeakRefDict.clear()


class AssetDataView(QScrollArea):
    """ Widget for asset data """

    def __init__(self, listView=None):
        super(AssetDataView, self).__init__()

        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)

        self.listView = listView
        self.dataWidget = QWidget()
        self.dataWidget.setLayout(QVBoxLayout())
        self.dataWidget.layout().setAlignment(Qt.AlignTop)
        self.layout().addWidget(self.dataWidget)

        self.ReflectSelectedData()
        self.listView.selectionModel().selectionChanged.connect(self.ReflectSelectedData)


    def _ClearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                _ClearLayout(item.layout())


    def ReflectSelectedData(self):
        self._ClearLayout(self.dataWidget.layout())

        selection = self.listView.GetSelected()
        if len(selection) > 0:
            asset = selection[0]

            data = asset.GetData()
            for key in data:
                displayKey = FormatDisplayKey(key)
                d = data[key]
                self.dataWidget.layout().addWidget(KeyDataLabel( displayKey + ": ", d))

            if type(asset) is Texture:
                label = QLabel()
                pixmap = QPixmap(asset.filename)
                label.setPixmap(pixmap)
                self.dataWidget.layout().addWidget(label)



class MainWindow(QMainWindow):
    """ Main window class - will generate PySide dialog & OpenGL context """


    def __init__(self, parent=GetMainWindow()):
        super(MainWindow, self).__init__(parent)

        # Window styling
        self.setWindowTitle("Asset Manager")
        #self.setFlags(self.flags() ^ Qt.WindowContextHelpButtonHint)  # Hide help
        self.resize(1280, 720)
        #self.setGeometry(600, 300, 450, 350)
        stdIcon = self.style().standardIcon
        self.show()  # Show early


        splitter = QSplitter(parent)
        splitter.setCollapsible(0, True)
        self.setCentralWidget(splitter)
        centralLayout = QVBoxLayout()
        self.centralWidget().setLayout(centralLayout)


        #self.addToolBar("File")
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        self.openSettings = QAction("&Settings", self)
        self.openSettings.triggered.connect(self._ShowSettings)
        menuBar.addAction(self.openSettings)


        toolBar = self.addToolBar("&Tools")

        # Select DCC action
        self.selectDCC = QComboBox()
        toolBar.addWidget(self.selectDCC)
        for key, value in DCCManager.packages.items():
            if os.path.isfile(value):
                item = self.selectDCC.addItem(GetAssociationIconFromFile(value), key)
        dccAction = QAction("Open DCC", self)
        dccAction.setShortcut("Ctrl+Shift+D")
        dccAction.setStatusTip("Open DCC package")
        dccAction.triggered.connect(self.OpenDCC)
        toolBar.addAction(dccAction)

        """self.selectDCC = QToolButton()
        self.selectDCC.setPopupMode(QToolButton.MenuButtonPopup)
        self.selectDCC.setToolTip("Open DCC")
        self.selectDCC.setMenu(QMenu(self.selectDCC))
        for key, value in DCCManager.packages.items():
            if os.path.isfile(value):
                action = QWidgetAction(self.selectDCC)
                button = QToolButton()
                button.setIcon(GetAssociationIconFromFile(value))
                button.setToolTip(key)
                button.setText(key)
                button.clicked.connect(self.OpenDCC)
                action.setDefaultWidget(button)
                self.selectDCC.menu().addAction(action)"""

        # Open directory action
        openDirectory = QToolButton(parent=self)
        openDirectory.setIcon(QIcon(stdIcon(QStyle.SP_DialogOpenButton)))
        self.currentDirectory = ""
        openDirectory.clicked.connect(self._SearchForDirectory)
        toolBar.addWidget(openDirectory)

        clear = QToolButton(parent=self)
        clear.setIcon(QIcon(stdIcon(QStyle.SP_DirClosedIcon)))
        clear.clicked.connect(self._CloseDirectory)
        toolBar.addWidget(clear)


        self.assetListView = AssetListView(AssetManager.assets)
        self.assetDataView = AssetDataView(self.assetListView)
        self.assetViewer = AssetViewer()

        centralLayout.addWidget(self.assetListView)

        splitter = QSplitter(parent)
        splitter.setOrientation(Qt.Vertical)
        splitter.setCollapsible(0, True)
        splitter.addWidget(self.assetDataView)
        splitter.addWidget(self.assetViewer)
        centralLayout.addWidget(splitter)


    def OpenDCC(self):
        subprocess.Popen(DCCManager.packages[self.selectDCC.currentText()])


    def _SearchForDirectory(self):
        dir = ""
        try:
            dir = QFileDialog.getExistingDirectory(self, "Open directory", self.currentDirectory or QDir.currentPath())
        except:
            pass
        if dir and os.path.isdir(dir):
            self.currentDirectory = dir
            self._OpenDirectory()


    def _OpenDirectory(self):
        if self.currentDirectory and os.path.isdir(self.currentDirectory):
            AssetManager.ImportFromDirectory(self.currentDirectory, clear=True)
            self.assetListView.AddAssets(AssetManager.assets, clear=True)

    def _CloseDirectory(self):
        self.assetListView.ClearAssets()


    def _ShowSettings(self):
        SettingsWindow.ShowUI(self)



def ShowUI():
    global ex
    try:
        ex.close()
    except:
        pass

    app = QApplication(sys.argv)
    #app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside2"))

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


    ex = MainWindow()
    sys.exit(app.exec_())

    return ex


if __name__ == '__main__':
    ShowUI()