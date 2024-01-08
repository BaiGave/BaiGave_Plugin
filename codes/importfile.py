import bpy
import os
import time
import random
import pickle
import subprocess
from .structure import nbt
from itertools import groupby

from .block import block
#from .level import create_level
from .functions.tip import button_callback

from .functions.get_data import get_all_data
from .schem import schem_chunk,schem_liquid,schem
# from .unuse.generate import generate
# from .unuse.chunk  import chunk as create_chunk
from .functions.mesh_to_mc import create_mesh_from_dictionary

import gzip
import amulet
import amulet_nbt




class ImportNBT(bpy.types.Operator):
    bl_idname = "baigave.import_nbt"
    bl_label = "导入.nbt文件"
    
    # 定义一个属性来存储文件路径
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    # 定义一个属性来过滤文件类型，只显示.nbt文件
    filter_glob: bpy.props.StringProperty(default="*.nbt", options={'HIDDEN'})

    # 定义操作的执行函数
    def execute(self, context):
        # 获取文件路径
        filepath = self.filepath
        filename = os.path.basename(filepath)
        start_time = time.time()
        data = amulet_nbt.load(filepath)
        
        blocks =data["blocks"]
        entities = data["entities"]
        if "palette" in data:
            palette = data["palette"]
        elif "palettes" in data:
            palette = data["palettes"][0]
           

        size = data["size"]
        d = {}  

        for block in blocks:
            pos_tags = block['pos']  
            pos = tuple(tag.value for tag in pos_tags)  
            state = block['state'].value 
            block_name = palette[state]['Name'].value if 'Name' in palette[state] else palette[state]['nbt']['name'].value
            if 'Properties' in palette[state]:
                block_state = palette[state]['Properties'].value
                block_state = ', '.join([f'{k}={v}' for k, v in block_state.items()])
            elif 'nbt' in palette[state] and 'name' in palette[state]['nbt']:
                block_state = palette[state]['nbt']['name'].value
                block_state = ', '.join([f'{k}={v}' for k, v in block_state.items()])
            else:
                block_state = None
            
            if block_state is not None:
                d[(pos[0],pos[2],pos[1])] = str(block_name)+"["+block_state+"]"
            else:
                d[(pos[0],pos[2],pos[1])] = block_name
        end_time = time.time()
        print("代码块执行时间：", end_time - start_time, "秒")

        #普通方法，有面剔除，速度较慢。
        start_time = time.time()
        nbt(d,filename)
        end_time = time.time()
        print("代码块执行时间：", end_time - start_time, "秒")

        #py+几何节点做法，无面剔除，但速度快。
        start_time = time.time()
        create_mesh_from_dictionary(d,filename.replace(".nbt",""))
        end_time = time.time()
        print("代码块执行时间：", end_time - start_time, "秒")
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


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
        name=os.path.basename(self.filepath)
        #清空缓存文件夹
        start_time = time.time()
        folder_path = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache"
        file_names = os.listdir(folder_path)
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
        level = amulet.load_level(self.filepath)
        all_chunks=sorted(level.all_chunk_coords("main"))
        chunks = [list(point) for point in level.bounds("main").bounds]
        nbt_data = amulet_nbt._load_nbt.load(self.filepath)
        
        #data=nbt_data["BlockEntities"][0]["data"]["data"]
        # 解析数据为坐标点
        # coordinates = []
        # for i in range(0, len(data), 3):
        #     x = data[i]
        #     y = data[i + 1]
        #     z = data[i + 2]
        #     coordinates.append((x, y, z))

        # # 构建字典
        # coordinates_dict = {f"Point {index + 1}": point for index, point in enumerate(coordinates)}

        # 打印字典
        #print(data)
        #print(len(data))
        size = {
            "x":int(nbt_data["Width"]),
            "y":int(nbt_data["Height"]),
            "z":int(nbt_data["Length"])
        }
        
        # 设置图片的大小和颜色
        image_width = int(size["z"])
        image_height = int(size["x"])
        default_color = (0.47, 0.75, 0.35, 1.0)  # RGBA颜色，对应#79c05a

        # 创建一个新的图片
        filename = os.path.basename(self.filepath)
        image = bpy.data.images.new("colormap", width=image_width, height=image_height)
        image.use_fake_user = True

        #设置默认颜色
        for y in range(image_height):
            for x in range(image_width):
                pixel_index = (y * image_width + x) * 4  # RGBA每个通道都是4个值
                image.pixels[pixel_index : pixel_index + 4] = default_color

        #小模型，直接导入
        if (chunks[1][0]-chunks[0][0])*(chunks[1][1]-chunks[0][1])*(chunks[1][2]-chunks[0][2]) < bpy.context.preferences.addons['BaiGave_Plugin'].preferences.sna_minsize:
            #几何节点+py方法
            schem(level,chunks,name)

            materials = bpy.data.materials
            for material in materials:
                try:
                    node_tree = material.node_tree
                    nodes = node_tree.nodes
                    for node in nodes:
                        if node.type == 'TEX_IMAGE':
                            if node.name == '色图':
                                node.image = bpy.data.images.get("colormap")
                except Exception as e:
                    print("材质出错了:", e)

        #大模型，分块导入
        else:
            groups = groupby(sorted(all_chunks), key=lambda x: x[0])
            # 合并区块，减少导入次数
            mp_chunks = []
            for k, g in groups:
                group_list = list(g)
                mp_chunks.append((group_list[0][0], group_list[0][1], group_list[-1][0], group_list[-1][1]))

            # for i in mp_chunks:
            #     schem_chunk(level,chunks,i)
            VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
            with open(VarCachePath, 'wb') as file:
                pickle.dump((chunks,mp_chunks,self.filepath,bpy.context.preferences.addons['BaiGave_Plugin'].preferences.sna_intervaltime),file)

            #多进程导入模型
            bpy.data.window_managers["WinMan"].bcp_max_connections = 32
            bpy.data.window_managers['WinMan'].bcp_port = 5001
            bpy.ops.wm.open_command_port()
            blender_path = bpy.app.binary_path
            ImportPath = bpy.utils.script_path_user()
            MultiprocessPath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_mp.py"

            #多进程实现方法：后台启动headless blender(-b)，只运行python代码(-P)，不显示界面
            for num in range(len(mp_chunks)):
                ChunkIndex = f"import bpy;bpy.context.scene.frame_current = {num}"
                subprocess.Popen([blender_path,"-b","--python-expr",ChunkIndex,"-P",MultiprocessPath])

            schem_liquid(level,chunks)
        end_time = time.time()
        print("预处理时间：", end_time - start_time, "秒")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


