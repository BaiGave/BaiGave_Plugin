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
        bpy.ops.baigave.read_saves_dir()
        bpy.ops.baigave.read_schems_dir()
        bpy.ops.baigave.read_colors_dir()
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
    bl_options = {'DEFAULT_CLOSED'}
    
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
        split_3E557 = box.split(factor=1, align=True)
        split_3E557.enabled = True
        split_3E557.active = True
        split_3E557.alignment = 'Expand'.upper()
        if not True: split_3E557.operator_context = "EXEC_DEFAULT"
        split_3E557.prop(bpy.context.preferences.addons['BaiGave_Plugin'].preferences, 'sna_processnumber', text='进程数', icon_value=0, emboss=True)
        # split_3E557.prop(bpy.context.preferences.addons['BaiGave_Plugin'].preferences, 'sna_intervaltime', text='间隔(秒)', icon_value=0, emboss=True)
        layout.split()
        box = layout.box()
        box.label(text="导入方块")
        box.operator("baigave.import_block", text="导入方块")

        box = layout.box()
        box.label(text="导入.nbt文件")
        box.operator("baigave.import_nbt", text="导入.nbt文件")

        box = layout.box()
        row=box.row()
        col=box.column()
        row.label(text="导入MC地图")
        row.operator("baigave.spawn_map", text="2D预览")
        # 添加min [x, y, z]输入框
        row = box.row()
        row.label(text="最小坐标")
        row.prop(context.scene, "min_coordinates", text="")

        # 添加max [x, y, z]输入框
        row = box.row()
        row.label(text="最大坐标")
        row.prop(context.scene, "max_coordinates", text="")
        col.operator("baigave.import_world", text="导入世界")

        row = layout.row()
        row.operator("object.add_sway_animation", text="植物摇摆")

        row = layout.row()
        row.operator("baigave.map_optimize", text="执行优化")

        # 添加布尔属性的选项
        row = layout.row()
        row.prop(scene, "is_weld", text="合并重叠顶点")
        

        row = layout.row()
        row.operator("baigave.image_merger", text="合并图片")
        
        
        # row = layout.row()
        # row.operator("baigave.select", text="选择区域")
        # row = layout.row()
        # row.operator("baigave.import_world", text="导入世界")

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
        row.operator("baigave.export_schem", text="导出结构")
        box = layout.box()
        box.prop(scene, "save_list",text="选择世界")
        box.label( text="结构位置：("+str(scene.schem_size[0])+"," +str(scene.schem_size[1])+","+ str(scene.schem_size[2])+")")
        box.label(text="长:"+str(scene.schem_size[0])+"宽:" +str(scene.schem_size[1])+"高:"+ str(scene.schem_size[2])+" (blender坐标系)")

        box.operator("baigave.calculate_size",text="计算结构大小")
        box.operator("baigave.export_to_save",text="导出结构到存档")
#创建存档面板
class CreateLevel(bpy.types.Panel):
    bl_label ="创建存档"
    bl_idname ="CreateLevelPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()    
        row.label(text = "存档",icon='ERROR')
        row = layout.row()
        box = layout.box()
        row=box.row()
        box.prop(scene, "world_name", text="存档名称")
        row = box.row()
        row.label(text = "出生点坐标")
        row = box.row()
        row.prop(scene, "spawn_x", text="X")
        row.prop(scene, "spawn_y", text="Y")
        row.prop(scene, "spawn_z", text="Z")
        row = box.row()
        row.prop(scene, "difficulty", text="难度")
        row = box.row()
        row.prop(scene, "gametype", text="游戏模式")
        row = box.row()
        row.prop(scene, "overworld_generator_type", text="世界类型")
        row = box.row()
        row.prop(scene, "breaking_the_height_limit", text="突破限高？")
        row = box.row()
        row.prop(scene, "day_time", text="时间")
        row = box.row()
        row.prop(scene, "seed", text="种子")
        row = layout.row()
        row.operator("baigave.create_world", text="创建存档")
        

