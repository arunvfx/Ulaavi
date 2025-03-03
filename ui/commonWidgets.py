from PySide2 import QtWidgets, QtCore


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

    # remove_dialog = QtWidgets.QDialog(parent)
    # remove_dialog.setWindowIcon(QtWidgets.QMessageBox.Warning)
    # remove_dialog.setStyleSheet("QDialog {background-color:  #323232;} "
    #                             "QLabel{border-radius: 5px; background-color:  #232323;} ")
    # remove_dialog.setFixedSize(400, 100)
    # remove_dialog.setWindowTitle(title.capitalize())
    # remove_button = QtWidgets.QDialogButtonBox(
    #     QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
    # remove_button.rejected.connect(remove_dialog.close)
    # remove_warning = QtWidgets.QLabel(content)
    # remove_warning.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
    # popup_layout = QtWidgets.QVBoxLayout(remove_dialog)
    # popup_layout.addWidget(remove_warning)
    # popup_layout.addWidget(remove_button)
    # remove_dialog.show()
