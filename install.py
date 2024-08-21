import os
import bpy
import sys
import threading
import zipfile
import subprocess
from .codes.functions.tip import ShowMessageBox


def restart_blender_after_delay(blender_exe):
    # 使用 subprocess 启动新的 Blender 实例并恢复上次会话
    si = subprocess.STARTUPINFO()
    si.dwFlags = subprocess.DETACHED_PROCESS
    subprocess.Popen(
        [blender_exe, "-con", "--python-expr", "import bpy; bpy.ops.wm.recover_last_session()"],
        startupinfo=si
    )
    # 关闭当前的 Blender 实例
    bpy.ops.wm.quit_blender()

path = os.path.join(sys.prefix, 'lib', 'site-packages', 'win32')
if not os.path.exists(path):
    ShowMessageBox("请重启blender!", "咕咕正在关闭ing", 'INFO')
    # 指定.zip文件和目标文件夹
    zip_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"BaiGave_Plugin","site-packages.zip")
    target_folder = os.path.join(sys.prefix, 'lib')

    # 使用zipfile模块解压.zip文件
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # 解压.zip文件到目标文件夹，覆盖已存在的文件
        zip_ref.extractall(target_folder)
    

    # 获取 Blender 可执行文件路径
    blender_exe = bpy.app.binary_path
    
    # 创建并启动一个新线程，用于延迟重启 Blender
    restart_thread = threading.Thread(target=restart_blender_after_delay, args=(blender_exe,))
    restart_thread.start()
