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
    
    next_id=0
    id_map={}
    filename=str(next_id)+"#"+str("minecraft:air")
    textures,elements,rotation,uvlock =get_model("minecraft:air")
    position = [0, 0, 0]
    has_air = [True, True, True, True, True, True]
    obj=block(textures, elements, position,rotation, filename, has_air,collection,uvlock)
    obj["id"] = "minecraft:air"
    id_map["minecraft:air"] = next_id
    next_id =1
    if ids != None and ids!=[]:
        ids = [id for id in ids if id not in id_map]
        for id in ids:
            filename=str(next_id)+"#"+str(id)
            # 获取模型数据
            textures, elements, rotation, uvlock = get_model(id)
            position = [0, 0, 0]
            has_air = [True, True, True, True, True, True]
            # 创建 block 对象
            obj=block(textures, elements, position, rotation, filename, has_air, collection, uvlock)
            obj["id"] = id
            id_map[id] = next_id
            next_id += 1  # 修改这里，确保每次迭代都递增 next_id

    collection.hide_render = True
    collection.hide_viewport = True
    return id_map

def registered_blocks(id_map):
    collection_name = "Blocks"
    create_or_clear_collection(collection_name)
    collection = bpy.data.collections.get(collection_name)
    collection.hide_render = False
    collection.hide_viewport = False
    
    for id in id_map:
        # 获取模型数据
        textures, elements, rotation, uvlock = get_model(id)
        position = [0, 0, 0]
        has_air = [True, True, True, True, True, True]
        filename=str(id_map[id])+"#"+str(id)
        # 创建 block 对象
        obj=block(textures, elements, position, rotation, filename, has_air, collection, uvlock)

    collection.hide_render = True
    collection.hide_viewport = True
    return id_map