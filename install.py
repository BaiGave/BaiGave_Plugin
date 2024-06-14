import os
import sys
import bpy
import zipfile
import importlib

def reload_all_modules():
    # 定义需要保留的核心模块
    core_modules = {'bpy', 'bpy_types', 'mathutils'}

    # 获取当前已加载的模块列表
    registered_modules = list(sys.modules.keys())

    # 卸载非核心模块
    for module_name in registered_modules:
        if module_name not in core_modules and not module_name.startswith("bl_") and not module_name.startswith("_"):
            print(f"卸载模块: {module_name}")
            del sys.modules[module_name]

    # 重新加载核心模块
    for module_name in core_modules:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)

    # 重新加载非核心模块
    for module_name in registered_modules:
        if module_name not in core_modules and module_name not in sys.modules:
            try:
                importlib.import_module(module_name)
                print(f"重新加载模块: {module_name}")
            except ImportError:
                print(f"模块 {module_name} 未找到，无法重新加载。")

path = os.path.join(sys.prefix, 'lib', 'site-packages', 'amulet')
if not os.path.exists(path):
    # 指定.zip文件和目标文件夹
    zip_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "site-packages.zip")
    target_folder = os.path.join(sys.prefix, 'lib')

    # 使用zipfile模块解压.zip文件
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # 解压.zip文件到目标文件夹，覆盖已存在的文件
        zip_ref.extractall(target_folder)
    #reload_all_modules()