#每个进程调用一类功能，导入特定方块
class MultiprocessSchem(bpy.types.Operator):
    bl_idname = "baigave.import_schem_mp"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        start_time = time.time()
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            chunks,mp_chunks,schempath,interval = pickle.load(file)

        level = amulet.load_level(self.filepath)
        current_frame = int(bpy.context.scene.frame_current)
        nbt_data = amulet_nbt._load_nbt.load(self.filepath)
        #print(nbt_data["BlockEntities"])
        
        size = {
            "x":int(nbt_data["Width"]),
            "y":int(nbt_data["Height"]),
            "z":int(nbt_data["Length"])
        }
        #print(size)

        # 设置图片的大小和颜色
        image_width = int(size["z"])
        image_height = int(size["x"])
        default_color = (0.47, 0.75, 0.35, 1.0)  # RGBA颜色，对应#79c05a

        # 创建一个新的图片
        filename = os.path.basename(self.filepath)
        image = bpy.data.images.new(filename+"_colormap", width=image_width, height=image_height)

        #设置默认颜色
        for y in range(image_height):
            for x in range(image_width):
                pixel_index = (y * image_width + x) * 4  # RGBA每个通道都是4个值
                image.pixels[pixel_index : pixel_index + 4] = default_color

        schem_chunk(level,chunks,mp_chunks[current_frame])
        end_time = time.time()
        print("预处理时间：", end_time - start_time, "秒")

        # obj = bpy.data.objects['Schemetics']
        # obj.location = (subchunks[0][0]-origin[0],-(subchunks[0][2]-origin[2]),subchunks[0][1]-origin[1])
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/chunk{}.blend".format(current_frame)
        bpy.ops.wm.save_as_mainfile(filepath=ModelCachePath)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    

