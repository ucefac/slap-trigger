# 修复方案：让单独 modifier key（如 command:right）能被其他软件识别

## 问题分析
1. sudo 运行时会使用 AppleScript 后端（use_applescript=True）
2. AppleScript 的 key code 方式无法让其他软件识别单独的 modifier key（如 command:right）
3. 非 sudo 运行需要 macimu 权限，但当前无法实现

## 解决方案：尝试 Python pynput 库

### 步骤
1. 安装 pynput：`pip install pynput`
2. 修改 keyboard.py，添加 pynput 后端
3. 测试 modifier-only 按键是否能被识别

### 备选方案
- 如果 pynput 无效，考虑用其他方式模拟 modifier 事件
- 可能需要用 PyObjC 直接调用 CGEvents API