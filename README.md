# Password Manager Desktop

一个离线运行的 PyQt5 桌面密码工具，提供密码生成、密码管理、JSON 导入导出和本地加密存储能力。

## 功能

- 按预设规则生成强密码
- 本地保存网站、用户名、密码和备注
- 使用 Fernet 进行本地加密
- 支持 JSON 导入和导出
- 复制敏感内容后自动清空剪贴板

## 运行

```bash
pip install -r requirements.txt
python main.py
```

## 打包

Windows 下可直接运行：

```bat
build.bat
```

## 目录

- `app/`：核心逻辑
- `ui/`：PyQt5 界面
- `resources/`：图标与样式
- `android_app/`：早期 Android 方向的实验性脚手架
