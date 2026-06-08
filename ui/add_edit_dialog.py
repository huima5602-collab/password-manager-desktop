from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from app.password_generator import estimate_strength, generate_password


class AddEditDialog(QDialog):
    def __init__(self, parent=None, record=None, preset_site_name="", preset_url=""):
        super().__init__(parent)
        self.record = record
        self._preset_site_name = preset_site_name
        self._preset_url = preset_url
        self.setWindowTitle("编辑记录" if record else "新增记录")
        self.setMinimumWidth(560)
        self._setup_ui()
        if record:
            self._load_record(record)
        else:
            self._apply_preset()
        self._update_strength()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        form = QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        form.addWidget(QLabel("网站/应用名 *"), 0, 0)
        self.site_name_input = QLineEdit()
        self.site_name_input.setPlaceholderText("例如：GitHub")
        form.addWidget(self.site_name_input, 0, 1)

        form.addWidget(QLabel("网址"), 1, 0)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("例如：https://github.com")
        form.addWidget(self.url_input, 1, 1)

        self.restore_btn = QPushButton("恢复预设网站名和网址")
        self.restore_btn.clicked.connect(self._restore_preset)
        self.restore_btn.setVisible(False)
        form.addWidget(self.restore_btn, 2, 1)

        form.addWidget(QLabel("用户名 / 邮箱"), 3, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("登录用户名或邮箱")
        form.addWidget(self.username_input, 3, 1)
        layout.addLayout(form)

        layout.addWidget(QLabel("密码 *"))
        pwd_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("输入或生成密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.gen_btn = QPushButton("生成")
        self.show_pwd_btn = QPushButton("显示")
        self.show_pwd_btn.setCheckable(True)
        pwd_layout.addWidget(self.password_input, 1)
        pwd_layout.addWidget(self.gen_btn)
        pwd_layout.addWidget(self.show_pwd_btn)
        layout.addLayout(pwd_layout)

        self.strength_label = QLabel("强度: -")
        self.strength_label.setObjectName("MutedText")
        layout.addWidget(self.strength_label)

        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setFixedHeight(22)
        self.strength_bar.setTextVisible(True)
        layout.addWidget(self.strength_bar)

        layout.addWidget(QLabel("备注"))
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("可选备注信息")
        self.note_input.setMaximumHeight(96)
        layout.addWidget(self.note_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.setObjectName("PrimaryButton")
        self.cancel_btn = QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.gen_btn.clicked.connect(self._generate_password)
        self.show_pwd_btn.toggled.connect(self._toggle_password_visibility)
        self.password_input.textChanged.connect(self._update_strength)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _apply_preset(self):
        if self._preset_site_name:
            self.site_name_input.setText(self._preset_site_name)
            self.restore_btn.setVisible(True)
        if self._preset_url:
            self.url_input.setText(self._preset_url)
            self.restore_btn.setVisible(True)

    def _restore_preset(self):
        if self._preset_site_name:
            self.site_name_input.setText(self._preset_site_name)
        if self._preset_url:
            self.url_input.setText(self._preset_url)

    def _toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_pwd_btn.setText("隐藏")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_pwd_btn.setText("显示")

    def _generate_password(self):
        self.password_input.setText(generate_password(length=20))

    def _update_strength(self):
        password = self.password_input.text()
        if not password:
            self.strength_label.setText("强度: -")
            self.strength_bar.setValue(0)
            self.strength_bar.setFormat("")
            return
        score, level, color = estimate_strength(password)
        self.strength_label.setText(f"强度: {level}，长度 {len(password)} 位")
        self.strength_bar.setValue(score)
        self.strength_bar.setFormat(f"{level} ({score}分)")
        self.strength_bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}"
        )

    def _load_record(self, record):
        self.site_name_input.setText(record["site_name"])
        self.url_input.setText(record["url"])
        self.username_input.setText(record["username"])
        self.password_input.setText(record["plain_password"])
        self.note_input.setText(record["note"])

    def get_data(self):
        return {
            "site_name": self.site_name_input.text().strip(),
            "url": self.url_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "note": self.note_input.toPlainText().strip(),
        }

    def accept(self):
        if not self.site_name_input.text().strip():
            QMessageBox.warning(self, "提示", "请输入网站/应用名")
            return
        if not self.password_input.text():
            QMessageBox.warning(self, "提示", "请输入或生成密码")
            return
        super().accept()
