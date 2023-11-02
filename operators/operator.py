import bpy
import os
import time
import random
import pickle
import threading
import subprocess
import sys

from .block import block
from .level import create_level
from .tip import button_callback

from .functions import get_all_data
from .schem import schem,schem_p,schem_leaves,schem_liquid,schem_dirtgrass,schem_snow,schem_deepstone,schem_sandgravel
from .generate import generate
from .chunk  import chunk as create_chunk
from .schem import schem_all,schem

import gzip
import amulet
import amulet_nbt
import zipfile
import logging
logging.getLogger("amulet").setLevel(logging.FATAL)
logging.getLogger("PyMCTranslate").setLevel(logging.FATAL)




# 定义 Operator 类 VIEW3D_read_dir
class VIEW3D_read_dir(bpy.types.Operator):
    """读取目录"""
    bl_idname = "view3d.read_dir"
    bl_label = "读取目录"
    
    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        my_properties.my_list.clear()

        path = context.scene.view3d_read_dir  # 使用自定义路径

        for path, dirs, files in os.walk(path):
            for filename in files:
                if filename.lower().endswith(".zip"):  # 检查文件扩展名
                    # 将文件名添加到列表属性
                    item = my_properties.my_list.add()
                    item.name = filename.replace(".zip", "")

        return {'FINISHED'}
    
# 定义 UIList 类 MyFileList
class MyFileList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)

