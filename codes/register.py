import bpy
import os
from .block import block
from .blockstates import get_model

def create_or_clear_collection(collection_name):
    # 检查集合是否已存在
    if collection_name in bpy.data.collections:
        existing_collection = bpy.data.collections.get(collection_name)
        try:
            bpy.context.scene.collection.children.link(existing_collection)
        except:
            pass

    else:
        # 创建一个新的集合
        new_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(new_collection)
        
def register_blocks(ids):
    collection_name = "Blocks"
    create_or_clear_collection(collection_name)
    collection = bpy.data.collections.get(collection_name)
    collection.hide_render = False
    collection.hide_viewport = False
    filepath = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp","Blocks.py")
    
    # 从文件中读取字典id_map
    id_map_file = open(filepath, 'r')
    id_map_content = id_map_file.read().strip()  # 读取文件内容并去除首尾空白字符
    id_map_file.close()

    try:
        id_map = eval(id_map_content)  # 尝试解析文件内容为字典
    except SyntaxError:  # 如果解析失败，即文件内容不是有效的Python字典表示
        id_map = {}  # 初始化为空字典

    # 更新id_map
    if id_map and collection.objects: # 如果id_map不为空
        next_id = max(id_map.values()) + 1
    else:
        next_id=0
        id_map={}
        id_map_file = open(filepath, 'w')
        id_map_file.write(str(id_map))  # 将字典转换为字符串并写入文件
        id_map_file.close()
        filename=str(next_id)+"#"+str("minecraft:air")
        textures,elements,rotation,uvlock =get_model("minecraft:air")
        position = [0, 0, 0]
        has_air = [True, True, True, True, True, True]
        bloc=block(textures, elements, position,rotation, filename, has_air,collection,uvlock)
        id_map["minecraft:air"] = next_id
        next_id =1
    if ids != None and ids!=[]:
        for id in ids:
            if id not in id_map:
                filename=str(next_id)+"#"+str(id)
                # 获取模型数据
                textures, elements, rotation, uvlock = get_model(id)
                position = [0, 0, 0]
                has_air = [True, True, True, True, True, True]

                # 创建block对象
                bloc = block(textures, elements, position, rotation, filename, has_air, collection,uvlock)
                
                id_map[id] = next_id
                next_id += 1  # 修改这里，确保每次迭代都递增next_id

    # 覆盖原始文件并保存更新后的id_map
    id_map_file = open(filepath, 'w')
    id_map_file.write("{\n")  # 开始写入字典
    for key, value in id_map.items():  # 将每对id都写入新的一行
        id_map_file.write(f"    '{key}': {value},\n")
    id_map_file.write("}\n")  # 结束写入字典
    id_map_file.close()

    collection.hide_render = True
    collection.hide_viewport = True
    return id_map

#临时修bug的
def register_blocks_only_names(ids):
    collection_name = "Blocks"
    collection = bpy.data.collections.get(collection_name)
    collection.hide_render = False
    collection.hide_viewport = False
    filepath = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp","Blocks.py")
    
    # 从文件中读取字典id_map
    id_map_file = open(filepath, 'r')
    id_map_content = id_map_file.read().strip()  # 读取文件内容并去除首尾空白字符
    id_map_file.close()

    try:
        id_map = eval(id_map_content)  # 尝试解析文件内容为字典
    except SyntaxError:  # 如果解析失败，即文件内容不是有效的Python字典表示
        id_map = {}  # 初始化为空字典

    next_id=0
    id_map={}
    id_map_file = open(filepath, 'w')
    id_map_file.write(str(id_map))  # 将字典转换为字符串并写入文件
    id_map_file.close()
    id_map["minecraft:air"] = next_id
    next_id =1
    if ids != None and ids!=[]:
        for id in ids:
            if id not in id_map:                
                id_map[id] = next_id
                next_id += 1  # 修改这里，确保每次迭代都递增next_id

    # 覆盖原始文件并保存更新后的id_map
    id_map_file = open(filepath, 'w')
    id_map_file.write("{\n")  # 开始写入字典
    for key, value in id_map.items():  # 将每对id都写入新的一行
        id_map_file.write(f"    '{key}': {value},\n")
    id_map_file.write("}\n")  # 结束写入字典
    id_map_file.close()

    collection.hide_render = True
    collection.hide_viewport = True
    return id_map