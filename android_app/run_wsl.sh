 #!/bin/bash
 echo "=== 密码生成与管理器 APK 编译 ==="
 cp -r /mnt/c/Users/23886/Documents/密码随机生成软件/android_app /tmp/pwdapp
 cd /tmp/pwdapp
 rm -rf .buildozer
 pip3 install --user buildozer 2>/dev/null
 export PATH=$PATH:$HOME/.local/bin
 buildozer android debug
 echo "=== 完成 ==="
 ls -la bin/*.apk 2>/dev/null || echo "APK 在 bin/ 目录下"