#创建编辑面板
class EditPanel(bpy.types.Panel):
    bl_label ="编辑"
    bl_idname ="EditPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        my_properties = scene.my_properties 
        
        row = layout.row()
        row.prop(scene, "color_list",text="对照表")
        row = layout.row()
        row.label(text="生成方块颜色对照表：")
        row = layout.row()
        
        row.template_list("ColorToBlockList", "", my_properties, "color_to_block_list", my_properties, "color_to_block_list_index")
        col = row.column()
        col.operator("baigave.add_color_to_block_operator",text="", icon='ADD')
        col.operator("baigave.delete_color_to_block_operator",text="", icon='REMOVE')
        row = layout.row()
        row.operator("baigave.make_color_dict", text="制作颜色-方块字典")
        row = layout.row()
        row.operator("baigave.objtoblocks", text="生成点云(转楼梯/台阶方块所需)")
        row = layout.row()
        row.operator("baigave.blockblender", text="转换网格体(方块)")

        
#创建存档面板
class MoreLevelSettings(bpy.types.Panel):
    bl_label ="更多设置"
    bl_idname ="MoreLevelSettings"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='CreateLevelPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        box = layout.box()

        box.label(text="指定单次命令执行可更改的最大方块数")
        box.prop(scene, "command_modification_block_limit", text="")

        box.label(text="决定了连锁型命令方块能连锁执行的总数量。	")
        box.prop(scene, "max_command_chain_length", text="")

        box.label(text="下雪时可在一格方块空间内堆积的雪的最高层数")
        box.prop(scene, "snow_accumulation_height", text="")

        box.label(text="首次进入服务器的玩家和没有重生点的死亡玩家在重生时与世界重生点坐标的距离")
        box.prop(scene, "spawn_radius", text="")

        box.label(text="每游戏刻每区段中随机的方块刻发生的频率")
        box.prop(scene, "random_tick_speed", text="")

        box.label(text="设置跳过夜晚所需的入睡玩家所占百分比。")
        box.prop(scene, "players_sleeping_percentage", text="")
#创建存档面板
class Ability(bpy.types.Panel):
    bl_label ="玩家能力"
    bl_idname ="Ability"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='CreateLevelPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        box = layout.box()
        box.prop(scene, "flySpeed", text="飞行速度")
        box.prop(scene, "walkSpeed", text="行走速度")
        # box.prop(scene, "flying", text="正在飞行？")
        # box.prop(scene, "mayfly", text="能飞行？")
        # box.prop(scene, "mayBuild", text="能建造？")
        # box.prop(scene, "instabuild", text="表示玩家是否可以瞬间摧毁方块")
        # box.prop(scene, "invulnerable", text="表示玩家是否能抵消除虚空伤害所有伤害和有害的效果")
        box.prop(scene, "luck", text="幸运值")
        box.prop(scene, "max_health", text="最大生命值")
        box.prop(scene, "knockback_resistance", text="击退抗性")
        #box.prop(scene, "movement_speed", text="移动加速度")
        box.prop(scene, "armor", text="盔甲值")
        box.prop(scene, "armor_toughness", text="盔甲韧性")
        box.prop(scene, "attack_damage", text="攻击伤害")
        box.prop(scene, "attack_speed", text="攻击速度")

