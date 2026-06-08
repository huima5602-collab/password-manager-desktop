from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.password_generator import estimate_strength, generate_password
from app.presets import WEBSITE_PRESETS

CUSTOM_PRESET_NAME = "自定义"


class PasswordGenWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_password = ""
        self._setup_ui()
        self._connect_signals()
        self._apply_preset(self.preset_combo.currentText())

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        top_panel = QFrame()
        top_panel.setObjectName("Panel")
        top_layout = QVBoxLayout(top_panel)
        top_layout.setContentsMargins(18, 16, 18, 18)
        top_layout.setSpacing(12)

        preset_header = QLabel("网站预设")
        preset_header.setObjectName("SectionTitle")
        top_layout.addWidget(preset_header)

        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("按网站规则快速配置"))
        self.preset_combo = QComboBox()
        for name in WEBSITE_PRESETS:
            self.preset_combo.addItem(name)
        self.preset_combo.setCurrentText(CUSTOM_PRESET_NAME)
        preset_layout.addWidget(self.preset_combo, 1)
        top_layout.addLayout(preset_layout)

        self.preset_note = QLabel("")
        self.preset_note.setObjectName("MutedText")
        self.preset_note.setWordWrap(True)
        top_layout.addWidget(self.preset_note)
        layout.addWidget(top_panel)

        settings_row = QHBoxLayout()
        settings_row.setSpacing(14)

        left_panel = QFrame()
        left_panel.setObjectName("Panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(18, 16, 18, 18)
        left_layout.setSpacing(14)

        left_title = QLabel("生成规则")
        left_title.setObjectName("SectionTitle")
        left_layout.addWidget(left_title)

        length_group = QGroupBox("密码长度")
        length_layout = QHBoxLayout(length_group)
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setRange(4, 128)
        self.length_slider.setValue(16)
        self.length_input = QLineEdit("16")
        self.length_input.setFixedWidth(56)
        self.length_input.setAlignment(Qt.AlignCenter)
        length_layout.addWidget(self.length_slider, 1)
        length_layout.addWidget(self.length_input)
        length_layout.addWidget(QLabel("位"))
        left_layout.addWidget(length_group)

        char_group = QGroupBox("字符类型")
        char_grid = QGridLayout(char_group)
        char_grid.setHorizontalSpacing(18)
        self.upper_cb = QCheckBox("大写字母 A-Z")
        self.lower_cb = QCheckBox("小写字母 a-z")
        self.digit_cb = QCheckBox("数字 0-9")
        self.special_cb = QCheckBox("特殊字符")
        for checkbox in [self.upper_cb, self.lower_cb, self.digit_cb, self.special_cb]:
            checkbox.setChecked(True)
        char_grid.addWidget(self.upper_cb, 0, 0)
        char_grid.addWidget(self.lower_cb, 0, 1)
        char_grid.addWidget(self.digit_cb, 1, 0)
        char_grid.addWidget(self.special_cb, 1, 1)
        left_layout.addWidget(char_group)

        custom_group = QGroupBox("自定义字符集")
        custom_layout = QVBoxLayout(custom_group)
        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("留空时使用上方字符类型，例如 abcXYZ123!@#")
        custom_layout.addWidget(self.custom_input)

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("模式"))
        self.custom_mode_combo = QComboBox()
        self.custom_mode_combo.addItem("只用自定义字符集生成", "only")
        self.custom_mode_combo.addItem("密码中必须包含自定义字符", "include")
        mode_layout.addWidget(self.custom_mode_combo, 1)
        custom_layout.addLayout(mode_layout)

        self.shuffle_cb = QCheckBox("打乱自定义字符顺序")
        self.shuffle_cb.setChecked(True)
        self.exclude_cb = QCheckBox("排除相似字符 (1/l/I, 0/O)")
        custom_layout.addWidget(self.shuffle_cb)
        custom_layout.addWidget(self.exclude_cb)
        left_layout.addWidget(custom_group)
        settings_row.addWidget(left_panel, 3)

        result_panel = QFrame()
        result_panel.setObjectName("Panel")
        result_layout = QVBoxLayout(result_panel)
        result_layout.setContentsMargins(18, 16, 18, 18)
        result_layout.setSpacing(12)

        result_title = QLabel("生成结果")
        result_title.setObjectName("SectionTitle")
        result_layout.addWidget(result_title)

        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setPlaceholderText("点击“生成密码”创建新密码")
        self.password_display.setMinimumHeight(44)
        result_layout.addWidget(self.password_display)

        self.strength_label = QLabel("强度: -")
        self.strength_label.setObjectName("MutedText")
        result_layout.addWidget(self.strength_label)

        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(True)
        self.strength_bar.setFixedHeight(24)
        result_layout.addWidget(self.strength_bar)

        action_layout = QGridLayout()
        self.generate_btn = QPushButton("生成密码")
        self.generate_btn.setObjectName("PrimaryButton")
        self.copy_btn = QPushButton("复制")
        self.save_to_mgr_btn = QPushButton("保存到管理器")
        self.save_to_mgr_btn.setObjectName("PrimaryButton")
        action_layout.addWidget(self.generate_btn, 0, 0)
        action_layout.addWidget(self.copy_btn, 0, 1)
        action_layout.addWidget(self.save_to_mgr_btn, 1, 0, 1, 2)
        result_layout.addLayout(action_layout)
        result_layout.addStretch()
        settings_row.addWidget(result_panel, 2)

        layout.addLayout(settings_row, 1)

    def _connect_signals(self):
        self.preset_combo.currentTextChanged.connect(self._apply_preset)
        self.length_slider.valueChanged.connect(self._on_slider_changed)
        self.length_input.editingFinished.connect(self._on_input_changed)
        self.upper_cb.toggled.connect(self.generate)
        self.lower_cb.toggled.connect(self.generate)
        self.digit_cb.toggled.connect(self.generate)
        self.special_cb.toggled.connect(self.generate)
        self.custom_input.textChanged.connect(self.generate)
        self.custom_mode_combo.currentIndexChanged.connect(self.generate)
        self.shuffle_cb.toggled.connect(self.generate)
        self.exclude_cb.toggled.connect(self.generate)
        self.generate_btn.clicked.connect(self.generate)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.save_to_mgr_btn.clicked.connect(self._save_to_manager)

    def _apply_preset(self, name):
        preset = WEBSITE_PRESETS.get(name)
        if not preset:
            return

        controls = [
            self.length_slider,
            self.length_input,
            self.upper_cb,
            self.lower_cb,
            self.digit_cb,
            self.special_cb,
            self.custom_input,
            self.exclude_cb,
            self.custom_mode_combo,
            self.shuffle_cb,
        ]
        for control in controls:
            control.blockSignals(True)

        self.length_slider.setValue(preset["length"])
        self.length_input.setText(str(preset["length"]))
        self.upper_cb.setChecked(preset["use_upper"])
        self.lower_cb.setChecked(preset["use_lower"])
        self.digit_cb.setChecked(preset["use_digits"])
        self.special_cb.setChecked(preset["use_special"])
        self.custom_input.setText(preset["custom_chars"])
        self.exclude_cb.setChecked(preset["exclude_similar"])
        index = self.custom_mode_combo.findData(preset["custom_mode"])
        if index >= 0:
            self.custom_mode_combo.setCurrentIndex(index)
        self.shuffle_cb.setChecked(preset["shuffle_custom"])
        self.preset_note.setText(preset.get("note", ""))

        for control in controls:
            control.blockSignals(False)

        self.generate()

    def _on_slider_changed(self, value):
        self.length_input.setText(str(value))
        self.generate()

    def _on_input_changed(self):
        try:
            value = int(self.length_input.text())
        except ValueError:
            value = 16
        value = max(4, min(128, value))
        self.length_input.setText(str(value))
        self.length_slider.setValue(value)
        self.generate()

    def generate(self):
        custom_mode = self.custom_mode_combo.currentData()
        self.current_password = generate_password(
            length=self.length_slider.value(),
            use_upper=self.upper_cb.isChecked(),
            use_lower=self.lower_cb.isChecked(),
            use_digits=self.digit_cb.isChecked(),
            use_special=self.special_cb.isChecked(),
            custom_chars=self.custom_input.text(),
            exclude_similar=self.exclude_cb.isChecked(),
            custom_mode=custom_mode,
            shuffle_custom=self.shuffle_cb.isChecked(),
        )
        self.password_display.setText(self.current_password)
        self._update_strength()
        self._notify("已生成新密码")

    def _update_strength(self):
        if not self.current_password:
            self.strength_bar.setValue(0)
            self.strength_bar.setFormat("")
            self.strength_label.setText("强度: -")
            return
        score, level, color = estimate_strength(self.current_password)
        self.strength_bar.setValue(score)
        self.strength_bar.setFormat(f"{level} ({score}分)")
        self.strength_label.setText(f"强度: {level}，长度 {len(self.current_password)} 位")
        self.strength_bar.setStyleSheet(
            f"QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}"
        )

    def copy_to_clipboard(self):
        if not self.current_password:
            return
        main_win = self.window()
        if hasattr(main_win, "set_sensitive_clipboard"):
            main_win.set_sensitive_clipboard(self.current_password, "密码已复制到剪贴板")
        else:
            QApplication.clipboard().setText(self.current_password)
            self._notify("密码已复制到剪贴板")

    def get_current_password(self):
        return self.current_password

    def _save_to_manager(self):
        if not self.current_password:
            QMessageBox.warning(self, "提示", "请先生成密码")
            return
        main_win = self.window()
        if hasattr(main_win, "save_password_from_generator"):
            preset_name = self.preset_combo.currentText()
            preset = WEBSITE_PRESETS.get(preset_name, {})
            site_name = preset.get("site_name", "") if preset_name != CUSTOM_PRESET_NAME else ""
            url = preset.get("url", "") if preset_name != CUSTOM_PRESET_NAME else ""
            main_win.save_password_from_generator(self.current_password, site_name, url)
        else:
            QMessageBox.warning(self, "提示", "无法跳转到密码管理器")

    def _notify(self, message):
        main_win = self.window()
        if hasattr(main_win, "show_message"):
            main_win.show_message(message)
