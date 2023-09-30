import bpy
import os
import time
import random

from math import floor
from .block import block
from .level import create_level
from .tip import button_callback

from .functions import get_all_data
from .schem import schem
from .generate import generate
from .chunk  import chunk as create_chunk



import gzip
import amulet
import amulet_nbt
import logging
logging.getLogger("amulet").setLevel(logging.FATAL)
logging.getLogger("PyMCTranslate").setLevel(logging.FATAL)

#主面板
class MainPanel(bpy.types.Panel):
    bl_label ="白给的工具"
    bl_idname ="MainPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type = 'UI'
    bl_category ='BaiGave'
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.label(text = "白给的工具",icon='BOLD')
#人物绑定面板        
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
        
        row.label(text = "人模",icon='ERROR')
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
        layout.prop(BaiGave,"JsonImportSpeed")
        row.operator("baigave.import_json", text="导入.json文件")
#世界面板     
class WorldPanel(bpy.types.Panel):
    bl_label ="世界"
    bl_idname ="WorldPanel"
    bl_space_type ='VIEW_3D'
    bl_region_type ='UI'
    bl_category ='BaiGave'
    bl_parent_id ='MainPanel'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()    
        row.label(text = "世界",icon='ERROR')
        
        row = layout.row()
        row.operator("baigave.import_schem", text="导入.schem文件")
        row = layout.row()
        row.operator("baigave.spawn_map", text="生成地图")
        row = layout.row()
        row.operator("baigave.select", text="选择区域")
        row = layout.row()
        row.operator("baigave.import_world", text="导入世界")
        row = layout.row()
        row.operator("baigave.create_save", text="创建存档")

# 定义一个导入.schem文件的操作类
class ImportSchem(bpy.types.Operator):
    bl_idname = "baigave.import_schem"
    bl_label = "导入.schem文件"
    
    # 定义一个属性来存储文件路径
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    # 定义一个属性来过滤文件类型，只显示.schem文件
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    # 定义操作的执行函数
    def execute(self, context):
        # 遍历字典的键值对
        d = {}
        nbt_data = amulet_nbt._load_nbt.load(self.filepath)
        Palette = dict(nbt_data["Palette"])
        Palette = {int(v): k for k, v in Palette.items()}
        size = {
            "x":int(nbt_data["Length"]),
            "y":int(nbt_data["Height"]),
            "z":int(nbt_data["Width"])
        }
        
        for i in range(len(nbt_data["BlockData"])):
            x = floor((i % (size["z"] * size["x"])) % size["z"])
            y = floor(i / (size["z"] * size["x"]))
            z = floor((i % (size["z"] * size["x"])) / size["z"])
            
            d[(x, z, y)] = str(Palette[int(nbt_data["BlockData"][i])])

        # 获取当前时间
        start_time = time.time()
        schem(d,os.path.basename(self.filepath))

        # 获取当前时间
        end_time = time.time()

        # 计算代码块执行时间
        execution_time = end_time - start_time

        # 打印执行时间
        print("代码块执行时间：", execution_time, "秒")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}
# 定义一个批量导入json文件的操作类
class Importjson(bpy.types.Operator):
    """点击导入json文件"""
    bl_idname = "baigave.import_json"
    bl_label = "导入json文件"
    _timer = None
    index = 0
    def modal(self, context, event):
        # 如果事件类型是计时器
        if event.type == 'TIMER':
            filepath = bpy.utils.script_path_user() + "\\addons\\BaiGave_Plugin\\assets\\minecraft\\models\\block\\"
            #测试
            #filepath = "C:\\Users\\user\\Desktop\\白给的人模\\BaiGave_Plugin\\assets\\minecraft\\models\\block\\"
            
            # 如果文件路径是一个目录
            if os.path.isdir(filepath):
                # 获取目录中的文件名
                filename = os.listdir(filepath)[self.index]
                # 如果文件名以.json结尾
                if filename.endswith(".json"):
                    #测试  
                    #filename = "hopper.json"
                    textures,elements,display = get_all_data(filepath, filename)
                    position =[self.index,0,0]

                    has_air= [True,True,True,True,True,True]
                    block(textures,elements,display,position,filename,has_air)
                    
                    # self.cancel(context)
                    # return {'FINISHED'}
                    # 索引加一
                    self.index += 1
                    # 如果索引超过了目录中的文件数
                    if self.index >= len(os.listdir(filepath)):
                        # 取消定时器并返回
                        self.cancel(context)
                        return {'FINISHED'}
        # 如果事件类型是ESC
        elif event.type == 'ESC':
            # 取消定时器并返回
            self.cancel(context)
            return {'CANCELLED'}
        # 其他情况，继续传递事件
        return {'PASS_THROUGH'}
    # 定义操作的执行函数
    def execute(self, context):
        # 在窗口管理器中添加一个定时器
        wm = context.window_manager
        self._timer = wm.event_timer_add(bpy.data.scenes["Scene"].BaiGave.JsonImportSpeed, window=context.window)
        # 在窗口管理器中添加这个操作符
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        # 从窗口管理器中移除定时器
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class GenerateWorld(bpy.types.Operator):
    """创建世界(未完成)"""
    bl_idname = "baigave.create_save"
    bl_label = "创建存档"

    # 定义操作的执行函数
    def execute(self, context):
        World_Name = "World1"
        SpawnX=0
        SpawnY=64
        SpawnZ=0
        hardcore=0
        Difficulty=0
        allowCommands=1
        LastPlayed = int(round(time.time() * 1000))
        DayTime=16000
        Seed = random.randint(0, 10000)


        folderpath = 'C:\\Users\\user\\Desktop\\白给的人模\\BaiGave_Plugin\\saves\\'+World_Name

        # 创建存档文件夹
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)
        level_dat = create_level(World_Name,SpawnX,SpawnY,SpawnZ,hardcore,Difficulty,allowCommands,LastPlayed,DayTime,Seed)
        # 将NBT数据写入文件
        filepath = 'C:\\Users\\user\\Desktop\\白给的人模\\BaiGave_Plugin\\saves\\'+World_Name+'\\level.dat'
        with gzip.open(filepath, 'wb') as file:
            level_dat.write(file)


        from amulet.api.chunk import Chunk
        from amulet.api.block import Block

        level = amulet.load_level("C:\\Users\\user\\Desktop\\白给的人模\\BaiGave_Plugin\\saves\\"+World_Name)
        new_chunk = Chunk(0, 0)
        stone = Block("minecraft", "stone")
        new_chunk.set_block(10,171,10,stone)
        new_chunk.changed = True
        level.put_chunk(new_chunk, "minecraft:overworld")

        level.save()

        level.close()

        
        return {'FINISHED'}
    