class PRINT_SELECTED_ITEM(bpy.types.Operator):
    """打印选中的项目"""
    bl_idname = "view3d.print_selected_item"
    bl_label = "打印选中的项目"

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        selected_item = my_properties.my_list[my_properties.my_list_index]
        zip_file_path = context.scene.view3d_read_dir + "\\" + selected_item.name + ".zip"  # 使用自定义路径
        mcmeta_content = ""

        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                if "pack.mcmeta" in zip_file.namelist():
                    with zip_file.open("pack.mcmeta") as mcmeta_file:
                        mcmeta_content = mcmeta_file.read().decode("utf-8")
                else:
                    self.report({'INFO'}, "文件 'pack.mcmeta' 不存在于.zip文件中。")
            self.report({'INFO'}, f"pack.mcmeta 内容：\n{mcmeta_content}")
        except Exception as e:
            self.report({'ERROR'}, f"无法打开或读取.zip文件: {e}")

        return {'FINISHED'}

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
        #清空缓存文件夹
        start_time = time.time()
        folder_path = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache"
        file_names = os.listdir(folder_path)
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
            
        # 遍历字典的键值对
        d = {}
        
        nbt_data = amulet_nbt._load_nbt.load(self.filepath)
        
        Palette = dict(nbt_data["Palette"])
        Palette = {int(v): k for k, v in Palette.items()}
        size = {
            "x":int(nbt_data["Width"]),
            "y":int(nbt_data["Height"]),
            "z":int(nbt_data["Length"])
        }
        def get_block_data(x, y, z):
            if 0 <= x < size["x"] and 0 <= y < size["y"] and 0 <= z < size["z"]:
                index = y * size["x"]* size["z"] + z* size["x"] + x
                if 0 <= index < len(nbt_data["BlockData"]):
                    return nbt_data["BlockData"][index]
            return None

        # 遍历 x, y, z 坐标
        for x in range(size["x"]):
            for y in range(size["y"]):
                for z in range(size["z"]):
                    block_data = get_block_data(x, y, z)
                    if block_data is not None:
                        block_id = Palette.get(block_data)
                        d[(x, z, y)] = str(block_id)
                    else:
                        print("a")
                        d[(x, z, y)] = "minecraft:air"
        #print(d)
        # print("x*y*z:"+str(size["x"]*size["y"]*size["z"]))
        # print(len(nbt_data["BlockData"]))
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

        #测试，把每个方块都单独作为一个物体生成出来
        #schem_all(d)
        #测试 单独导出自定义方块
        #schem(d)
        end_time = time.time()
        print("预处理时间：", end_time - start_time, "秒")

        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'wb') as file:
            pickle.dump((d,self.filepath),file)
        with open(VarCachePath, 'rb') as file:
            d,schempath = pickle.load(file)
        
        #bpy.context.space_data.shading.color_type = 'TEXTURE'
        #bpy.context.space_data.overlay.show_stats = True

        #多进程导入模型
        def import_schems():
            blender_path = bpy.app.binary_path
            ImportPath = bpy.utils.script_path_user()
            MPplantsPath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_plants.py"
            MPleavesPath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_leaves.py"
            MPliquidPath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_liquid.py"
            MPothersPath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_others.py"
            MPdirtgrassPath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_dirtgrass.py"
            MPdeepstonePath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_deepstone.py"
            MPsandgravelPath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_sandgravel.py"
            MPsnowPath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_snow.py"

            #多进程实现方法：后台启动headless blender(-b)，只运行python代码(-P)，不显示界面
            subprocess.Popen([blender_path, "-b", "-P", MPplantsPath])
            subprocess.Popen([blender_path, "-b", "-P", MPleavesPath])
            subprocess.Popen([blender_path, "-b", "-P", MPliquidPath])
            subprocess.Popen([blender_path, "-b","-P", MPothersPath])
            subprocess.Popen([blender_path, "-b", "-P", MPdirtgrassPath])
            subprocess.Popen([blender_path, "-b", "-P", MPdeepstonePath])
            subprocess.Popen([blender_path, "-b", "-P", MPsandgravelPath])
            subprocess.Popen([blender_path, "-b", "-P", MPsnowPath])

            b1=b2=b3=b4=b5=b6=b7=b8=0
            p1 = ImportPath + "/addons/BaiGave_Plugin/schemcache/plants.blend"
            p2 = ImportPath + "/addons/BaiGave_Plugin/schemcache/leaves.blend"
            p3 = ImportPath + "/addons/BaiGave_Plugin/schemcache/liquid.blend"
            p4 = ImportPath + "/addons/BaiGave_Plugin/schemcache/others.blend"
            p5 = ImportPath + "/addons/BaiGave_Plugin/schemcache/dirtgrass.blend"
            p6 = ImportPath + "/addons/BaiGave_Plugin/schemcache/deepstone.blend"
            p7 = ImportPath + "/addons/BaiGave_Plugin/schemcache/sandgravel.blend"
            p8 = ImportPath + "/addons/BaiGave_Plugin/schemcache/snow.blend"

            #等待每个进程生成的缓存文件，然后追加到当前场景
            while True:
                if os.path.exists(p1) and b1==0:
                    b1=1
                    with bpy.data.libraries.load(p1) as (data_from, data_to):
                        data_to.objects = [name for name in data_from.objects if name == "plants"]
                    for obj in data_to.objects:
                        bpy.context.scene.collection.objects.link(obj)
                    end_time = time.time()
                    print("代码块执行时间：", end_time - start_time, "秒")
                elif os.path.exists(p2) and b2==0:
                    b2=1
                    with bpy.data.libraries.load(p2) as (data_from, data_to):
                        data_to.objects = [name for name in data_from.objects if name == "leaves"]
                    for obj in data_to.objects:
                        bpy.context.scene.collection.objects.link(obj)
                    end_time = time.time()
                    print("代码块执行时间：", end_time - start_time, "秒")
                elif os.path.exists(p3) and b3==0:
                    b3=1
                    with bpy.data.libraries.load(p3) as (data_from, data_to):
                        data_to.objects = [name for name in data_from.objects if name == "liquid"]
                    for obj in data_to.objects:
                        bpy.context.scene.collection.objects.link(obj)
                    end_time = time.time()
                    print("代码块执行时间：", end_time - start_time, "秒")
                elif os.path.exists(p4) and b4==0:
                    b4=1
                    with bpy.data.libraries.load(p4) as (data_from, data_to):
                        data_to.objects = [name for name in data_from.objects if name == "others"]
                    for obj in data_to.objects:
                        bpy.context.scene.collection.objects.link(obj)
                    end_time = time.time()
                    print("代码块执行时间：", end_time - start_time, "秒")
                elif os.path.exists(p5) and b5==0:
                    b5=1
                    with bpy.data.libraries.load(p5) as (data_from, data_to):
                        data_to.objects = [name for name in data_from.objects if name == "dirtgrass"]
                    for obj in data_to.objects:
                        bpy.context.scene.collection.objects.link(obj)
                    end_time = time.time()
                    print("代码块执行时间：", end_time - start_time, "秒")
                elif os.path.exists(p6) and b6==0:
                    b6=1
                    with bpy.data.libraries.load(p6) as (data_from, data_to):
                        data_to.objects = [name for name in data_from.objects if name == "deepstone"]
                    for obj in data_to.objects:
                        bpy.context.scene.collection.objects.link(obj)
                    end_time = time.time()
                    print("代码块执行时间：", end_time - start_time, "秒")
                elif os.path.exists(p7) and b7==0:
                    b7=1
                    with bpy.data.libraries.load(p7) as (data_from, data_to):
                        data_to.objects = [name for name in data_from.objects if name == "sandgravel"]
                    for obj in data_to.objects:
                        bpy.context.scene.collection.objects.link(obj)
                    end_time = time.time()
                    print("代码块执行时间：", end_time - start_time, "秒")
                elif os.path.exists(p8) and b8==0:
                    b8=1
                    with bpy.data.libraries.load(p8) as (data_from, data_to):
                        data_to.objects = [name for name in data_from.objects if name == "snow"]
                    for obj in data_to.objects:
                        bpy.context.scene.collection.objects.link(obj)
                    end_time = time.time()
                    print("代码块执行时间：", end_time - start_time, "秒")
                elif b1==1 and b2==1 and b3==1 and b4==1 and b5==1 and b6==1 and b7==1 and b8==1:
                    # 添加材质
                    materials = bpy.data.materials
                    for material in materials:
                        try:
                            node_tree = material.node_tree
                            nodes = node_tree.nodes
                            for node in nodes:
                                if node.type == 'TEX_IMAGE':
                                    if node.name == '色图':
                                        node.image = bpy.data.images.get(filename+"_colormap")
                        except:
                            pass
                    break
                else:
                    time.sleep(0.1)

        start_time = time.time()
        #多线程防止blender卡死
        threading.Thread(target=import_schems).start()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


