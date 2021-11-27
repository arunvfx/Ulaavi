# -*- coding: utf-8 -*-

#  Created by Arun Subramaniyam
#  Ebro Elements is a tool to organise assets for VFX.


from PySide2.QtWidgets import QWidget, QApplication
from PySide2.QtCore import Qt, QEvent
from ui_ulaavi import Ui_Ulaavi
from update_ui import UpdateUI
from ui_settings import Ui_Settings
import nukescripts
import nuke


class Ulaavi(Ui_Ulaavi, QWidget):

    def __init__(self):
        super(Ulaavi, self).__init__()
        self.setupUi(self)
        self.settings_ui = Ui_Settings()
        self.update_ui()
        self.current_category = None
        for widget in QApplication.allWidgets():
            if type(widget).__name__ == 'Ulaavi':
                widget.close()

    def update_ui(self):
        self.ui = UpdateUI(self)
        self.btn_settings.clicked.connect(lambda: self.ui.enable_settings_ui(self.settings_ui))
        self.btn_home.clicked.connect(lambda: self.ui.enable_content_ui(self.settings_ui))
        self.btn_search.toggled.connect(lambda: self.ui.toggle_search())
        self.btn_info_global.toggled.connect(lambda: self.ui.toggle_info())
        self.btn_add_group.clicked.connect(lambda: self.ui.add_group(self))
        self.btn_remove_group.clicked.connect(self.ui.remove_group)
        self.btn_category_add.clicked.connect(self.ui.add_category)
        self.btn_category_remove.clicked.connect(self.ui.remove_category)
        self.btn_info_global.toggled.connect(lambda: self.ui.metadata(info=self.btn_info_global.isChecked()))
        self.btn_favourite.toggled.connect(self.ui.load_thumbnail)
        self.btn_refresh.clicked.connect(self.ui.load_thumbnail)
        self.combo_group.currentIndexChanged.connect(self.ui.add_root_to_tree)
        self.tree_category.itemChanged.connect(self.item_changed)
        self.combo_file_type_filter.currentIndexChanged.connect(self.ui.load_thumbnail)
        self.tree_category.currentItemChanged.connect(
            lambda: self.ui.load_thumbnail_widget(self.frame_thumb_loader.width(), self.frame_thumb_loader.height())
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F2:
            item = self.tree_category.currentItem()
            if not item.text(0).lower() == 'root':
                print(self.ui.validate_rename())
                if not self.ui.validate_rename():
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    self.tree_category.editItem(item, 0)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.current_category = str(item.text(0))
                else:
                    self.label_status_progress.setText('Items loaded, cannot rename!')

        if event.key() == Qt.Key_F6:
            self.ui.metadata(popup=True, info=self.btn_info_global.isChecked())

    def item_changed(self):
        try:
            if self.current_category:
                self.ui.update_category_to_json(self.tree_category.currentItem(), self.current_category)
                self.current_category = None
        except Exception:
            pass

    def event(self, event):
        if event.type() == QEvent.Type.Show:
            try:
                set_widget_margins_to_zero(self)
            except:
                pass
        return QWidget.event(self, event)


class widgetPanel(nukescripts.PythonPanel):
    def __init__(self):
        super(widgetPanel, self).__init__(title="Ulaavi", id="uk.co.thefoundry.WidgetPanel")
        self.pyKnob = nuke.PyCustom_Knob("", "", "widgetKnob()")
        self.addKnob(self.pyKnob)


class widgetKnob():
    def makeUI(self):
        self.wid = Ulaavi()
        return self.wid


def set_widget_margins_to_zero(widget_object):
    if widget_object:
        target_widgets = set()
        target_widgets.add(widget_object.parentWidget().parentWidget())
        target_widgets.add(widget_object.parentWidget().parentWidget().parentWidget().parentWidget())

        for widget_layout in target_widgets:

            try:
                widget_layout.layout().setContentsMargins(0, 0, 0, 0)
            except:
                pass


def main():
    main.e = Ulaavi()
    main.e.show()


if __name__ == '__main__':
    app = QApplication([])
    e = Ulaavi()
    e.show()
    app.exec_()

