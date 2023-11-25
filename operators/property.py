import bpy
import os
import zipfile
import threading
import functools
import re
import shutil
import toml
import json

class ModInfo(bpy.types.PropertyGroup):
    icon: bpy.props.StringProperty(name="图标")
    name: bpy.props.StringProperty(name="名称")
    description: bpy.props.StringProperty(name="描述")

#属性
class Property(bpy.types.PropertyGroup):
    bpy.types.Scene.mods_dir = bpy.props.StringProperty(
        name="模组路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "mods")
    )
    bpy.types.Scene.icons_dir = bpy.props.StringProperty(
        name="图标路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "icons")
    )
    bpy.types.Scene.resourcepacks_dir = bpy.props.StringProperty(
        name="资源包路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "resourcepacks")
    )
    bpy.types.Scene.is_weld = bpy.props.BoolProperty(name="合并重叠顶点", default=True)

    JsonImportSpeed: bpy.props.FloatProperty(name="导入速度(秒每个）",description="Import speed",min=0.01, max=2.0,default=1.0)
    resourcepack_list: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    resourcepack_list_index: bpy.props.IntProperty()

    # 定义 mod_list 属性并附加到 my_properties
    mod_list: bpy.props.CollectionProperty(type=ModInfo)
    mod_list_index: bpy.props.IntProperty()
    
    # 定义一个 EnumProperty 作为下拉列表的选项
    bpy.types.Scene.version_list = bpy.props.EnumProperty(
        name="版本",
        description="选择一个版本",
        items=(),
    )
def unzip_files():
    # 指定的文件夹路径
    folder_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "mods")

    # 临时文件夹路径
    temp_dir = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp")

    # 遍历文件夹中的所有文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.jar'):
            # 构造完整的文件路径
            file_path = os.path.join(folder_path, file_name)

            version = None
            file_name_parts = file_name.replace('.jar', '').split('_')
            for part in file_name_parts:
                if all(char.isdigit() or char == '.' for char in part) and part.count('.') <= 2:
                    version = part
                    break

            # 解压文件
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                mod_id = None 
                for member in zip_ref.namelist():
                    # 判断是否存在fabric.mod.json，若存在则读取其中的modid
                    if member == 'fabric.mod.json':
                        with zip_ref.open(member) as mod_json_file:
                            mod_json_content = mod_json_file.read()
                            mod_data = json.loads(mod_json_content.decode('utf-8'))
                            # 读取 "id" 字段的值
                            mod_id = mod_data.get("id")
                            icon = mod_data.get("icon").replace("/", "\\")
                            name = mod_data.get("name")
                            description = mod_data.get("description")
                        break  # 找到fabric.mod.json后终止循环
                    elif member == 'META-INF/mods.toml':
                        with zip_ref.open('META-INF/mods.toml') as mods_toml_file:
                            mods_toml_content = mods_toml_file.read()
                            mods_toml_data = toml.loads(mods_toml_content.decode('utf-8'))
                            if "mods" in mods_toml_data:
                                for mod_entry in mods_toml_data["mods"]:
                                    mod_id = mod_entry["modId"]
                                    icon = mod_entry.get("logoFile", "").replace("/", "\\")  # 添加默认值，防止没有 "logoFile" 字段时报错
                                    name = mod_entry.get("displayName", "")  # 添加默认值，防止没有 "displayName" 字段时报错
                                    description = mod_entry.get("description", "")  # 添加默认值，防止没有 "description" 字段时报错
                            else:
                                print(f"在 {file_name} 中找不到 'mods' 条目")
                        break
                    elif version and mod_id is not None:
                        mod_id = "minecraft"
                        break

                if mod_id:
                    # 创建新文件夹以modid命名
                    new_folder_path = os.path.join(temp_dir, mod_id)
                    try:
                        if not os.path.exists(new_folder_path):
                            os.makedirs(new_folder_path)
                        elif os.path.exists(new_folder_path):
                            continue
                    except:
                        pass

                    # 将文件解压到新文件夹中
                    for member in zip_ref.namelist():
                        try:
                            # 提取第一层目录下的 assets 和 data 文件夹以及第一层文件夹下的 .json 和 .png 文件
                            if member.startswith('assets/') or member.startswith('data/'):
                                # 构造解压路径
                                extract_path = os.path.join(new_folder_path, member)
                                dir_extract_path = os.path.dirname(extract_path)+"/"
                                # 如果目标文件夹不存在，则创建
                                try:
                                    if not os.path.exists(dir_extract_path):
                                        os.makedirs(dir_extract_path)
                                except:
                                    pass
                                if not os.path.exists(extract_path):
                                    with zip_ref.open(member) as file_in_zip, open(extract_path, 'wb') as output_file:
                                        shutil.copyfileobj(file_in_zip, output_file)

                            elif not '/' in member:  # 第一级目录下的文件
                                if member.endswith('.json') or member.endswith('.png'):
                                    extract_path = os.path.join(new_folder_path, member)
                                    with zip_ref.open(member) as file_in_zip, open(extract_path, 'wb') as output_file:
                                        shutil.copyfileobj(file_in_zip, output_file)
                        except Exception as e:
                            print(f"An error occurred: {e}")
                            pass
        



class UnzipOperator(bpy.types.Operator):
    bl_idname = "baigave.unzip_operator"
    bl_label = "加载模组包"

    def execute(self, context):
        thread = threading.Thread(target=unzip_files)
        thread.start()

        bpy.app.timers.register(functools.partial(self.check_thread, thread), first_interval=1.0)
        return {'RUNNING_MODAL'}

    def check_thread(self, thread):
        # 检查线程是否在运行
        if not thread.is_alive():
            return {'FINISHED'}
        return {'RUNNING_MODAL'}



def read_blockstate_files(directory):
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            blockstate_dir = os.path.join(root, dir, "assets", dir, "blockstates")
            if os.path.exists(blockstate_dir):
                for file in os.listdir(blockstate_dir):
                    if file.endswith(".json"):
                        file_path = os.path.join(blockstate_dir, file)
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if 'variants' in data:
                                variants = data['variants']
                                for variant_key, variant_value in variants.items():
                                    if 'model' in variant_value:
                                        model = variant_value['model']
                                        # Do something with the 'model' value
            else:
                print(f"No 'blockstates' folder found in {dir} folder")
    print("finish")
classes=[ModInfo,Property,UnzipOperator]


def register():
    threading.Thread(target=unzip_files).start()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_properties = bpy.props.PointerProperty(type=Property)
    temp_dir = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp")
    read_blockstate_files(temp_dir)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
