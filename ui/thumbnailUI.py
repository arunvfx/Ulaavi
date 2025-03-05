from PySide2 import QtWidgets, QtCore, QtGui


class ThumbnailUI(QtWidgets.QTableWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    a = ThumbnailUI()
    a.show()
    app.exec_()