#创建存档面板
class GameRules(bpy.types.Panel):
    bl_label ="游戏规则"
    bl_idname ="GameRules"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='MoreLevelSettings'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        box = layout.box()

        box.label(text="是否在聊天框中公告玩家进度的达成")
        box.prop(scene, "announce_advancements", text="")

        box.label(text="由方块源（除TNT）爆炸炸毁的方块是否会有概率不掉落")
        box.prop(scene, "block_explosion_drop_decay", text="")

        box.label(text="命令方块执行命令时是否在聊天框中向管理员显示")
        box.prop(scene, "command_block_output", text="")

        box.label(text="是否让服务器停止检查使用鞘翅玩家的移动速度。")
        box.prop(scene, "disable_elytra_movement_check", text="")

        box.label(text="是否禁用袭击")
        box.prop(scene, "disable_raids", text="")

        box.label(text="是否进行昼夜更替和月相变化")
        box.prop(scene, "do_daylight_cycle", text="")

        box.label(text="非生物实体是否掉落物品")
        box.prop(scene, "do_entity_drops", text="")

        box.label(text="火是否蔓延及自然熄灭")
        box.prop(scene, "do_fire_tick", text="")

        box.label(text="玩家死亡时是否不显示死亡界面直接重生")
        box.prop(scene, "do_immediate_respawn", text="")

        box.label(text="幻翼是否在夜晚生成")
        box.prop(scene, "do_insomnia", text="")

        box.label(text="玩家的合成配方是否需要解锁才能使用")
        box.prop(scene, "do_limited_crafting", text="")

        box.label(text="生物在死亡时是否掉落物品")
        box.prop(scene, "do_mob_loot", text="")

        box.label(text="生物是否自然生成。不影响刷怪笼")
        box.prop(scene, "do_mob_spawning", text="")

        box.label(text="控制灾厄巡逻队的生成")
        box.prop(scene, "do_patrol_spawning", text="")

        box.label(text="方块被破坏时是否掉落物品")
        box.prop(scene, "do_tile_drops", text="")

        box.label(text="控制流浪商人的生成")
        box.prop(scene, "do_trader_spawning", text="")

        box.label(text="决定藤蔓是否会向周围扩散，不影响洞穴藤蔓、缠怨藤和垂泪藤")
        box.prop(scene, "do_vines_spread", text="")

        box.label(text="监守者是否生成")
        box.prop(scene, "do_warden_spawning", text="")

        box.label(text="天气是否变化")
        box.prop(scene, "do_weather_cycle", text="")

        box.label(text="玩家是否承受窒息伤害")
        box.prop(scene, "drowning_damage", text="")

        box.label(text="玩家是否承受跌落伤害")
        box.prop(scene, "fall_damage", text="")

        box.label(text="玩家是否承受火焰伤害[仅Java版][1]")
        box.prop(scene, "fire_damage", text="")

        box.label(text="当被激怒的条件敌对生物的目标玩家死亡时，该生物是否恢复未激怒状态")
        box.prop(scene, "forgive_dead_players", text="")

        box.label(text="玩家是否承受冰冻伤害")
        box.prop(scene, "freeze_damage", text="")

        box.label(text="玩家是否能听到可无视距离播放给全部玩家的特定游戏事件音效")
        box.prop(scene, "global_sound_events", text="")

        box.label(text="玩家死亡后是否保留物品栏物品、经验（死亡时物品不掉落、经验不清空）")
        box.prop(scene, "keep_inventory", text="")

        box.label(text="流动的熔岩是否可产生熔岩源")
        box.prop(scene, "lava_source_conversion", text="")

        box.label(text="是否在服务器日志中记录管理员使用过的命令")
        box.prop(scene, "log_admin_commands", text="")

        box.label(text="由生物源爆炸炸毁的方块是否会有概率不掉落")
        box.prop(scene, "mob_explosion_drop_decay", text="")

        box.label(text="生物是否能够进行破坏性行为")
        box.prop(scene, "mob_griefing", text="")

        box.label(text="玩家是否能在饥饿值足够时自然恢复生命值")
        box.prop(scene, "natural_regeneration", text="")

        box.label(text="调试屏幕是否简化而非显示详细信息")
        box.prop(scene, "reduced_debug_info", text="")

        box.label(text="玩家执行命令的返回信息是否在聊天框中显示。")
        box.prop(scene, "send_command_feedback", text="")

        box.label(text="是否在聊天框中显示玩家的死亡信息。")
        box.prop(scene, "show_death_messages", text="")

        box.label(text="是否允许旁观模式的玩家生成区块")
        box.prop(scene, "spectators_generate_chunks", text="")

        box.label(text="由TNT爆炸炸毁的方块是否会有概率不掉落")
        box.prop(scene, "tnt_explosion_drop_decay", text="")

        box.label(text="被激怒的条件敌对生物是否攻击附近任何玩家")
        box.prop(scene, "universal_anger", text="")

        box.label(text="流动的水是否可产生水源")
        box.prop(scene, "water_source_conversion", text="")

       
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

# 定义 UIList 类 ColorToBlockList
class ColorToBlockList(bpy.types.UIList):
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

classes=[ResourcepackList,ColorToBlockList,ModList,MainPanel,RigPanel,BlockPanel,ImportPanel,ExportPanel,EditPanel,CreateLevel,ModPanel,ResourcepacksPanel,MoreLevelSettings,GameRules,
         Ability]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        