class ImportSchemLiquid(bpy.types.Operator):
    bl_idname = "baigave.import_schem_liquid"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            d,schempath = pickle.load(file)
        schem_liquid(d,"liquid")
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/liquid.blend"
        bpy.ops.wm.save_as_mainfile(filepath=ModelCachePath)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class Importjson(bpy.types.Operator):
    """导入选定的json文件"""
    bl_idname = "baigave.import_json"
    bl_label = "导入json文件"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        # 检查文件路径是否有效
        if os.path.isfile(self.filepath) and self.filepath.endswith(".json"):
            # 获取文件名
            filename = os.path.basename(self.filepath)
            textures, elements,parent = get_all_data(os.path.dirname(self.filepath)+"\\", filename)
            position = [0, 0, 0]
            has_air = [True, True, True, True, True, True]
            block(textures, elements, position,[0,0,0], filename, has_air)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "请选择有效的.json文件")
            return {'CANCELLED'}

    def invoke(self, context, event):
        # 打开文件选择对话框
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SNA_AddonPreferences_F35F8(bpy.types.AddonPreferences):
    bl_idname = 'BaiGave_Plugin'
    sna_processnumber: bpy.props.IntProperty(name='ProcessNumber', description='目前自动组合区块，无需设置', default=6, subtype='NONE', min=1, max=64)
    sna_intervaltime: bpy.props.FloatProperty(name='IntervalTime', description='处理完每个区块，间隔一段时间再导入进来', default=1.0, subtype='NONE', unit='NONE', min=0.0, max=10.0, step=3, precision=1)
    sna_minsize: bpy.props.IntProperty(name='MinSize', description='超过这个数就会启用多进程分区块导入', default=1000000, subtype='NONE', min=1000, max=99999999)

    def draw(self, context):
        if not (False):
            layout = self.layout 


class SNA_OT_My_Generic_Operator_A38B8(bpy.types.Operator):
    bl_idname = "sna.my_generic_operator_a38b8"
    bl_label = "刷新"
    bl_description = "自动设置以下参数"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if bpy.app.version >= (3, 0, 0) and True:
            cls.poll_message_set('')
        return not False

    def execute(self, context):
        Variable = None
        Variable=int(os.cpu_count()/2)
        bpy.context.preferences.addons['BaiGave_Plugin'].preferences.sna_processnumber = Variable
        bpy.context.preferences.addons['BaiGave_Plugin'].preferences.sna_intervaltime = 1
        bpy.context.preferences.addons['BaiGave_Plugin'].preferences.sna_minsize = 1000000
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


# class GenerateWorld(bpy.types.Operator):
#     """创建世界(未完成)"""
#     bl_idname = "baigave.create_save"
#     bl_label = "创建存档"

#     # 定义操作的执行函数
#     def execute(self, context):
#         World_Name = "World1"
#         SpawnX=0
#         SpawnY=64
#         SpawnZ=0
#         hardcore=0
#         Difficulty=0
#         allowCommands=1
#         LastPlayed = int(round(time.time() * 1000))
#         DayTime=16000
#         Seed = random.randint(0, 10000)


#         folderpath = 'C:\\Users\\user\\Desktop\\白给的人模\\BaiGave_Plugin\\saves\\'+World_Name

#         # 创建存档文件夹
#         if not os.path.exists(folderpath):
#             os.makedirs(folderpath)
#         level_dat = create_level(World_Name,SpawnX,SpawnY,SpawnZ,hardcore,Difficulty,allowCommands,LastPlayed,DayTime,Seed)
#         # 将NBT数据写入文件
#         filepath = 'C:\\Users\\user\\Desktop\\白给的人模\\BaiGave_Plugin\\saves\\'+World_Name+'\\level.dat'
#         with gzip.open(filepath, 'wb') as file:
#             level_dat.write(file)

        
#         from amulet.api.chunk import Chunk
#         from amulet.api.block import Block

#         level = amulet.load_level("C:\\Users\\user\\Desktop\\白给的人模\\BaiGave_Plugin\\saves\\"+World_Name)
#         new_chunk = Chunk(0, 0)
#         stone = Block("minecraft", "stone")
#         new_chunk.set_block(10,171,10,stone)
#         new_chunk.changed = True
#         level.put_chunk(new_chunk, "minecraft:overworld")

