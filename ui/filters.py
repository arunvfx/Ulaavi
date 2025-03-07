# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore


# -------------------------------- Custom Modules ------------------------------------


class Filters(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.hLayout = QtWidgets.QHBoxLayout(self)

        self.lbl_tags = QtWidgets.QLabel('  Tags')
        self.cmb_tags = QtWidgets.QComboBox()

        self.lineEdit_search = QtWidgets.QLineEdit()
        self.lineEdit_search.setPlaceholderText('Search here...')

        self.hLayout.addWidget(self.lbl_tags)
        self.hLayout.addWidget(self.cmb_tags)
        self.hLayout.addWidget(self.lineEdit_search)
