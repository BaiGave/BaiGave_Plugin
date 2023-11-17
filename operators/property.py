import bpy
import os
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
        default="C:\\Users\\user\\Desktop\\BaiGave_Plugin\\resourcepacks"
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


classes=[ModInfo,Property]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_properties = bpy.props.PointerProperty(type=Property)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
