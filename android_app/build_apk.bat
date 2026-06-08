 @echo off
 chcp 65001 >nul
 echo ==========================================
 echo   密码生成与管理器 - APK 编译
 echo ==========================================
 echo.
 echo [1/4] 复制项目到 WSL...
 wsl sh -c "rm -rf /tmp/pwdapp && cp -r /mnt/c/Users/23886/Documents/密码随机生成软件/android_app /tmp/pwdapp"
 echo [2/4] 安装依赖...
 wsl sh -c "apt-get update -qq && apt-get install -y -qq python3-pip openjdk-17-jdk-headless git wget unzip 2>/dev/null"
 wsl sh -c "pip3 install --user buildozer 2>/dev/null"
 echo [3/4] 开始编译 APK（首次需下载约2GB，10-30分钟）...
 wsl sh -c "cd /tmp/pwdapp && export PATH=$HOME/.local/bin:$PATH && buildozer android debug"
 echo [4/4] 完成！APK 在 android_app/bin/ 目录
 pause
