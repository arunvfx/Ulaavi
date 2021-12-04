# -*- coding: utf-8 -*-

import os
import shutil
from distutils import util

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from database.database import Database
from utils.settings import Settings
from utils.container import TableContent
from ui.add_templete import Template

try:
    import nuke
except:
    pass


class UpdateUI:
    def __init__(self, ui):
        self.table = None
        self.ui = ui
        self.settings = Settings()
        self.db = Database()
        self.template = Template()
        self.toggle_search()

    # -------------------------------------------- Basic ui ops ----------------------------------

    def add_filter_items(self):
        """
        load filters to ui
        """
        items = ("All", "Stock", "Template", 'Mesh')
        for item in items:
            self.ui.combo_file_type_filter.addItem(item)

    def load_groups_ui(self, default_group=None):
        """
        load groups into ui from json.
        """
        try:
            self.ui.combo_group.clear()
            for group in self.db.read_from_json():
                self.ui.combo_group.addItem(group)
            if default_group:
                self.ui.combo_group.setCurrentText(default_group)
        except IndexError:
            self.set_status_label("No group to load !")

    def add_root_tree(self):
        """
        load 'root' to tree and load categories as children.
        """
        self.ui.tree_category.clear()
        root = QTreeWidgetItem(["root"])
        self.ui.tree_category.addTopLevelItem(root)
        self.load_category_ui(root)
        self.ui.tree_category.expandItem(root)
        self.ui.tree_category.setCurrentItem(root)

    def toggle_search(self):
        """
        toggle search button to show/hide filter and searchbar.
        """
        if self.ui.btn_search.isChecked():
            self.ui.combo_file_type_filter.show()
            self.ui.lineEdit_search.show()
        else:
            self.ui.combo_file_type_filter.hide()
            self.ui.lineEdit_search.hide()

    def toggle_info(self):
        """
        toggle info panel.
        """
        if self.ui.btn_info_global.isChecked():
            self.ui.frame_content_right.show()
        else:
            self.ui.frame_content_right.hide()

    def enable_content_ui(self, settings):
        """
        show Thumbnail Widget and hide settings Widget.
        """
        self.ui.gridLayout.addWidget(self.ui.frame_content, 1, 0, 1, 1)
        settings.hide()
        self.ui.frame_content.show()

    def enable_settings_ui(self, settings):
        """
        show settings panel and hide Thumbnail Widget.
        """
        UpdateUI.update_settings_ui(settings)
        self.trigger_settings_signals(settings)
        self.ui.gridLayout.addWidget(settings, 1, 0, 1, 1)
        self.ui.frame_content.hide()
        settings.show()

    def set_status_label(self, data):
        self.ui.label_status_progress.setText(data)

    # --------------------------------------------- LOAD THUMBNAIL -------------------------------

    def load_thumbnail_widget(self, width=None, height=None):
        """
        create thumbnail widget to parent width/height
        if ffmpeg path mapped ; else: call warning popup to map ffmpeg
        """
        # delete thumbnail widget if already exists
        for widget in QApplication.allWidgets():
            if type(widget).__name__ == "TableContent":
                widget.deleteLater()

        # if create thumbnail widget and load items once child is selected in  a tree
        if self.ui.tree_category.currentItem():
            if not (self.ui.tree_category.currentItem().text(0) == "root" or
                    self.ui.tree_category.currentItem().parent().text(0) == "root"):
                try:
                    self.table = TableContent(
                        width,
                        height,
                        self.ui.tree_category.currentItem().text(0),
                        self.ui.tree_category.currentItem().parent().text(0),
                        self.ui.combo_group.currentText(),
                        self.ui.btn_favourite.isChecked(),
                        self.ui.combo_file_type_filter.currentText().lower().strip(),
                        self.ui.lineEdit_search.text(),
                        self.ui.label_status_progress,
                        self.ui.info_text,
                        self.ui.btn_info_global.isChecked()
                    )
                    self.ui.horizontalLayout_4.addWidget(self.table)

                except OSError:
                    self.warning_popup("FFMPEG not found! Enter valid path for FFMPEG.")
                except Exception as error:
                    print(error)

    def update_thumbnail_items(self):
        """
        reload item in widget based on filters, fav/delete actions.
        """
        try:
            self.table.update_thumbnail_ui(
                self.ui.frame_thumb_loader.width(),
                self.ui.frame_thumb_loader.height(),
                self.ui.btn_favourite.isChecked(),
                self.ui.combo_file_type_filter.currentText()
            )
        except AttributeError:
            self.load_thumbnail_widget(
                self.ui.frame_thumb_loader.width(),
                self.ui.frame_thumb_loader.height()
            )
        except Exception as error:
            print(error)

    # --------------------------------------------- LOAD METADATA --------------------------------

    def metadata(self, info=False):
        """
        call function to laod metadata in info widget
        """
        try:
            TableContent.metadata_selected_item(self.table, False, info)
        except AttributeError:
            self.set_status_label("Select an item to access metadata !")
        except Exception as e:
            print(e)

    # ------------------------------------------- Validate Rename Category -----------------------

    def validate_category_rename(self):
        """
        check for any item injected into sub-categories. if not, enable rename funtions; else, not
        """
        data = {}
        db = self.db.read_from_json()
        group = self.ui.combo_group.currentText()
        parent = self.ui.tree_category.currentItem().parent().text(0)
        child = self.ui.tree_category.currentItem().text(0)
        if parent == "root":
            data = db[group][child]
        if not parent == "root":
            data = db[group][parent][child]
        for data_key, data_value in data.items():
            if data_value:
                return True

    # ------------------------------------------------ SETTINGS ops ------------------------------

    def trigger_settings_signals(self, settings):
        """
        trigger customize and save settings
        """
        settings.btn_browse_proxy.clicked.connect(lambda: self.set_proxy_to_ui(settings))
        settings.btn_browse_ffmpeg.clicked.connect(
            lambda: self.set_ffmpeg_to_settings_ui(settings)
        )
        settings.btn_apply_settings.clicked.connect(lambda: self.save_settings(settings))
        settings.btn_reset_settings.clicked.connect(lambda: self.reset_settings(settings))

    def set_ffmpeg_to_settings_ui(self, settings):
        """
        select proxy directory by user
        """
        ffmpeg_path = self.browse_proxy_dir()
        if ffmpeg_path:
            settings.ffmpegLineEdit.setText(ffmpeg_path)

    def set_proxy_to_ui(self, settings):
        """
        select proxy directory by user
        """
        proxy_path = self.browse_proxy_dir()
        if proxy_path:
            settings.proxyLineEdit.setText(proxy_path)

    def browse_proxy_dir(self):
        """
        return directory path selected by user for proxy.
        """
        file_browser = QFileDialog()
        file_browser.setStyleSheet(self.ui.styleSheet())
        return file_browser.getExistingDirectory(
            self.ui, "Select Directory", "",
            options=QFileDialog.DontUseNativeDialog
        )

    def save_settings(self, settings):
        """
        save changes to settings.json.
        """
        self.settings.write_settings(
            settings.ffmpegLineEdit.text(),
            settings.jsonLineEdit.text(),
            settings.proxyLineEdit.text(),
            settings.lineEdit_threads.text(),
            settings.always_top_chkbox.isChecked(),
            settings.cache_image_sequence.isChecked()
        )
        self.load_thumbnail_widget(
            self.ui.frame_thumb_loader.width(),
            self.ui.frame_thumb_loader.height()
        )
        self.set_status_label("Changes saved!")

    def reset_settings(self, settings):
        """
        reset settings to default
        """
        self.settings.write_default_settings()
        UpdateUI.update_settings_ui(settings)
        self.set_status_label("settings reset done!")

    @staticmethod
    def update_settings_ui(settings):
        """
        update settings data to UI from settings.json
        """
        data = UpdateUI.load_settings()
        settings.jsonLineEdit.setText(data["json"])
        settings.proxyLineEdit.setText(data["proxy"])
        settings.lineEdit_threads.setText(str(data["threads"]))
        settings.ffmpegLineEdit.setText(str(data["ffmpeg"]))
        settings.always_top_chkbox.setChecked(util.strtobool(data["stay_top"]))
        settings.cache_image_sequence.setChecked(util.strtobool(data["img_seq"]))

    # ------------------------------------- MANAGE GROUPS ----------------------------------------

    def add_group(self, parent):
        """
        add new group into ui and ingest into data.json
        """
        for widget in QApplication.allWidgets():
            if widget.objectName() == 'Add Group':
                widget.close()
        dialog = QDialog(parent)
        dialog.setObjectName("Add Group")
        dialog.setWindowTitle("Add Group")
        dialog.setFixedSize(300, 120)
        group_line_edit = QLineEdit()
        group_line_edit.setPlaceholderText("Enter group name...")
        group_line_edit.setMinimumHeight(24)
        actions = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        label = QLabel('')
        h_layout = QHBoxLayout(dialog)
        frame = QFrame()
        h_layout.addWidget(frame)
        v_layout = QVBoxLayout(frame)
        v_layout.addWidget(group_line_edit)
        v_layout.addWidget(label)
        v_layout.addWidget(actions)
        dialog.show()
        actions.accepted.connect(
            lambda: self.ingest_group_ui_json(dialog, group_line_edit, label)
        )
        actions.rejected.connect(dialog.close)

    def ingest_group_ui_json(self, dialog, group_line_edit, label):
        """
        if group doesn't exists in data.json > update group in ui/data.json and create directory ;
        else > show warning
        """
        group_name = group_line_edit.text()
        if not group_name.lower() in [group.lower() for group in self.db.read_from_json()] and \
                not group_name.strip() == '':
            label.setText('')
            self.ui.combo_group.addItem(group_name.strip())
            self.ui.combo_group.setCurrentText(group_name.strip())
            self.db.ingest_to_json({group_name.strip(): {}})
            dialog.close()
            self.make_directory(group_name)
        else:
            if group_name.strip() == "":
                label.setText("Enter valid Group Name")
            else:
                label.setText(r"Group '<b>{}</b>' already exists!" .format(group_name))

    def remove_group(self):
        """
        initiate remove current group
        """
        if self.ui.combo_group.currentText():
            self.remove_item_popup(
                "All proxies belongs to the group will be deleted. \n"
                "Are your sure, want to delete the group?",
                True
            )

    def remove_item_popup(self, text, is_group=False):
        """
        Popup warning/confirmation:  to remove a group/category
        """
        for widget in QApplication.allWidgets():
            if widget.objectName() == "Remove Popup":
                widget.close()
        remove_dialog = QDialog(self.ui)
        remove_dialog.setObjectName("Remove Popup")
        remove_dialog.setStyleSheet("QDialog {background-color:  #323232;} "
                                    "QLabel{border-radius: 5px; background-color:  #232323;} ")
        remove_dialog.setFixedSize(400, 100)
        remove_dialog.setWindowTitle("Warning")
        remove_button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        remove_button.accepted.connect(
            lambda: self.pop_item_ui_json(
                remove_dialog, self.ui.combo_group.currentText(), is_group
            )
        )
        remove_button.rejected.connect(remove_dialog.close)
        remove_warning = QLabel(text)
        remove_warning.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        popup_layout = QVBoxLayout(remove_dialog)
        popup_layout.addWidget(remove_warning)
        popup_layout.addWidget(remove_button)
        remove_dialog.show()

    def pop_item_ui_json(self, remove_dialog, group, is_group):
        """
        Remove group/category from data.json ;
        initiate remove directory from proxy
        """
        removed_signal = None
        remove_dir_signal = None
        if is_group:
            removed_signal = self.db.remove_category_from_json(group)
            remove_dir_signal = self.remove_directory(
                "{}".format(self.ui.combo_group.currentText())
            )
        else:
            if not self.ui.tree_category.currentItem().text(0) == "root":
                if self.ui.tree_category.currentItem().parent().text(0) == "root":
                    removed_signal = self.db.remove_category_from_json(
                        group,
                        1,
                        self.ui.tree_category.currentItem().text(0)
                    )
                    remove_dir_signal = self.remove_directory(
                        "{}/{}".format(group, self.ui.tree_category.currentItem().text(0))
                    )

                else:
                    try:
                        removed_signal = self.db.remove_category_from_json(
                            group,
                            2,
                            self.ui.tree_category.currentItem().parent().text(0),
                            self.ui.tree_category.currentItem().text(0)
                        )

                        remove_dir_signal = self.remove_directory(
                            "{}/{}/{}".format(
                                group,
                                self.ui.tree_category.currentItem().parent().text(0),
                                self.ui.tree_category.currentItem().text(0)
                            )
                        )
                    except KeyError:
                        self.add_root_tree()
                for item in self.ui.tree_category.selectedItems():
                    item.parent().removeChild(item)
        self.ui.label_status_progress.setText("{}, {}".format(removed_signal, remove_dir_signal))
        self.load_groups_ui(group)
        remove_dialog.close()

    @staticmethod
    def load_settings():
        """
        return data from settings.json
        """
        settings = Settings()
        return settings.load_settings()

    @staticmethod
    def make_directory(directory):
        """
        create directory if not exists
        """
        settings_file = UpdateUI.load_settings()
        if not os.path.isdir("{}/{}".format(settings_file["proxy"], directory)):
            os.makedirs("{}/{}".format(settings_file["proxy"], directory))

    @staticmethod
    def rename_directory(src, dest):
        """
        update directory name once renamed group/category
        """
        settings_file = UpdateUI.load_settings()
        if not os.path.isdir("{}/{}".format(settings_file["proxy"], dest)):
            os.rename(
                "{}/{}".format(settings_file["proxy"], src),
                "{}/{}".format(settings_file["proxy"], dest)
            )

    @staticmethod
    def remove_directory(directory):
        """
        try to remove directory from proxy
        """
        status = None
        settings_file = UpdateUI.load_settings()
        if os.path.exists("{}/{}".format(settings_file["proxy"], directory)):
            try:
                shutil.rmtree("{}/{}".format(settings_file["proxy"], directory))
                status = "Removed successfully!"
            except Exception:
                status = "Can't remove cache, manually delete!"
        return status

    def user_search(self):
        self.table.load_user_search(self.ui.lineEdit_search.text())

    # --------------------------------------- CATEGORY -------------------------------------------

    def add_category(self):
        """
        add category with default name in tree,
        ingest into data.json,
        create directory
        """
        if self.ui.combo_group.currentText():
            item = None
            current_item = self.ui.tree_category.currentItem()
            try:
                max_item = str(
                    int(
                        max(
                            [item.text(0) for item in self.ui.tree_category.findItems(
                                "New_Item_", Qt.MatchStartsWith | Qt.MatchRecursive)]
                        ).split('_')[2]
                    ) + 1
                ).zfill(2)
            except ValueError:
                max_item = str(1).zfill(2)

            if current_item.text(0) == "root" or current_item.parent().text(0) == "root":
                item = QTreeWidgetItem(current_item)
                item.setText(0, "New_Item_{}".format(max_item))
                self.ui.tree_category.addTopLevelItem(item)
                self.ui.tree_category.currentItem().setExpanded(True)
                if current_item.text(0) == "root":
                    item.setBackgroundColor(0, QColor("#323232"))

            if current_item.text(0) == "root":
                self.db.ingest_to_json(item.text(0), 1, self.ui.combo_group.currentText())
                self.make_directory("{}/{}".format(
                    self.ui.combo_group.currentText(), item.text(0))
                )

            elif current_item.parent().text(0) == "root":
                self.db.ingest_to_json(
                    item.text(0),
                    2,
                    self.ui.combo_group.currentText(),
                    self.ui.tree_category.currentItem().text(0))
                self.make_directory("{}/{}/{}".format(
                    self.ui.combo_group.currentText(),
                    self.ui.tree_category.currentItem().text(0),
                    item.text(0)
                ))
        else:
            self.warning_popup("No Valid Group selected!")

    def remove_category(self):
        """
        initiate remove selected category
        """
        try:
            if not self.ui.tree_category.currentItem().text(0) == "root":
                self.remove_item_popup(
                    "All proxies belongs to this category  will be deleted. "
                    "\nAre your sure, want to delete this Category?",
                    is_group=False
                )
        except AttributeError:
            self.set_status_label("No Item to delete!")

    def update_category_json(self, updated_data, current_data):
        """
        ingest updated category name in data.json.
        update directory name.
        """
        group_name = self.ui.combo_group.currentText()
        parent_name = self.ui.tree_category.currentItem().parent().text(0)
        if updated_data.parent():
            if updated_data.parent().text(0) == "root":
                if not updated_data.text(0).lower() in \
                       [data_key.lower()
                        for data_key, data_value in
                        self.db.read_from_json()[group_name].items()]:

                    self.db.update_category_to_json(
                        updated_data.text(0),
                        current_data,
                        depth=1,
                        group=group_name
                    )
                    self.rename_directory(
                        "{}/{}".format(group_name, current_data),
                        "{}/{}".format(group_name, updated_data.text(0))
                    )
                else:
                    self.ui.tree_category.currentItem().setText(0, current_data)

            # update sub-category
            else:
                if not updated_data.text(0).lower() in \
                       [data_key.lower()
                        for data_key, data_val in
                        self.db.read_from_json()[group_name]
                        [parent_name].items()]:

                    self.db.update_category_to_json(
                        updated_data.text(0),
                        current_data,
                        selected_sub=parent_name,
                        depth=2,
                        group=group_name
                    )
                    self.rename_directory(
                        "{}/{}/{}".format(group_name,parent_name, current_data),
                        "{}/{}/{}".format(group_name, parent_name, updated_data.text(0))
                    )
                else:
                    self.ui.tree_category.currentItem().setText(0, current_data)
            self.load_thumbnail_widget(
                self.ui.frame_thumb_loader.width(),
                self.ui.frame_thumb_loader.height()
            )

    def load_category_ui(self, root):
        """
        load categories into ui from data.json
        """
        db = self.db.read_from_json()
        group = self.ui.combo_group.currentText()
        try:
            for category in db[group]:
                child = QTreeWidgetItem([category])
                root.addChild(child)
                child.setBackgroundColor(0, QColor("#323232"))
                for sub_category in db[group][category]:
                    sub = QTreeWidgetItem([sub_category])
                    child.addChild(sub)
        except KeyError:
            print("No Categories found!")

    def warning_popup(self, label_text):
        for widget in QApplication.allWidgets():
            if widget.objectName() == "warning":
                widget.close()
        warning_dialog = QDialog(self.ui)
        warning_dialog.setObjectName("warning")
        warning_dialog.setStyleSheet(
            "QDialog {background-color:  #323232;} "
            "QLabel{border-radius: 5px; background-color:  #232323;} "
        )
        warning_dialog.setFixedSize(350, 100)
        warning_dialog.setWindowTitle('Warning')
        warning_button = QDialogButtonBox(QDialogButtonBox.Ok)
        warning_button.accepted.connect(warning_dialog.close)
        warning_label = QLabel(label_text)
        warning_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        warning_layout = QVBoxLayout(warning_dialog)
        warning_layout.addWidget(warning_label)
        warning_layout.addWidget(warning_button)
        warning_dialog.show()

    # ------------------------------- ADD NUKE TEMPLATE ------------------------------------------

    def add_template(self):
        """
        open 'Add Template' widget with group/category/Sub-category loaded
        """
        self.template.setGeometry(
            self.ui.pos().x() + self.ui.width()/2 - 250,
            self.ui.pos().y() + self.ui.height()/2 - 100,
            500,
            200
        )
        db = Database().read_from_json()
        self.load_group_template_ui(db)
        self.load_category_template_ui(db)
        self.load_subcategory_template_ui(db)
        pixmap = QPixmap("{}/icons/nuke_1.png".format(os.path.dirname(os.path.dirname(__file__))))
        pixmap.setDevicePixelRatio(1.75)
        self.template.label_thumb.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.template.label_thumb.setPixmap(pixmap)
        self.template.comboBox_group.currentTextChanged.connect(
            lambda: self.swap_template("group", db)
        )
        self.template.comboBox_category.currentTextChanged.connect(
            lambda: self.swap_template("category", db)
        )
        self.template.add_btn.clicked.connect(lambda: self.save_template_script(db))
        self.template.cancel_btn.clicked.connect(self.template.close)
        self.template.show()
        self.template.activateWindow()
        self.template.raise_()

    def load_group_template_ui(self, db):
        """
        load groups to ui from data.json
        """
        self.template.comboBox_group.clear()
        for db_key, db_value in db.items():
            self.template.comboBox_group.addItem(db_key)
        self.template.comboBox_group.setCurrentText(self.ui.combo_group.currentText())

    def load_category_template_ui(self, db, count=None):
        """
        load category to ui from data.json
        """
        self.template.comboBox_category.clear()
        for db_key, db_value in db.items():
            if db_key == self.template.comboBox_group.currentText() and not count:
                self.load_category_template_ui(db_value, 1)
            elif count:
                self.template.comboBox_category.addItem(db_key)
        try:
            if self.ui.tree_category.currentItem().text(0) == "root":
                self.template.comboBox_category.setCurrentText(
                    self.ui.tree_category.currentItem().child(0).text(0)
                )
            elif self.ui.tree_category.currentItem().parent().text(0) == "root":
                self.template.comboBox_category.setCurrentText(
                    self.ui.tree_category.currentItem().text(0)
                )
        except AttributeError as error:
            print(error)

    def load_subcategory_template_ui(self, db, count=None):
        """
        load sub-categories to ui from data.json
        """
        self.template.comboBox_sub_category.clear()
        for db_key, db_value in db.items():
            if db_key == self.template.comboBox_group.currentText() and not count:
                self.load_subcategory_template_ui(db_value, 1)
            elif db_key == self.template.comboBox_category.currentText() and count == 1:
                self.load_subcategory_template_ui(db_value, 2)
            elif count == 2:
                self.template.comboBox_sub_category.addItem(db_key)

        try:
            if self.ui.tree_category.currentItem().text(0) == "root":
                self.template.comboBox_category.setCurrentText(
                    self.ui.tree_category.currentItem().child(0).text(0)
                )
                self.template.comboBox_sub_category.setCurrentText(
                    self.ui.tree_category.currentItem().child(0).child(0).text(0)
                )

            elif self.ui.tree_category.currentItem().parent().text(0) == "root":
                self.template.comboBox_category.setCurrentText(
                    self.ui.tree_category.currentItem().text(0)
                )
                self.template.comboBox_sub_category.setCurrentText(
                    self.ui.tree_category.currentItem().child(0).text(0)
                )

            elif self.ui.tree_category.currentItem().parent().parent().text(0) == "root":
                self.template.comboBox_category.setCurrentText(
                    self.ui.tree_category.currentItem().parent().text(0)
                )
                self.template.comboBox_sub_category.setCurrentText(
                    self.ui.tree_category.currentItem().text(0)
                )
        except AttributeError as error:
            print(error)

    def swap_template(self, current_widget, db):
        """
        change category / group 
        """
        if current_widget == "group":
            self.load_category_template_ui(db)
            self.load_subcategory_template_ui(db)
        elif current_widget == "category":
            self.load_subcategory_template_ui(db)

    def save_template_script(self, db):
        """
        Save selected nodes as nk script and update in data.json
        """
        settings = self.settings.load_settings()
        group = self.template.comboBox_group.currentText()
        parent = self.template.comboBox_category.currentText()
        child = self.template.comboBox_sub_category.currentText()
        if self.template.lineEdit_label.text():
            sel_db_item = db[group][parent][child]
            label_exists = [
                db_key for db_key, db_value in sel_db_item.items()
                if os.path.splitext(self.template.lineEdit_label.text())[0].lower() in
                os.path.splitext(db_key)[0].lower()
            ]
            if not label_exists:
                self.template.label_info.setText('')
                nk_file = "{}/{}/{}/{}/{}.nk".format(
                    settings["proxy"],
                    group,
                    parent,
                    child,
                    self.template.lineEdit_label.text().strip()
                )
                if nuke.selectedNodes():
                    nuke.nodeCopy(nk_file)
                    Database().update_items_into_json(
                        nk_file,
                        child,
                        parent,
                        group,
                        "{}.nk".format(self.template.lineEdit_label.text().strip())
                    )
                    self.update_thumbnail_items()
                    self.template.close()
            else:
                self.template.label_info.setText("Template name already exists!")
        else:
            self.template.label_info.setText("Enter Valid Template Name!")
