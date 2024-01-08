import bpy

#主面板
class MainPanel(bpy.types.Panel):
    bl_label ="白给的工具"
    bl_idname ="MainPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type = 'UI'
    bl_category ='白给的工具'
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def __init__(self) -> None:
        bpy.ops.baigave.read_mods_dir()
        bpy.ops.baigave.read_resourcepacks_dir()
        bpy.ops.baigave.read_versions_dir()
        super().__init__()

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
#导入面板     
class ImportPanel(bpy.types.Panel):
    bl_label ="导入"
    bl_idname ="ImportPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='MainPanel'
    #bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()    
        row.label(text = "导入",icon='ERROR')
        # 创建一个框
        box = layout.box()
        box.label(text="导入.schem文件")
        box.operator("baigave.import_schem", text="导入.schem文件")

        split_8D70F = box.split(factor=0.15, align=True)
        split_8D70F.enabled = True
        split_8D70F.active = True
        split_8D70F.alignment = 'Expand'.upper()
        if not True: split_8D70F.operator_context = "EXEC_DEFAULT"
        op = split_8D70F.operator('sna.my_generic_operator_a38b8', text='', icon_value=692, emboss=True, depress=False)
        split_8D70F.prop(bpy.context.preferences.addons['BaiGave_Plugin'].preferences, 'sna_minsize', text='方块数分界线', icon_value=0, emboss=True)
        split_3E557 = box.split(factor=0.47, align=True)
        split_3E557.enabled = True
        split_3E557.active = True
        split_3E557.alignment = 'Expand'.upper()
        if not True: split_3E557.operator_context = "EXEC_DEFAULT"
        split_3E557.prop(bpy.context.preferences.addons['BaiGave_Plugin'].preferences, 'sna_processnumber', text='进程数', icon_value=0, emboss=False)
        split_3E557.prop(bpy.context.preferences.addons['BaiGave_Plugin'].preferences, 'sna_intervaltime', text='间隔(秒)', icon_value=0, emboss=True)
        layout.split()
        row = layout.row()
        row.operator("baigave.import_nbt", text="导入.nbt文件")

        row = layout.row()
        row.operator("object.add_sway_animation", text="草摇摆")

        row = layout.row()
        row.operator("baigave.map_optimize", text="执行优化")

        # 添加布尔属性的选项
        row = layout.row()
        row.prop(scene, "is_weld", text="合并重叠顶点")
        
        row = layout.row()
        row.operator("baigave.objtoblocks", text="转换网格体")
        # row = layout.row()
        # row.operator("baigave.spawn_map", text="生成地图")
        # row = layout.row()
        # row.operator("baigave.select", text="选择区域")
        # row = layout.row()
        # row.operator("baigave.import_world", text="导入世界")
        # row = layout.row()
        # row.operator("baigave.create_save", text="创建存档")

#导出面板     
class ExportPanel(bpy.types.Panel):
    bl_label ="导出"
    bl_idname ="ExportPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()    
        row.label(text = "导出",icon='ERROR')

# 资源包面板
class ResourcepacksPanel(bpy.types.Panel):
    bl_label = "资源包"
    bl_idname = "ResourcepacksPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BaiGave'
    bl_parent_id = 'ModPanel'
    bl_options = {'DEFAULT_CLOSED'}


    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, "resourcepacks_dir", text="路径")  # 添加路径字段
        row = layout.row()
        scene = context.scene
        my_properties = scene.my_properties 
        row.template_list("ResourcepackList", "", my_properties, "resourcepack_list", my_properties, "resourcepack_list_index")
        
        col = row.column(align=True)
         # 上下移动按钮
        col.operator("baigave.move_resourcepack_item", text="", icon='TRIA_UP').direction = 'UP'
        col.operator("baigave.move_resourcepack_item", text="", icon='TRIA_DOWN').direction = 'DOWN'  
        col.operator("baigave.add_resourcepack_operator",text="", icon='ADD')
        col.operator("baigave.delete_resourcepack_operator",text="", icon='REMOVE')
        # 添加打印选中项目的按钮
        layout.operator("baigave.unzip_resourcepacks_operator", text="刷新")

#模组界面
class ModPanel(bpy.types.Panel):
    bl_label = "Mod 设置"
    bl_idname = "ModPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BaiGave'
    bl_parent_id = 'MainPanel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        my_properties = scene.my_properties 
        row = layout.row()
        # 添加 Minecraft 版本选择
        row.label(text="选择 Minecraft 版本:")
        row = layout.row()
        row.prop(scene, "version_list", text="")
        row = layout.row()
        row.label(text="已加载的模组：")
        row = layout.row()
        # 使用template_list来显示模组列表
        row.template_list("ModList", "", my_properties, "mod_list", my_properties, "mod_list_index")
        col = row.column(align=True)
         # 上下移动按钮
        col.operator("baigave.move_mod_item", text="", icon='TRIA_UP').direction = 'UP'
        col.operator("baigave.move_mod_item", text="", icon='TRIA_DOWN').direction = 'DOWN'    
        col.operator("baigave.add_mod_operator",text="", icon='ADD')
        col.operator("baigave.delete_mod_operator",text="", icon='REMOVE')
        # 添加一个按钮
        layout.operator("baigave.unzip_mods_operator", text="刷新")

# -----------------------------------------------------------------------------
# UIList
# -----------------------------------------------------------------------------

# 定义 UIList 类 ResourcepackList
class ResourcepackList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)

# 定义 UIList 类 ModList
class ModList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # 显示模组名称、图标和描述
            row = layout.row(align=True)
            row.label(text=item.name)
            row.label(text=item.description)

classes=[ResourcepackList,ModList,MainPanel,RigPanel,BlockPanel,ImportPanel,ExportPanel,ModPanel,ResourcepacksPanel]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        