from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app import database as db
from ui.password_gen_widget import PasswordGenWidget
from ui.password_manager_widget import PasswordManagerWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("密码生成与管理器")
        self.setMinimumSize(1040, 700)

        self._clipboard_value = None
        self._clipboard_clear_timer = QTimer(self)
        self._clipboard_clear_timer.setSingleShot(True)
        self._clipboard_clear_timer.timeout.connect(self._clear_sensitive_clipboard)

        db.ensure_initialized()
        self._setup_ui()
        self._init_data()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        side_bar = QFrame()
        side_bar.setObjectName("SideBar")
        side_bar.setFixedWidth(190)
        side_layout = QVBoxLayout(side_bar)
        side_layout.setContentsMargins(18, 18, 18, 18)
        side_layout.setSpacing(14)

        app_name = QLabel("密码工具箱")
        app_name.setObjectName("AppName")
        app_hint = QLabel("生成、保存和查找密码")
        app_hint.setObjectName("AppHint")
        side_layout.addWidget(app_name)
        side_layout.addWidget(app_hint)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("NavList")
        self.nav_list.setFrameShape(QFrame.NoFrame)
        self.nav_gen = QListWidgetItem("密码生成")
        self.nav_mgr = QListWidgetItem("密码管理")
        self.nav_list.addItem(self.nav_gen)
        self.nav_list.addItem(self.nav_mgr)
        self.nav_list.setCurrentRow(0)
        side_layout.addWidget(self.nav_list, 1)
        main_layout.addWidget(side_bar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 18)
        content_layout.setSpacing(14)

        self.page_title = QLabel("密码生成")
        self.page_title.setObjectName("PageTitle")
        self.page_subtitle = QLabel("按网站规则生成强密码，并可直接保存到管理器。")
        self.page_subtitle.setObjectName("PageSubtitle")
        content_layout.addWidget(self.page_title)
        content_layout.addWidget(self.page_subtitle)

        self.stack = QStackedWidget()
        self.gen_widget = PasswordGenWidget()
        self.mgr_widget = PasswordManagerWidget()
        self.stack.addWidget(self.gen_widget)
        self.stack.addWidget(self.mgr_widget)
        content_layout.addWidget(self.stack, 1)
        main_layout.addWidget(content, 1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("就绪")
        self.status_bar.addPermanentWidget(self.status_label)

        self.nav_list.currentRowChanged.connect(self._switch_page)

    def _init_data(self):
        db.ensure_initialized()
        self.update_status()

    def _switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.page_title.setText("密码生成")
            self.page_subtitle.setText("按网站规则生成强密码，并可直接保存到管理器。")
        else:
            self.page_title.setText("密码管理")
            self.page_subtitle.setText("搜索、查看和维护本机保存的密码记录。")

    def update_status(self):
        count = db.get_record_count()
        self.status_label.setText(f"记录总数: {count}")

    def show_message(self, message, timeout=3500):
        self.statusBar().showMessage(message, timeout)
        QTimer.singleShot(timeout, self.update_status)

    def set_sensitive_clipboard(self, text, success_message, timeout=20000):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self._clipboard_value = text
        self._clipboard_clear_timer.start(timeout)
        self.show_message(success_message)

    def _clear_sensitive_clipboard(self):
        clipboard = QApplication.clipboard()
        if self._clipboard_value is not None and clipboard.text() == self._clipboard_value:
            clipboard.clear()
            self.show_message("剪贴板中的敏感内容已清空", timeout=2500)
        self._clipboard_value = None

    def save_password_from_generator(self, password, preset_site_name="", preset_url=""):
        self.nav_list.setCurrentRow(1)
        self.stack.setCurrentIndex(1)
        self.mgr_widget.add_record(
            prefill_password=password,
            preset_site_name=preset_site_name,
            preset_url=preset_url,
        )
