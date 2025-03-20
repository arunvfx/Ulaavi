"""
This module provides utility functions for creating graphical user interface (GUI) interactions using the PySide2 or
PySide6 libraries. It includes functions for displaying input dialogs and popup messages.
"""
# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets
except ModuleNotFoundError:
    from PySide6 import QtWidgets


# -------------------------------- Custom Modules ------------------------------------


def get_input_widget(title, label, parent=None):
    """
    Displays a text input dialog to get user input.

    This function creates a simple dialog with a title, label, and a text input field.
    The user's input is returned as a tuple containing the entered text and a boolean
    indicating whether the user clicked "OK".

    :param title: The title of the input dialog.
    :type title: str
    :param label: The label displayed above the text input field.
    :type label: str
    :param parent: The parent widget of the dialog. Defaults to None.
    :type parent: QWidget, optional

    :return: A tuple containing:
        - The text entered by the user (str).
        - A boolean indicating whether the user clicked "OK" (True) or "Cancel" (False).
    :rtype: tuple[str, bool]
    """
    return QtWidgets.QInputDialog.getText(parent, title, label, echo=QtWidgets.QLineEdit.Normal)


def popup_message(title, content, msgType='message', parent=None):
    msgType = msgType.lower()
    msgBox = None

    if msgType == 'question':
        msgBox = QtWidgets.QMessageBox.question(parent, title, content)
    elif msgType == 'warning':
        msgBox = QtWidgets.QMessageBox.warning(parent, title, content)
    elif msgType == 'message':
        msgBox = QtWidgets.QMessageBox.information(parent, title, content)
    elif msgType == 'error':
        msgBox = QtWidgets.QMessageBox.critical(parent, title, content)

    if msgBox == QtWidgets.QMessageBox.Yes:
        return True

    return False
