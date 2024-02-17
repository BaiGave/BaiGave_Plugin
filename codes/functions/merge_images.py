import bpy
import os
import sys
import zipfile

# 指定.zip文件和目标文件夹
zip_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "site-packages.zip")
target_folder = os.path.join(sys.prefix, 'lib')

# 使用zipfile模块解压.zip文件
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    # 解压.zip文件到目标文件夹，覆盖已存在的文件
    zip_ref.extractall(target_folder)
from PIL import Image

def read_properties_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def merger(filepath):
    # 获取文件夹路径
    directory = os.path.dirname(filepath)

    properties_file_name = ""  # 初始化属性文件名

    # 提取 .properties 文件的名字（不包括扩展名）
    for file in os.listdir(directory):
        if file.endswith(".properties"):
            properties_file_path = os.path.join(directory, file)
            lines = read_properties_file(properties_file_path)
            # 检查是否有 "matchTiles" 项
            for line in lines:
                if line.startswith("matchTiles="):
                    match_tiles_value = line.split("=")[1].strip()
                    properties_file_name = match_tiles_value
                    break  # 找到后退出循环

    # 遍历文件夹下的所有 .png 文件
    image_paths = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".png")]


    # 创建一个新的空白图片，大小为所有图片的总宽度 x 单个图片的高度
    result_image = Image.new('RGB', (len(image_paths) * 16, 16))

    # 将每张图片按照顺序粘贴到新图片上
    for i, image_path in enumerate(image_paths):
        image = Image.open(image_path)
        result_image.paste(image, (i * 16, 0))

    # 保存合并后的图片
    result_image.save(os.path.join(directory, f"{properties_file_name}.png"))

    

class ImageMergerOperator(bpy.types.Operator):
    bl_idname = "baigave.image_merger"
    bl_label = "合并图片"

    # 定义一个属性来存储文件路径
    filepath: bpy.props.StringProperty(subtype="FILE_PATH") # type: ignore

    def execute(self, context):
        # 获取用户选择的文件路径
        filepath = self.filepath
        merger(filepath)
        self.report({'INFO'}, "成功合并图片！")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

classes = [ImageMergerOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)