class SelectArea(bpy.types.Operator):
    """选择区域（性能有问题）"""
    bl_label = "选择区域"
    bl_idname = 'baigave.select'
    
    def execute(self, context):
        # 获取当前场景的名称
        current_scene = bpy.context.scene.name
        # 如果场景名称不为"地图"，则返回
        if current_scene != "地图":
            button_callback(self, context,"地图仍未创建！")
            return {'CANCELLED'}
        # 检查当前场景是否已经有名为"Map"的集合
        existing_collections = bpy.data.collections.values()
        for coll in existing_collections:
            if coll.name == "Map":
                button_callback(self, context,"已经存在选择框！(如果你删除了一些东西请连同集合一起删除）")
                return {'CANCELLED'}
        # 获取当前文件的路径
        current_path = os.path.dirname(os.path.abspath(__file__))
        # 拼接路径和文件名
        filepath = os.path.join(current_path, "Map.blend")
        # 从文件中加载名为"Map"的集合
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.collections = ["Map"]
        # 将集合链接到当前场景
        for coll in data_to.collections:
            if coll is not None:
                bpy.context.scene.collection.children.link(coll)
        return {'FINISHED'}



class ImportWorld(bpy.types.Operator):
    """导入世界(性能有问题)"""
    bl_label = "导入世界"
    bl_idname = 'baigave.import_world'

    current_chunk_index = 0  # 当前处理的区块索引

    def modal(self, context, event):
        if event.type == 'ESC':
            # 如果用户按下ESC键，停止模态操作
            return {'CANCELLED'}

        if self.current_chunk_index < len(self.processed_chunks):
            # 处理下一个区块
            chunk = self.processed_chunks[self.current_chunk_index]
            x = chunk.cx
            z = chunk.cz
            self.process_chunk(self.level,chunk, x, z)

            self.current_chunk_index += 1
        else:
            # 完成所有区块的处理
             # 获取当前时间
            end_time = time.time()

            # 计算代码块执行时间
            execution_time = end_time - self.start_time

            # 打印执行时间
            print("代码块执行时间：", execution_time, "秒")
            return {'FINISHED'}
        # 继续模态操作
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # 获取当前时间
        self.start_time = time.time()
        from .map import processed_chunks
        from .map import level
        self.level = level
        self.processed_chunks = []  # 重置处理过的区块列表

        # 获取选择区域的位置
        object_names = ["pos1", "pos2"]
        positions = {name: bpy.data.objects[name].matrix_world.translation * 1024 for name in object_names if name in bpy.data.objects}

        # 计算选择区域的范围
        x_values = [int(position.x) for position in positions.values()]
        z_values = [int(position.y) for position in positions.values()]
        min_x = min(x_values) // 16
        max_x = max(x_values) // 16
        min_z = min(z_values) // 16
        max_z = max(z_values) // 16

        # 获取需要处理的区块
        for chunk in processed_chunks:
            x = chunk.cx
            z = chunk.cz

            if min_x <= x <= max_x and min_z <= z <= max_z:
                self.processed_chunks.append(chunk)

        # 设置模态操作属性
        context.window_manager.modal_handler_add(self)

        # 启动模态操作
        return {'RUNNING_MODAL'}

    def process_chunk(self, level,chunk, x, z):
        vertices,faces,texture_list,uv_list,direction,uv_rotation_list = create_chunk(chunk, level)
        generate(x, z, vertices, faces, texture_list, uv_list, direction, uv_rotation_list)