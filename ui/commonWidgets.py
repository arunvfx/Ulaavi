# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets
except ModuleNotFoundError:
    from PySide6 import QtWidgets

# -------------------------------- Custom Modules ------------------------------------


def get_input_widget(title, label, parent=None):
    """
    get user input from popup widget

    :param title: widget title
    :type title: str
    :param label: label
    :type label: str
    :param parent: parent widget
    :type parent: QWidget
    :return: user input string, user accepted or not (ok | cancel)
    :rtype: str, bool
    """
    return QtWidgets.QInputDialog.getText(parent, title, label)


def popup_message(title, content, msgType='message', parent=None):
    """
    popup message

    :param title: title
    :type title: str
    :param content: content
    :type content: str
    :param msgType: message | warning | error
    :type msgType: str
    :param parent: parent widget
    :type parent: QWidget
    :return: confirmation
    :rtype: bool
    """
    msgType = msgType.lower()

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
