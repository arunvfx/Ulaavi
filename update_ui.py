# -*- coding: utf-8 -*-

from PySide2.QtWidgets import QFileDialog, QDialog, QHBoxLayout, QLineEdit, QLabel, QDialogButtonBox, QVBoxLayout, \
    QFrame, QTreeWidgetItem, QApplication
from PySide2.QtGui import QIcon, QColor, QPixmap
from PySide2.QtCore import Qt

import distutils.util
import os
from settings import Settings
from database import Database
from contents import TableContent
from add_templete import Ui_Add_Script
import shutil


class UpdateUI:
    def __init__(self, ui):
        self.ui = ui
        self.set_icons()
        self.settings = Settings()
        self.db = Database()
        self.default_ui()
        self.toggle_search()

    def set_icons(self):
        """
        update icons to UI
        """
        self.ui.btn_settings.setIcon(QIcon(os.path.dirname(__file__) + '/icons/setting.png'))
        self.ui.btn_refresh.setIcon(QIcon(os.path.dirname(__file__) + '/icons/refresh.png'))
        self.ui.btn_home.setIcon(QIcon(os.path.dirname(__file__) + '/icons/home.png'))
        self.ui.btn_favourite.setIcon(QIcon(os.path.dirname(__file__) + '/icons/remove_fav.png'))
        self.ui.btn_grid_view.setIcon(QIcon(os.path.dirname(__file__) + '/icons/grid.png'))
        self.ui.btn_list_view.setIcon(QIcon(os.path.dirname(__file__) + '/icons/list.png'))
        self.ui.btn_info_global.setIcon(QIcon(os.path.dirname(__file__) + '/icons/info.png'))
        self.ui.btn_category_add.setIcon(QIcon(os.path.dirname(__file__) + '/icons/plus_cyan.png'))
        self.ui.btn_add_group.setIcon(QIcon(os.path.dirname(__file__) + '/icons/plus.png'))
        self.ui.btn_category_remove.setIcon(QIcon(os.path.dirname(__file__) + '/icons/minus_cyan.png'))
        self.ui.btn_remove_group.setIcon(QIcon(os.path.dirname(__file__) + '/icons/minus.png'))
        self.ui.btn_screen_capture.setIcon(QIcon(os.path.dirname(__file__) + '/icons/capture.png'))
        self.ui.btn_search.setIcon(QIcon(os.path.dirname(__file__) + '/icons/search.png'))

    def default_ui(self):
        """
        UI default settings
        """
        if UpdateUI.load_settings()['stay_top'] == 'True':
            self.ui.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.ui.lineEdit_search.hide()
        self.ui.combo_file_type_filter.hide()
        self.ui.frame_content_right.hide()
        self.ui.tree_category.setStyleSheet('QTreeWidget:item{height: 24px;}')
        self.load_groups_to_ui()
        self.add_root_to_tree()
        self.add_filter_items()
        self.ui.lineEdit_search.textChanged.connect(
            lambda: self.table.load_by_user_search(self.ui.lineEdit_search.text())
        )
        self.ui.btn_screen_capture.clicked.connect(self.add_template)

    # -------------------------------------------- Basic ui ops -------------------------------------------------------

    def add_filter_items(self):
        """
        load filters to ui
        """
        items = ['All', 'Stock', 'Template', 'Mesh']
        for item in items:
            self.ui.combo_file_type_filter.addItem(item)

    def load_groups_to_ui(self, default_group=None):
        """
        load groups into ui from json
        """
        try:
            self.ui.combo_group.clear()
            for group in self.db.read_from_json():
                self.ui.combo_group.addItem(group)
            if default_group:
                self.ui.combo_group.setCurrentText(default_group)
        except IndexError:
            self.set_status_label('No group to load !')

    def add_root_to_tree(self):
        """
        load 'root' to tree and load categories as childern
        """
        self.ui.tree_category.clear()
        root = QTreeWidgetItem(['root'])
        self.ui.tree_category.addTopLevelItem(root)
        self.load_category_into_ui(root)                # to load categories to ui
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
        toggle info panel
        """
        if self.ui.btn_info_global.isChecked():
            self.ui.frame_content_right.show()
        else:
            self.ui.frame_content_right.hide()

    def enable_content_ui(self, settings):
        """
        show Thumbnail Widget and hide settings Widget
        """
        self.ui.gridLayout.addWidget(self.ui.frame_content, 1, 0, 1, 1)
        settings.hide()
        self.ui.frame_content.show()

    def enable_settings_ui(self, settings):
        """
        show settings panel and hide Thumbnail Widget
        """
        UpdateUI.update_settings_ui(settings)
        self.trigger_settings_ops(settings)
        self.ui.gridLayout.addWidget(settings, 1, 0, 1, 1)
        self.ui.frame_content.hide()
        settings.show()

    def set_status_label(self, data):
        self.ui.label_status_progress.setText(data)

    # --------------------------------------------- LOAD THUMBNAIL ----------------------------------------------------

    def load_thumbnail_widget(self, width=None, height=None):
        """
        create thumbnail widget to parent width/height
        if ffmpeg path mapped ; else: call warning popup to map ffmpeg
        """
        # delete thumbnail widget if already exists
        try:
            self.table.deleteLater()
        except Exception:
            pass

        # if create thumbnail widget and load items once child is selected in  a tree
        if self.ui.tree_category.currentItem():
            if not (self.ui.tree_category.currentItem().text(0) == 'root' or
                    self.ui.tree_category.currentItem().parent().text(0) == 'root'):
                try:
                    self.table = TableContent(width,
                                              height,
                                              self.ui.progress_bar,
                                              self.ui.tree_category.currentItem().text(0),
                                              self.ui.tree_category.currentItem().parent().text(0),
                                              self.ui.combo_group.currentText(),
                                              self.ui.btn_favourite.isChecked(),
                                              self.ui.combo_file_type_filter.currentText().lower().strip(),
                                              self.ui.lineEdit_search.text(),
                                              self.ui.label_status_progress,
                                              self.ui.info_text,
                                              self.ui.btn_info_global.isChecked())
                    self.ui.horizontalLayout_4.addWidget(self.table)
                except Exception:
                    self.ffmpeg_warning()

    def load_thumbnail(self):
        """
        reload item in widget based on filters, fav/delete actions
        """
        try:
            self.table.update_thumbnail_to_ui(self.ui.frame_thumb_loader.width(),
                                              self.ui.frame_thumb_loader.height(),
                                              self.ui.btn_favourite.isChecked(),
                                              self.ui.combo_file_type_filter.currentText())
        except AttributeError:
            self.load_thumbnail_widget(self.ui.frame_thumb_loader.width(), self.ui.frame_thumb_loader.height())
        except Exception:
            pass

    # --------------------------------------------- LOAD METADATA -----------------------------------------------------

    def metadata(self, info=False):
        """
        call function to laod metadata in info widget
        """
        try:
            TableContent.metadata_selected_item(self.table, False, info)
        except AttributeError:
            self.set_status_label('Select an item to access metadata !')
        except Exception:
            pass
    
    # ------------------------------------------- Validate Rename Category -------------------------------------------

    def validate_rename(self):
        """
        check for any item injected into sub-categories. if not, enable rename funtions; else, not
        """
        db = self.db.read_from_json()
        if self.ui.tree_category.currentItem().parent().text(0) == 'root':
            data = db[self.ui.combo_group.currentText()][self.ui.tree_category.currentItem().text(0)]
        if not self.ui.tree_category.currentItem().parent().text(0) == 'root':
            data = db[self.ui.combo_group.currentText()][self.ui.tree_category.currentItem().parent().text(0)][self.ui.tree_category.currentItem().text(0)]
        for k, v in data.items():
            print(v)
            if v: return True
            else: False

    # ------------------------------------------------ SETTINGS ops ---------------------------------------------------

    def trigger_settings_ops(self, settings):
        """
        trigger customize and save settings
        """
        settings.btn_browse_proxy.clicked.connect(lambda: self.set_proxy_to_ui(settings))
        settings.btn_browse_ffmpeg.clicked.connect(lambda: self.set_ffmpeg_to_ui(settings))
        settings.btn_apply_settings.clicked.connect(lambda: self.save_settings(settings))
        settings.btn_reset_settings.clicked.connect(lambda: self.reset_settings(settings))

    def set_ffmpeg_to_ui(self, settings):
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
        return directory path selected by user for proxy
        """
        ff = QFileDialog()
        ff.setStyleSheet(self.ui.styleSheet())
        return ff.getExistingDirectory(self.ui, 'Select Directory', '', options=QFileDialog.DontUseNativeDialog)

    def save_settings(self, settings):
        """
        save changes to settings.json
        """
        self.settings.write_settings(settings.ffmpegLineEdit.text(),
                                     settings.jsonLineEdit.text(),
                                     settings.proxyLineEdit.text(),
                                     settings.lineEdit_threads.text(),
                                     str(settings.always_top_chkbox.isChecked()),
                                     str(settings.cache_image_sequence.isChecked()))
        self.load_thumbnail_widget(self.ui.frame_thumb_loader.width(), self.ui.frame_thumb_loader.height())
        self.set_status_label('Changes saved!')

    def reset_settings(self, settings):
        """
        reset settings to default
        """
        self.settings.write_default_settings()
        UpdateUI.update_settings_ui(settings)
        self.set_status_label('settings reset done!')

    @staticmethod
    def update_settings_ui(settings):
        """
        update settings data to UI from settings.json
        """
        data = UpdateUI.load_settings()
        settings.jsonLineEdit.setText(data['json'])
        settings.proxyLineEdit.setText(data['proxy'])
        settings.lineEdit_threads.setText(str(data['threads']))
        settings.ffmpegLineEdit.setText(str(data['ffmpeg']))
        settings.always_top_chkbox.setChecked(distutils.util.strtobool(data['stay_top']))
        settings.cache_image_sequence.setChecked(distutils.util.strtobool(data['img_seq']))

    # ------------------------------------- MANAGE GROUPS -------------------------------------------------------------

    def add_group(self, parent):
        """
        add new group into ui and ingest into data.json
        """
        for widget in QApplication.allWidgets():
            if widget.objectName() == "Add Group":
                widget.close()
        dialog = QDialog(parent)
        dialog.setObjectName('Add Group')
        dialog.setWindowTitle('Add Group')
        dialog.setFixedSize(300, 120)
        group_name = QLineEdit()
        group_name.setPlaceholderText('Enter group name...')
        group_name.setMinimumHeight(24)
        actions = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        label = QLabel('')
        hb = QHBoxLayout(dialog)
        frame = QFrame()
        hb.addWidget(frame)
        layout = QVBoxLayout(frame)
        layout.addWidget(group_name)
        layout.addWidget(label)
        layout.addWidget(actions)
        dialog.show()
        actions.accepted.connect(lambda: self.ingest_group_to_ui_json(dialog, group_name, label))
        actions.rejected.connect(dialog.close)

    def ingest_group_to_ui_json(self, dialog, text, label):
        """
        if group doesn't exists in data.json > update group in ui/data.json and create directory ;
        else > show warning
        """
        if not text.text() in [group for group in self.db.read_from_json()] and \
                not text.text().strip() == '':
            label.setText('')
            self.ui.combo_group.addItem(text.text().strip())
            self.ui.combo_group.setCurrentText(text.text().strip())
            self.db.ingest_to_json({text.text().strip(): {}})
            dialog.close()
            self.make_directory(text.text())
        else:
            if text.text().strip() == '':
                label.setText("Enter valid Group Name")
            else:
                label.setText(r"Group '<b>%s</b>' already exists!" % text.text())

    def remove_group(self):
        """
        initiate remove current group
        """
        if self.ui.combo_group.currentText():
            self.remove_item_popup(
                'All proxies belongs to the group will be deleted. \nAre your sure, want to delete the group?',
                True
            )

    def remove_item_popup(self, text, is_group=False):
        """
        Popup warning/confirmation:  to remove a group/category
        """
        for panel in QApplication.allWidgets():
            if panel.objectName() == "Remove Group":
                panel.close()
        dialog = QDialog(self.ui)
        dialog.setObjectName('Remove Group')
        dialog.setStyleSheet('QDialog {background-color:  #323232;} '
                             'QLabel{border-radius: 5px; background-color:  #232323;} ')
        dialog.setFixedSize(400, 100)
        dialog.setWindowTitle('Warning')
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: self.pop_item_from_ui_json(dialog, self.ui.combo_group.currentText(), is_group))
        btns.rejected.connect(dialog.close)
        label = QLabel(text)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        layout = QVBoxLayout(dialog)
        layout.addWidget(label)
        layout.addWidget(btns)
        dialog.show()

    def pop_item_from_ui_json(self, dialog, group, is_group):
        """
        Remove group/category from data.json ;
        initiate remove directory from proxy
        """
        removed_signal = ''
        if is_group:
            removed_signal = self.db.remove_category_from_json(group)
            remove_dir_signal = self.remove_directory('%s' % self.ui.combo_group.currentText())
        else:
            if not self.ui.tree_category.currentItem().text(0) == 'root':
                if self.ui.tree_category.currentItem().parent().text(0) == 'root':
                    removed_signal = self.db.remove_category_from_json(
                        group,
                        1,
                        self.ui.tree_category.currentItem().text(0)
                    )
                    remove_dir_signal = self.remove_directory('%s/%s' % (group,
                                                                         self.ui.tree_category.currentItem().text(0)))

                else:
                    try:
                        removed_signal = self.db.remove_category_from_json(
                            group,
                            2,
                            self.ui.tree_category.currentItem().parent().text(0),
                            self.ui.tree_category.currentItem().text(0)
                        )
                        remove_dir_signal = self.remove_directory('%s/%s/%s' % (
                            group,
                            self.ui.tree_category.currentItem().parent().text(0),
                            self.ui.tree_category.currentItem().text(0)))
                    except KeyError:
                        self.add_root_to_tree()
                for item in self.ui.tree_category.selectedItems():
                    item.parent().removeChild(item)
        self.ui.label_status_progress.setText('{}, {}'.format(removed_signal, remove_dir_signal))
        self.load_groups_to_ui(group)
        dialog.close()

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
        if not os.path.isdir(settings_file['proxy'] + '/' + directory):
            os.makedirs(settings_file['proxy'] + '/' + directory)

    @staticmethod
    def rename_directory(src, dest):
        """
        update directory name once renamed group/category
        """
        settings_file = UpdateUI.load_settings()
        os.rename(settings_file['proxy'] + '/' + src, settings_file['proxy'] + '/' + dest)

    @staticmethod
    def remove_directory(directory):
        """
        try to remove directory from proxy
        """
        status = ''
        settings_file = UpdateUI.load_settings()
        if os.path.exists(settings_file['proxy'] + '/' + directory):
            try:
                shutil.rmtree(settings_file['proxy'] + '/' + directory)
                status = 'Removed successfully!'
            except Exception:
                status = "Can't remove cache, manually delete!"
        return status

    # --------------------------------------- CATEGORY ------------------------------------------------------------

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
                            [i.text(0)
                             for i in self.ui.tree_category.findItems("New_Item_", Qt.MatchStartsWith | Qt.MatchRecursive)]
                        ).split('_')[2]) + 1).zfill(2)
            except ValueError:
                max_item = str(1).zfill(2)

            if current_item.text(0) == 'root' or current_item.parent().text(0) == 'root':
                item = QTreeWidgetItem(current_item)
                item.setText(0, 'New_Item_%s' % max_item)
                self.ui.tree_category.addTopLevelItem(item)
                self.ui.tree_category.currentItem().setExpanded(True)
                try:
                    if current_item.text(0) == 'root':
                        item.setBackgroundColor(0, QColor('#323232'))
                except Exception as e: pass

            if current_item.text(0) == 'root':
                self.db.ingest_to_json(item.text(0), 1, self.ui.combo_group.currentText())
                self.make_directory('%s/%s' % (self.ui.combo_group.currentText(), item.text(0)))

            elif current_item.parent().text(0) == 'root':
                self.db.ingest_to_json(item.text(0),
                                       2,
                                       self.ui.combo_group.currentText(),
                                       self.ui.tree_category.currentItem().text(0))
                self.make_directory('%s/%s/%s' % (self.ui.combo_group.currentText(),
                                                  self.ui.tree_category.currentItem().text(0),
                                                  item.text(0)))
        else:
            self.warning_popup('No Valid Group selected!')

    def remove_category(self):
        """
        initiate remove selected category
        """
        try:
            if not self.ui.tree_category.currentItem().text(0) == 'root':
                self.remove_item_popup(
                    'All proxies belongs to this category  will be deleted. '
                            '\nAre your sure, want to delete this Category?', is_group=False)
        except AttributeError:
            self.set_status_label('No Item to delete!')

    def update_category_to_json(self, updated_data, current_data):
        """
        ingest updated category name in data.json;
        update directory name
        """
        if updated_data.parent():
            # update category
            if updated_data.parent().text(0) == 'root':
                if not updated_data.text(0).lower() in \
                       [k.lower() for k, v in self.db.read_from_json()[self.ui.combo_group.currentText()].items()]:
                    self.db.update_category_to_json(updated_data.text(0),
                                                    current_data,
                                                    depth=1,
                                                    group=self.ui.combo_group.currentText())
                    self.rename_directory('%s/%s' % (self.ui.combo_group.currentText(), current_data),
                                          '%s/%s' % (self.ui.combo_group.currentText(), updated_data.text(0))
                                          )
                else:
                    self.ui.tree_category.currentItem().setText(0, current_data)

            # update sub-category
            else:
                if not updated_data.text(0).lower() in \
                       [k.lower() for k, v in self.db.read_from_json()[self.ui.combo_group.currentText()]
                       [self.ui.tree_category.currentItem().parent().text(0)].items()]:

                    self.db.update_category_to_json(
                        updated_data.text(0), current_data,
                        selected_sub=self.ui.tree_category.currentItem().parent().text(0),
                        depth=2,
                        group=self.ui.combo_group.currentText()
                    )
                    self.rename_directory('%s/%s/%s' % (self.ui.combo_group.currentText(),
                                                        self.ui.tree_category.currentItem().parent().text(0),
                                                        current_data),
                                          '%s/%s/%s' % (self.ui.combo_group.currentText(),
                                                        self.ui.tree_category.currentItem().parent().text(0),
                                                        updated_data.text(0))
                                          )
                else:
                    self.ui.tree_category.currentItem().setText(0, current_data)
            self.load_thumbnail_widget(self.ui.frame_thumb_loader.width(), self.ui.frame_thumb_loader.height())

    def load_category_into_ui(self, root):
        """
        load categories in ui from data.json
        """
        db = self.db.read_from_json()
        group = self.ui.combo_group.currentText()
        try:
            for category in db[group]:
                child = QTreeWidgetItem([category])
                root.addChild(child)
                child.setBackgroundColor(0, QColor('#323232'))
                for sub_category in db[group][category]:
                    sub = QTreeWidgetItem([sub_category])
                    child.addChild(sub)
        except KeyError as k:
            print('No Categories found!')

    # ---------------------------------------------- FFMPEG -----------------------------------------------------------

    def ffmpeg_warning(self):
        """
        Popup Warning: invalid FFMPEG path
        """
        self.warning_popup('FFMPEG not found! Enter valid path for FFMPEG.')

    def warning_popup(self, text):
        dialog = QDialog(self.ui)
        dialog.setStyleSheet('QDialog {background-color:  #323232;} '
                             'QLabel{border-radius: 5px; background-color:  #232323;} ')
        dialog.setFixedSize(350, 100)
        dialog.setWindowTitle('Warning')
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dialog.close)
        label = QLabel(text)
        label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        layout = QVBoxLayout(dialog)
        layout.addWidget(label)
        layout.addWidget(btns)
        dialog.show()

    # ------------------------------- ADD NUKE TEMPLETE --------------------------------------------------------------

    def add_template(self):
        """
        open 'Add Template' widget with group/category/Sub-category loaded
        """
        self.template = Ui_Add_Script()
        db = Database().read_from_json()
        self.load_group_template_ui(db)
        self.load_category_template_ui(db)
        self.load_subcategory_template_ui(db)
        pixmap = QPixmap(os.path.dirname(__file__) + '/icons/nuke_1.png')
        pixmap.setDevicePixelRatio(1.75)
        self.template.label_thumb.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.template.label_thumb.setPixmap(pixmap)
        self.template.comboBox_group.currentTextChanged.connect(lambda: self.swap_template('group', db))
        self.template.comboBox_category.currentTextChanged.connect(lambda: self.swap_template('category', db))
        self.template.add_btn.clicked.connect(lambda: self.save_template_script(db))
        self.template.cancel_btn.clicked.connect(self.template.close)
        self.template.show()

    def load_group_template_ui(self, db):
        """
        load groups to ui from data.json
        """
        self.template.comboBox_group.clear()
        for k, v in db.items():
            self.template.comboBox_group.addItem(k)
        self.template.comboBox_group.setCurrentText(self.ui.combo_group.currentText())

    def load_category_template_ui(self, db, count=None):
        """
        load category to ui from data.json
        """
        self.template.comboBox_category.clear()
        for k, v in db.items():
            if k == self.template.comboBox_group.currentText() and not count:
                self.load_category_template_ui(v, 1)
            elif count:
                self.template.comboBox_category.addItem(k)
            else:
                continue

    def load_subcategory_template_ui(self, db, count=None):
        """
        load sub-categories to ui from data.json
        """
        self.template.comboBox_sub_category.clear()
        for k, v in db.items():
            if k == self.template.comboBox_group.currentText() and not count:
                self.load_subcategory_template_ui(v, 1)
            elif k == self.template.comboBox_category.currentText() and count == 1:
                self.load_subcategory_template_ui(v, 2)
            elif count == 2:
                self.template.comboBox_sub_category.addItem(k)
            else:
                continue

    def swap_template(self, current_wid, db):
        """
        change category / group 
        """
        if current_wid == 'group':
            self.load_category_template_ui(db)
            self.load_subcategory_template_ui(db)
        elif current_wid == 'category':
            self.load_subcategory_template_ui(db)

    def save_template_script(self, db):
        """
        Save selected nodes as nk script and update in data.json
        """
        settings = Settings().load_settings()
        if self.template.lineEdit_label.text():
            sel_db_item = (db[self.template.comboBox_group.currentText()][self.template.comboBox_category.currentText()][self.template.comboBox_sub_category.currentText()])
            label_exists = [k for k, v in sel_db_item.items()
                            if os.path.splitext(self.template.lineEdit_label.text())[0].lower() in
                            os.path.splitext(k)[0].lower()]
            if not label_exists:
                self.template.label_info.setText('')
                nk_file = '{}/{}/{}/{}/{}.nk'.format(settings['proxy'],
                                                     self.template.comboBox_group.currentText(),
                                                     self.template.comboBox_category.currentText(),
                                                     self.template.comboBox_sub_category.currentText(),
                                                     self.template.lineEdit_label.text().strip())
                import nuke
                if nuke.selectedNodes():
                    nuke.nodeCopy(nk_file)
                    Database().update_items_into_json(nk_file,
                                                          self.template.comboBox_sub_category.currentText(),
                                                          self.template.comboBox_category.currentText(),
                                                          self.template.comboBox_group.currentText(),
                                                          self.template.lineEdit_label.text().strip() + '.nk')
                    self.load_thumbnail()
                    self.template.close()
            else:
                self.template.label_info.setText(' Template name already exists!,')
        else:
            self.template.label_info.setText('Enter Valid Template Name!')




