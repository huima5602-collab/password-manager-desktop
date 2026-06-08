import json
import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app import database as db
from ui.add_edit_dialog import AddEditDialog

PASSWORD_ERROR_VALUES = {"[缺少密钥文件]", "[解密失败]"}


class PasswordManagerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_records = []
        self.selected_record = None
        db.ensure_initialized()
        self._setup_ui()
        self._connect_signals()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        toolbar = QFrame()
        toolbar.setObjectName("Panel")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(14, 12, 14, 12)
        toolbar_layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索网站名或用户名")
        self.search_btn = QPushButton("搜索")
        self.clear_search_btn = QPushButton("清空")
        self.add_btn = QPushButton("新增")
        self.add_btn.setObjectName("PrimaryButton")
        self.edit_btn = QPushButton("编辑")
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setObjectName("DangerButton")
        self.copy_user_btn = QPushButton("复制用户名")
        self.copy_pwd_btn = QPushButton("复制密码")
        self.export_btn = QPushButton("导出")
        self.import_btn = QPushButton("导入")

        toolbar_layout.addWidget(self.search_input, 1)
        toolbar_layout.addWidget(self.search_btn)
        toolbar_layout.addWidget(self.clear_search_btn)
        toolbar_layout.addSpacing(8)
        for button in [
            self.add_btn,
            self.edit_btn,
            self.delete_btn,
            self.copy_user_btn,
            self.copy_pwd_btn,
            self.export_btn,
            self.import_btn,
        ]:
            toolbar_layout.addWidget(button)
        layout.addWidget(toolbar)

        self.empty_state = QLabel("")
        self.empty_state.setObjectName("EmptyState")
        self.empty_state.setAlignment(Qt.AlignCenter)
        self.empty_state.setMinimumHeight(30)
        layout.addWidget(self.empty_state)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        table_panel = QFrame()
        table_panel.setObjectName("Panel")
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(12, 12, 12, 12)
        table_layout.setSpacing(10)

        table_title = QLabel("密码记录")
        table_title.setObjectName("SectionTitle")
        table_layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "网站/应用", "用户名", "网址", "更新时间"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        table_layout.addWidget(self.table, 1)
        splitter.addWidget(table_panel)

        detail_panel = QFrame()
        detail_panel.setObjectName("Panel")
        detail_layout = QVBoxLayout(detail_panel)
        detail_layout.setContentsMargins(16, 16, 16, 16)
        detail_layout.setSpacing(12)

        detail_title = QLabel("记录详情")
        detail_title.setObjectName("SectionTitle")
        detail_layout.addWidget(detail_title)

        self.detail_site = QLabel("未选择记录")
        self.detail_site.setObjectName("PageTitle")
        self.detail_site.setWordWrap(True)
        detail_layout.addWidget(self.detail_site)

        self.detail_grid = QGridLayout()
        self.detail_grid.setHorizontalSpacing(10)
        self.detail_grid.setVerticalSpacing(9)
        self.detail_url = QLabel("-")
        self.detail_username = QLabel("-")
        self.detail_password = QLabel("-")
        self.detail_created = QLabel("-")
        self.detail_updated = QLabel("-")
        for value_label in [
            self.detail_url,
            self.detail_username,
            self.detail_password,
            self.detail_created,
            self.detail_updated,
        ]:
            value_label.setWordWrap(True)
            value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.detail_grid.addWidget(QLabel("网址"), 0, 0)
        self.detail_grid.addWidget(self.detail_url, 0, 1)
        self.detail_grid.addWidget(QLabel("用户名"), 1, 0)
        self.detail_grid.addWidget(self.detail_username, 1, 1)
        self.detail_grid.addWidget(QLabel("密码"), 2, 0)
        self.detail_grid.addWidget(self.detail_password, 2, 1)
        self.detail_grid.addWidget(QLabel("创建时间"), 3, 0)
        self.detail_grid.addWidget(self.detail_created, 3, 1)
        self.detail_grid.addWidget(QLabel("更新时间"), 4, 0)
        self.detail_grid.addWidget(self.detail_updated, 4, 1)
        detail_layout.addLayout(self.detail_grid)

        detail_layout.addWidget(QLabel("备注"))
        self.detail_note = QLabel("-")
        self.detail_note.setObjectName("MutedText")
        self.detail_note.setWordWrap(True)
        self.detail_note.setTextInteractionFlags(Qt.TextSelectableByMouse)
        detail_layout.addWidget(self.detail_note)

        detail_actions = QGridLayout()
        self.detail_copy_user_btn = QPushButton("复制用户名")
        self.detail_copy_pwd_btn = QPushButton("复制密码")
        self.open_url_btn = QPushButton("打开网址")
        detail_actions.addWidget(self.detail_copy_user_btn, 0, 0)
        detail_actions.addWidget(self.detail_copy_pwd_btn, 0, 1)
        detail_actions.addWidget(self.open_url_btn, 1, 0, 1, 2)
        detail_layout.addLayout(detail_actions)
        detail_layout.addStretch()
        splitter.addWidget(detail_panel)
        splitter.setSizes([680, 320])

        layout.addWidget(splitter, 1)

    def _connect_signals(self):
        self.search_btn.clicked.connect(self.refresh)
        self.clear_search_btn.clicked.connect(self._clear_search)
        self.search_input.returnPressed.connect(self.refresh)
        self.add_btn.clicked.connect(self.add_record)
        self.edit_btn.clicked.connect(self.edit_record)
        self.delete_btn.clicked.connect(self.delete_record)
        self.copy_user_btn.clicked.connect(self.copy_username)
        self.copy_pwd_btn.clicked.connect(self.copy_password)
        self.detail_copy_user_btn.clicked.connect(self.copy_username)
        self.detail_copy_pwd_btn.clicked.connect(self.copy_password)
        self.open_url_btn.clicked.connect(self.open_url)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.doubleClicked.connect(self.copy_password)
        self.export_btn.clicked.connect(self.export_data)
        self.import_btn.clicked.connect(self.import_data)

    def _clear_search(self):
        self.search_input.clear()
        self.refresh()

    def refresh(self):
        keyword = self.search_input.text().strip()
        self.current_records = db.get_all_passwords(keyword)
        self.table.setRowCount(len(self.current_records))

        for row_index, record in enumerate(self.current_records):
            self.table.setItem(row_index, 0, QTableWidgetItem(str(record["id"])))
            self.table.setItem(row_index, 1, QTableWidgetItem(record["site_name"]))
            self.table.setItem(row_index, 2, QTableWidgetItem(record["username"]))
            self.table.setItem(row_index, 3, QTableWidgetItem(record["url"]))
            self.table.setItem(
                row_index,
                4,
                QTableWidgetItem(self._short_date(record.get("updated_at", ""))),
            )

        if self.current_records:
            self.table.selectRow(0)
            self.selected_record = self.current_records[0]
            self._update_detail(self.selected_record)
            self.empty_state.clear()
            self.empty_state.setVisible(False)
        else:
            self.selected_record = None
            self.empty_state.setVisible(True)
            if keyword:
                self.empty_state.setText("没有找到匹配的记录")
            else:
                self.empty_state.setText("暂时没有记录，点击“新增”保存第一条密码")
            self._update_detail(None)

        self._update_action_state()
        self._update_parent_status()

    def _on_selection_changed(self):
        self.selected_record = self._get_selected_record(show_alert=False)
        self._update_detail(self.selected_record)
        self._update_action_state()

    def _get_selected_record(self, show_alert=True):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.current_records):
            if show_alert:
                self._notify("请先选择一条记录")
            return None
        return self.current_records[row]

    def _update_detail(self, record):
        if not record:
            self.detail_site.setText("未选择记录")
            self.detail_url.setText("-")
            self.detail_username.setText("-")
            self.detail_password.setText("-")
            self.detail_created.setText("-")
            self.detail_updated.setText("-")
            self.detail_note.setText("-")
            return

        self.detail_site.setText(record["site_name"] or "-")
        self.detail_url.setText(record["url"] or "-")
        self.detail_username.setText(record["username"] or "-")
        password = record.get("plain_password", "")
        if password in PASSWORD_ERROR_VALUES:
            self.detail_password.setText(password)
        elif password:
            self.detail_password.setText("•" * max(8, min(len(password), 24)))
        else:
            self.detail_password.setText("-")
        self.detail_created.setText(record.get("created_at", "") or "-")
        self.detail_updated.setText(record.get("updated_at", "") or "-")
        self.detail_note.setText(record.get("note", "") or "无备注")

    def _update_action_state(self):
        has_selection = self.selected_record is not None
        for button in [
            self.edit_btn,
            self.delete_btn,
            self.copy_user_btn,
            self.copy_pwd_btn,
            self.detail_copy_user_btn,
            self.detail_copy_pwd_btn,
            self.open_url_btn,
        ]:
            button.setEnabled(has_selection)

        self.open_url_btn.setEnabled(
            has_selection and bool(self.selected_record.get("url", "").strip())
        )

    def add_record(self, prefill_password=None, preset_site_name="", preset_url=""):
        dialog = AddEditDialog(
            self,
            record=None,
            preset_site_name=preset_site_name,
            preset_url=preset_url,
        )
        if prefill_password:
            dialog.password_input.setText(prefill_password)
        if dialog.exec_():
            data = dialog.get_data()
            db.add_password(
                site_name=data["site_name"],
                url=data["url"],
                username=data["username"],
                plain_password=data["password"],
                note=data["note"],
            )
            self.refresh()
            self._notify("记录已添加")

    def edit_record(self):
        record = self._get_selected_record()
        if not record:
            return
        dialog = AddEditDialog(self, record=record)
        if dialog.exec_():
            data = dialog.get_data()
            db.update_password(
                record_id=record["id"],
                site_name=data["site_name"],
                url=data["url"],
                username=data["username"],
                plain_password=data["password"],
                note=data["note"],
            )
            self.refresh()
            self._notify("记录已更新")

    def delete_record(self):
        record = self._get_selected_record()
        if not record:
            return
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除“{record['site_name']} - {record['username']}”的密码记录吗？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            db.delete_password(record["id"])
            self.refresh()
            self._notify("记录已删除")

    def copy_username(self):
        record = self._get_selected_record()
        if not record:
            return
        self._copy_sensitive_text(record.get("username", ""), "用户名已复制到剪贴板")

    def copy_password(self):
        record = self._get_selected_record()
        if not record:
            return
        password = record.get("plain_password", "")
        if password in PASSWORD_ERROR_VALUES:
            QMessageBox.warning(self, "提示", f"当前记录无法复制密码：{password}")
            return
        self._copy_sensitive_text(password, "密码已复制到剪贴板")

    def open_url(self):
        record = self._get_selected_record()
        if not record:
            return
        url = record.get("url", "").strip()
        if not url:
            self._notify("当前记录没有网址")
            return
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        self._notify("正在打开网址")

    def export_data(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出数据",
            "password_backup.json",
            "JSON 文件 (*.json)",
        )
        if not file_path:
            return
        records = db.export_all_data()
        with open(file_path, "w", encoding="utf-8") as handle:
            json.dump(records, handle, ensure_ascii=False, indent=2)
        self._notify(f"已导出 {len(records)} 条记录")

    def import_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入数据",
            "",
            "JSON 文件 (*.json)",
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                records = json.load(handle)
            if not isinstance(records, list):
                raise ValueError("导入文件格式错误")
            db.import_records(records)
            self.refresh()
            self._notify(f"已导入 {len(records)} 条记录")
        except Exception as exc:
            QMessageBox.critical(self, "导入失败", f"无法导入文件：\n{exc}")

    def _short_date(self, value):
        if value and len(value) > 16:
            return value[:16].replace("T", " ")
        return value or ""

    def _notify(self, message):
        main_win = self.window()
        if hasattr(main_win, "show_message"):
            main_win.show_message(message)

    def _copy_sensitive_text(self, text, success_message):
        main_win = self.window()
        if hasattr(main_win, "set_sensitive_clipboard"):
            main_win.set_sensitive_clipboard(text, success_message)
        else:
            QApplication.clipboard().setText(text)
            self._notify(success_message)

    def _update_parent_status(self):
        main_win = self.window()
        if hasattr(main_win, "update_status"):
            main_win.update_status()
