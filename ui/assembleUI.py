import sys
from PySide2 import QtWidgets, QtCore

from ui import categoriesUI, settingsUI, actionsUI, thumbnailUI


class MainUI:
    def setupUi(self, mainWidget):
        if not mainWidget.objectName():
            mainWidget.setObjectName("Ulaavi")

        self.categories = categoriesUI.Categories()
        self.actions = actionsUI.ActionsUI()
        self.thumbnail = thumbnailUI.ThumbnailUI()

        self.__vLayoutMain = QtWidgets.QVBoxLayout(mainWidget)

        self.__splitter = QtWidgets.QSplitter()
        self.__splitter.setObjectName("splitter")
        self.__splitter.setOrientation(QtCore.Qt.Horizontal)

        self.__leftFrame = QtWidgets.QFrame(self.__splitter)
        self.__rightFrame = QtWidgets.QFrame(self.__splitter)

        self.__hLayout = QtWidgets.QHBoxLayout(self.__leftFrame)
        self.__vLayout = QtWidgets.QVBoxLayout(self.__rightFrame)

        self.__vLayout.addWidget(self.actions)
        self.__vLayout.addWidget(self.thumbnail)
        self.__hLayout.addWidget(self.categories)

        self.__leftFrame.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__leftFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.__leftFrame.setFrameShadow(QtWidgets.QFrame.Plain)

        self.__rightFrame.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__rightFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.__rightFrame.setFrameShadow(QtWidgets.QFrame.Plain)

        self.__vLayoutMain.addWidget(self.__splitter)

        self.__vLayoutMain.setContentsMargins(0, 0, 0, 0)
        self.__hLayout.setContentsMargins(0, 0, 0, 0)
        self.__vLayout.setContentsMargins(0, 0, 0, 0)
        self.__splitter.setContentsMargins(0, 0, 0, 0)


class Ulaavi(MainUI, QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    t = Ulaavi()
    t.show()
    app.exec_()
