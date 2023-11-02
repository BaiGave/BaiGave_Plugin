import bpy
#主面板
class MainPanel(bpy.types.Panel):
    bl_label ="白给的工具"
    bl_idname ="MainPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type = 'UI'
    bl_category ='白给的工具'
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.label(text = "白给的工具",icon='BOLD')
#人模绑定面板        
class RigPanel(bpy.types.Panel):
    bl_label ="人模"
    bl_idname ="RigPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        BaiGave = scene.BaiGave
        row = layout.row()    
        
        row.label(text = "白给的人模",icon='ERROR')
        row = layout.row()
        row.operator("spawn.model")
        row = layout.row()
        row.label(text = "角色类别：",icon='COLLECTION_COLOR_01')
        row = layout.row()
        row = layout.row()
        row.prop(BaiGave,"steve")
        row.prop(BaiGave,"alex")
        row = layout.row()
        row.label(text = "骨骼权重：",icon='BONE_DATA')
        row = layout.row()
        row.prop(BaiGave,"vanllia")
        row.prop(BaiGave,"normal")
        row = layout.row()
        row.label(text = "2d/3d",icon='LIGHT_DATA')
        row = layout.row()
        row.prop(BaiGave,"Layer2d")
        row.prop(BaiGave,"Layer3d")
#方块面板        
class BlockPanel(bpy.types.Panel):
    bl_label ="方块"
    bl_idname ="BlockPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        BaiGave = scene.BaiGave
        
        row = layout.row()    
        row.label(text = "方块",icon='SNAP_VOLUME')
        
        row = layout.row()
        #layout.prop(BaiGave,"JsonImportSpeed")
        row.operator("baigave.import_json", text="导入.json文件")
#世界面板     
class WorldPanel(bpy.types.Panel):
    bl_label ="世界"
    bl_idname ="WorldPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='MainPanel'
    #bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()    
        row.label(text = "世界",icon='ERROR')
        
        row = layout.row()
        row.operator("baigave.import_schem", text="导入.schem文件")

        row = layout.row()
        row.operator("object.add_sway_animation", text="草摇摆")

        row = layout.row()
        row.operator("baigave.map_optimize", text="执行优化")

        # 添加布尔属性的选项
        row = layout.row()
        row.prop(scene, "is_weld", text="合并重叠顶点")
        
        # row = layout.row()
        # row.operator("baigave.spawn_map", text="生成地图")
        # row = layout.row()
        # row.operator("baigave.select", text="选择区域")
        # row = layout.row()
        # row.operator("baigave.import_world", text="导入世界")
        # row = layout.row()
        # row.operator("baigave.create_save", text="创建存档")

# 资源包面板
class ResourcepacksPanel(bpy.types.Panel):
    bl_label = "资源包"
    bl_idname = "ResourcepacksPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BaiGave'
    bl_parent_id = 'MainPanel'
    #bl_options = {'DEFAULT_CLOSED'}

    def __init__(self) -> None:
        bpy.ops.view3d.read_dir()
        super().__init__()

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "view3d_read_dir", text="路径")  # 添加路径字段

        scene = context.scene
        row = layout.row()

        # 使用layout.template_list显示UIList
        my_properties = scene.my_properties 
        layout.template_list("MyFileList", "", my_properties, "my_list", my_properties, "my_list_index")
        # 添加打印选中项目的按钮
        layout.operator("view3d.print_selected_item", text="更改资源包")