#         level.save()

#         level.close()

        
#         return {'FINISHED'}
    
# class SelectArea(bpy.types.Operator):
#     """选择区域（性能有问题）"""
#     bl_label = "选择区域"
#     bl_idname = 'baigave.select'
    
#     def execute(self, context):
#         # 获取当前场景的名称
#         current_scene = bpy.context.scene.name
#         # 如果场景名称不为"地图"，则返回
#         if current_scene != "地图":
#             button_callback(self, context,"地图仍未创建！")
#             return {'CANCELLED'}
#         # 检查当前场景是否已经有名为"Map"的集合
#         existing_collections = bpy.data.collections.values()
#         for coll in existing_collections:
#             if coll.name == "Map":
#                 button_callback(self, context,"已经存在选择框！(如果你删除了一些东西请连同集合一起删除）")
#                 return {'CANCELLED'}
#         # 获取当前文件的路径
#         current_path = os.path.dirname(os.path.abspath(__file__))
#         # 拼接路径和文件名
#         filepath = os.path.join(current_path, "blend_files","Map.blend")
#         # 从文件中加载名为"Map"的集合
#         with bpy.data.libraries.load(filepath) as (data_from, data_to):
#             data_to.collections = ["Map"]
#         # 将集合链接到当前场景
#         for coll in data_to.collections:
#             if coll is not None:
#                 bpy.context.scene.collection.children.link(coll)
#         return {'FINISHED'}

# class ImportWorld(bpy.types.Operator):
#     """导入世界(性能有问题)"""
#     bl_label = "导入世界"
#     bl_idname = 'baigave.import_world'

#     current_chunk_index = 0  # 当前处理的区块索引

#     def modal(self, context, event):
#         if event.type == 'ESC':
#             # 如果用户按下ESC键，停止模态操作
#             return {'CANCELLED'}

#         if self.current_chunk_index < len(self.processed_chunks):
#             # 处理下一个区块
#             chunk = self.processed_chunks[self.current_chunk_index]
#             x = chunk.cx
#             z = chunk.cz
#             self.process_chunk(self.level,chunk, x, z)

#             self.current_chunk_index += 1
#         else:
#             # 完成所有区块的处理
#              # 获取当前时间
#             end_time = time.time()

#             # 计算代码块执行时间
#             execution_time = end_time - self.start_time

#             # 打印执行时间
#             print("代码块执行时间：", execution_time, "秒")
#             return {'FINISHED'}
#         # 继续模态操作
#         return {'RUNNING_MODAL'}

#     def execute(self, context):
#         # 获取当前时间
#         self.start_time = time.time()
#         from .map import processed_chunks
#         from .map import level
#         self.level = level
#         self.processed_chunks = []  # 重置处理过的区块列表

#         # 获取选择区域的位置
#         object_names = ["pos1", "pos2"]
#         positions = {name: bpy.data.objects[name].matrix_world.translation * 1024 for name in object_names if name in bpy.data.objects}

#         # 计算选择区域的范围
#         x_values = [int(position.x) for position in positions.values()]
#         z_values = [int(position.y) for position in positions.values()]
#         min_x = min(x_values) // 16
#         max_x = max(x_values) // 16
#         min_z = min(z_values) // 16
#         max_z = max(z_values) // 16

#         # 获取需要处理的区块
#         for chunk in processed_chunks:
#             x = chunk.cx
#             z = chunk.cz

#             if min_x <= x <= max_x and min_z <= z <= max_z:
#                 self.processed_chunks.append(chunk)

#         # 设置模态操作属性
#         context.window_manager.modal_handler_add(self)

#         # 启动模态操作
#         return {'RUNNING_MODAL'}

#     def process_chunk(self, level,chunk, x, z):
#         vertices,faces,texture_list,uv_list,direction,uv_rotation_list = create_chunk(chunk, level)
#         generate(x, z, vertices, faces, texture_list, uv_list, direction, uv_rotation_list)

classes=[ImportSchem,MultiprocessSchem,Importjson,#ImportWorld,SelectArea, GenerateWorld,
         ImportNBT,SNA_AddonPreferences_F35F8,SNA_OT_My_Generic_Operator_A38B8]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    