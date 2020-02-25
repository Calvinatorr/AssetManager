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
from DCC import *


class AssetListView(QTreeWidget):
    """ List view for all assets """

    _headers = ["Asset", "Type", "File Type", "$weakref"]

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
            self.setColumnWidth(i, 48)

        # Set up resize policy
        '''
        try: #PySide2 first
            self.header().setSectionResizeMode(0, QHeaderView.Stretch)
            #for i in range(1, self.GetLastColumnIndex()+1):
            #    self.header().setSectionResizeMode(i, QHeaderView.Fixed)
        except: # PySide fallback
            self.header().setResizeMode(0, QHeaderView.Stretch)
            #for i in range(1, self.GetLastColumnIndex()+1):
            #    self.header().setResizeMode(i, QHeaderView.Fixed)
        '''

        #self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Never add a horizontal scrolling bar
        self.header().setSortIndicator(0, Qt.AscendingOrder)    # Always sort by ascending order, defaults to reverse
        self.hideColumn(self.GetLastColumnIndex())              # Hide ref column

        # Add selected nodes
        self.AddAssets(assets) # We also sort the table within this function

        self.setEditTriggers(QTreeWidget.NoEditTriggers)
        #self.setSelectionMode(QTreeWidget.ExtendedSelection)


    def GetSelected(self):
        assets = []
        for item in self.selectedItems():
            id = int(item.data(self.GetLastColumnIndex(), 0))
            a = self._assetWeakRefDict[id]
            assets.append(a)
        return assets


    def AddAsset(self, asset):
        """ Add asset to list view """

        #if not type(asset) is Asset or not issubclass(asset, Asset):
        #    return

        data = [
            asset.GetBaseName(),
            type(asset).__name__,
            asset.GetFileType(),
            str(id(asset))
         ]
        item = QTreeWidgetItem(self, data)
        icon = QIcon()
        self._assetWeakRefDict[id(asset)] = asset
        #item.setIcon(0, icon)


    def AddAssets(self, assets=[]):
        """ Add list of assets to list view (update) """

        if len(assets) <= 0:
            return

        for a in assets:
            self.AddAsset(a)


class AssetDataView(QScrollArea):
    """ Widget for asset data """

    def __init__(self, listView=None):
        super(AssetDataView, self).__init__()

        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

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
        #stdIcon = self.style().standardIcon
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
        self.openSettings.triggered.connect(SettingsWindow.ShowUI)
        menuBar.addAction(self.openSettings)


        toolBar = self.addToolBar("&Tools")
        dccAction = QAction("Open DCC", self)
        dccAction.setShortcut("Ctrl+Shift+D")
        dccAction.setStatusTip("Open DCC package")
        dccAction.triggered.connect(self.OpenDCC)
        toolBar.addAction(dccAction)

        self.selectDCC = QComboBox()
        #self.selectDCC.addItem(QIcon(), "Blender")
        for key, value in DCCManager.packages.items():
            if os.path.isfile(value):
                self.selectDCC.addItem(GetAssociationIconFromFile(value), key)

        toolBar.addWidget(self.selectDCC)



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
        #centralLayout.addWidget(self.assetViewer)

    def OpenDCC(self):
        subprocess.Popen(DCCManager.packages[self.selectDCC.currentText()])



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