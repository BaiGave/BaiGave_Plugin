import bpy
import os
import zipfile
import threading

class ModInfo(bpy.types.PropertyGroup):
    icon: bpy.props.StringProperty(name="图标")
    name: bpy.props.StringProperty(name="名称")
    description: bpy.props.StringProperty(name="描述")

#属性
class Property(bpy.types.PropertyGroup):
    bpy.types.Scene.mods_dir = bpy.props.StringProperty(
        name="模组路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "assets")
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
    folder_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "assets")
    
    # 临时文件夹路径
    temp_dir = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp")

    # 遍历文件夹中的所有文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.jar'):
            # 构造完整的文件路径
            file_path = os.path.join(folder_path, file_name)
            
            # 创建一个与.jar文件同名的新文件夹
            new_folder_path = os.path.join(temp_dir, os.path.splitext(file_name)[0])
            
            # 如果文件夹已存在，则跳过
            if os.path.exists(new_folder_path):
                continue
            
            os.makedirs(new_folder_path, exist_ok=True)
            
            # 解压文件
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    # 只解压 asset 和 data 文件夹以及 .json 和 .png 文件
                    if member.startswith('asset') or member.startswith('data') or member.endswith('.json') or member.endswith('.png'):
                        zip_ref.extract(member, new_folder_path)
classes=[ModInfo,Property]


def register():
    threading.Thread(target=unzip_files).start()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_properties = bpy.props.PointerProperty(type=Property)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
