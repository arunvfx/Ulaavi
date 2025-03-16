# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui


# -------------------------------- Custom Modules ------------------------------------


class StatusBar(QtWidgets.QFrame):

    def __init__(self):
        super().__init__()

        self.__hLayout = QtWidgets.QHBoxLayout(self)

        self.label_status = QtWidgets.QLabel()
        self.__hLayout.addWidget(self.label_status)

        self.__hLayout.setContentsMargins(3, 3, 3, 3)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setFixedHeight(30)
        # self.setFixedHeight(60)

    def set_status(self, text: str):
        self.label_status.setText(text)
