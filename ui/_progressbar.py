"""
Thumbnail Progress Bar Module

This module provides a custom progress bar widget, `ThumbnailProgressBar`, designed for use in thumbnail proxy layouts.
The progress bar is styled to be minimalistic and seamlessly integrates into parent layouts. It supports adding and removing
the progress bar dynamically, setting a range, and updating its value.

Dependencies:
    - PySide2 or PySide6 for Qt bindings.

Classes:
    - ThumbnailProgressBar: A custom QProgressBar with fixed height, no text, and custom styling.

Usage:
    - Add the progress bar to a parent widget's layout using `add_progress_bar()`.
    - Update the progress bar's value using `update_value()`.
    - Remove the progress bar using `remove_progress_bar()`.
"""

# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui


# -------------------------------- Custom Modules ------------------------------------


class ThumbnailProgressBar(QtWidgets.QProgressBar):
    """
   A custom progress bar widget designed for displaying progress in thumbnail proxy layouts.

   This progress bar is styled to be minimalistic, with a fixed height, no text, and a
   custom chunk color. It can be added to or removed from a parent widget's layout and
   supports setting a range and updating its value.

   :inherits: QtWidgets.QProgressBar
   """

    def __init__(self):
        """
        Initialize the ThumbnailProgressBar.

        Sets the initial value to 0, fixes the height, hides the text, and applies custom
        styling to the progress bar.
        """
        super().__init__()

        self.setValue(0)
        self.setFixedHeight(3)
        self.setTextVisible(False)
        self.setStyleSheet("QProgressBar::chunk{background-color: #212121;} "
                           "QProgressBar{border: 0; background-color: transparent;}")

        self._set_widget_properties()

    def _set_widget_properties(self) -> None:
        """
        Configure widget properties, such as layout margins and geometry.

        This method sets the content margins of the progress bar to 0 to ensure it fits
        seamlessly into its parent layout.
        """
        self.setContentsMargins(0, 0, 0, 0)

    def add_progress_bar(self, video: QtWidgets.QWidget):
        """
        Add the progress bar to the active thumbnail proxy layout.

        :param video: The parent widget to which the progress bar will be added.
        :type video: QtWidgets.QWidget
        """
        video.vLayout.addWidget(self)

    def remove_progress_bar(self):
        """
        Remove the progress bar from its parent layout and reset its value.

        This method disassociates the progress bar from its parent widget and resets its
        value to 0.
        """
        self.setParent(None)
        self.setValue(0)

    def set_range(self, max_range: int):
        """
        Set the maximum range of the progress bar.

        :param max_range: The maximum value for the progress bar.
        :type max_range: int
        """
        self.setRange(0, max_range)

    def update_value(self, max_range: int):
        """
        Update the progress bar's value.

        If the current value reaches the maximum range, the progress bar is reset to 0.
        Otherwise, the value is incremented by 1.

        :param max_range: The maximum value for the progress bar.
        :type max_range: int
        """
        if self.value() == max_range:
            self.setValue(0)
        self.setValue(self.value() + 1)