#每个进程调用一类功能，导入特定方块
class ImportSchemPlants(bpy.types.Operator):
    bl_idname = "baigave.import_schem_plants"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            d,schempath = pickle.load(file)
        schem_p(d,"plants")
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/plants.blend"
        bpy.ops.wm.save_as_mainfile(filepath=ModelCachePath)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ImportSchemLeaves(bpy.types.Operator):
    bl_idname = "baigave.import_schem_leaves"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            d,schempath = pickle.load(file)
        schem_leaves(d,"leaves")
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/leaves.blend"
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
    
class ImportSchemOthers(bpy.types.Operator):
    bl_idname = "baigave.import_schem_others"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            d,schempath = pickle.load(file)
        schem(d,"others")
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/others.blend"
        bpy.ops.wm.save_as_mainfile(filepath=ModelCachePath)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ImportSchemDirtGrass(bpy.types.Operator):
    bl_idname = "baigave.import_schem_dirtgrass"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            d,schempath = pickle.load(file)
        schem_dirtgrass(d,"dirtgrass")
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/dirtgrass.blend"
        bpy.ops.wm.save_as_mainfile(filepath=ModelCachePath)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ImportSchemDeepStone(bpy.types.Operator):
    bl_idname = "baigave.import_schem_deepstone"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            d,schempath = pickle.load(file)
        schem_deepstone(d,"deepstone")
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/deepstone.blend"
        bpy.ops.wm.save_as_mainfile(filepath=ModelCachePath)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ImportSchemSandGravel(bpy.types.Operator):
    bl_idname = "baigave.import_schem_sandgravel"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            d,schempath = pickle.load(file)
        schem_sandgravel(d,"sandgravel")
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/sandgravel.blend"
        bpy.ops.wm.save_as_mainfile(filepath=ModelCachePath)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ImportSchemSnow(bpy.types.Operator):
    bl_idname = "baigave.import_schem_snow"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            d,schempath = pickle.load(file)
        schem_snow(d,"snow")
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/snow.blend"
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
            textures, elements = get_all_data(os.path.dirname(self.filepath)+"\\", filename)
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
