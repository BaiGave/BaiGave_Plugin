import bpy
#属性
class Property(bpy.types.PropertyGroup):
    bpy.types.Scene.view3d_read_dir = bpy.props.StringProperty(
        name="资源包路径",
        default="C:\\Users\\user\\Desktop\\BaiGave_Plugin\\resourcepacks"
    )
    bpy.types.Scene.is_weld = bpy.props.BoolProperty(name="合并重叠顶点", default=True)
    
    JsonImportSpeed: bpy.props.FloatProperty(name="导入速度(秒每个）",description="Import speed",min=0.01, max=2.0,default=1.0)
    my_list: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    my_list_index: bpy.props.IntProperty()
    
    