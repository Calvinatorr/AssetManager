""" Texture viewer GUI """

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


class TextureViewer(QScrollArea):
    """ Texture viewer GUI widget """

    def __init__(self, pixmap: QPixmap):
        super(TextureViewer, self).__init__()

        self.show()
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        # Image view
        label = QLabel()
        label.setPixmap(pixmap.scaledToWidth(1024))
        self.layout().addWidget(label)


        self.rgba = QToolButton()
        self.rgba.setPopupMode(QToolButton.MenuButtonPopup)
        self.rgba.setToolTip("RGBA")
        self.rgba.setMenu(QMenu(self.rgba))
        self.rgba.setText("RGBA")
        self.layout().addWidget(self.rgba)
        for c in ["R", "G", "B", "A"]:
            action = QWidgetAction(self.rgba)
            checkbox = QCheckBox()
            checkbox.setText(c)
            checkbox.setChecked(True)
            action.setDefaultWidget(checkbox)
            self.rgba.menu().addAction(action)




"""if __name__ == '__main__':
    global ex
    try:
        ex.close()
    except:
        pass

    app = QApplication(sys.argv)

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


    ex = TextureViewer(pixmap=QPixmap("E:\Documents\PostUniversity\Resources\Lighting\HDRIs\TorontoDowntown_HDRI.jpg"))
    sys.exit(app.exec_())"""