 # 安卓 APK 编译指南
 
 ## 前置条件
 需要在 Linux 环境（Ubuntu/Debian 推荐）或 WSL 中编译。
 
 ## 编译步骤
 
 1. 安装 Buildozer:
    pip install buildozer
 
 2. 进入 android_app 目录:
    cd android_app
 
 3. 编译 APK:
    buildozer android debug
 
 4. APK 输出在:
    android_app/bin/ 目录下
 
 ## 注意事项
 - 首次编译会下载 Android SDK/NDK（约 2GB），需要较长时间
 - 确保有足够的磁盘空间（至少 10GB）
 - 网络连接稳定
 - cryptography 库会自动编译进 APK
