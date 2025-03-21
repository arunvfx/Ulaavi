"""
Status Bar Module
================

This module provides a status bar widget for displaying status messages in the application.
It is designed to be simple and reusable, with support for updating the status text.

Key Features:
    - **Status Display**: Displays a status message in a label.
    - **Customizable Height**: Allows setting a fixed height for the status bar.
    - **Minimal Design**: No frame or shadow for a clean look.

Usage:
    - Use the `set_status` method to update the status text.
    - Add the widget to the main layout to display status messages.

"""

# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui


# -------------------------------- Custom Modules ------------------------------------


class StatusBar(QtWidgets.QFrame):
    """
   A status bar widget for displaying status messages.

   This widget provides a simple label for displaying status text and can be added to
   the main layout of an application.

   :param parent: The parent widget, defaults to None.
   :type parent: QWidget, optional
   """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__hLayout = QtWidgets.QHBoxLayout(self)

        self.label_status = QtWidgets.QLabel()
        self.__hLayout.addWidget(self.label_status)

        self.__hLayout.setContentsMargins(3, 3, 3, 3)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setFixedHeight(30)

    def set_status(self, text: str) -> None:
        """
        Set the status text to be displayed in the status bar.

        :param text: The status text to display.
        :type text: str
        """
        self.label_status.setText(text)
