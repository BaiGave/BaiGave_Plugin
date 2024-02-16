import bpy
import bmesh
from .model import create_mesh,add_mesh_to_collection,get_or_create_material,set_uv
from .blockstates import blockstates
import amulet
from .classification_files.block_type import liquid,exclude,sea_plants
import numpy as np
import os
from .register import create_or_clear_collection,register_blocks,registered_blocks
import pickle

#用于删除[]的部分 
def remove_brackets(input_string):
    output_string = ""
    inside_brackets = False

    for char in input_string:
        if char == '[':
            inside_brackets = True
        elif char == ']' and inside_brackets:
            inside_brackets = False
        elif not inside_brackets:
            output_string += char

    return output_string


def schem(level,chunks,cached,filename="schem",position=(0,0,0)):
    # 获取最小和最大坐标
    min_coords = chunks[0]
    max_coords = chunks[1]

    # 创建一个新的网格对象
    mesh = bpy.data.meshes.new(name=filename)
    mesh.attributes.new(name='blockid', type="INT", domain="POINT")
    mesh.attributes.new(name='biome', type="FLOAT_COLOR", domain="POINT")
    obj = bpy.data.objects.new(filename, mesh)

    # 将对象添加到场景中
    scene = bpy.context.scene
    scene.collection.objects.link(obj)
    # 创建一个新的集合
    collection_name="Blocks"
    create_or_clear_collection(collection_name)
    collection =bpy.data.collections.get(collection_name)
    nodetree_target = "SchemToBlocks"

    #导入几何节点
    try:
        nodes_modifier.node_group = bpy.data.node_groups[collection_name]
    except:
        file_path =bpy.context.scene.geometrynodes_blend_path
        inner_path = 'NodeTree'
        object_name = nodetree_target
        bpy.ops.wm.append(
            filepath=os.path.join(file_path, inner_path, object_name),
            directory=os.path.join(file_path, inner_path),
            filename=object_name
        )

    if not cached:
        # 创建顶点和顶点索引
        vertices = []
        ids = []  # 存储顶点id

        # 遍历范围内所有的坐标
        for x in range(min_coords[0], max_coords[0] + 1):
            for y in range(min_coords[1], max_coords[1] + 1):
                for z in range(min_coords[2], max_coords[2] + 1):
                    try:
                        # 获取坐标处的方块       
                        blc =level.get_version_block(x, y, z, "main",("java", (1, 20, 4)))
                        id =blc[0]
                        if isinstance(id,amulet.api.block.Block):
                            id = str(id).replace('"', '')
                            result = remove_brackets(id) 
                            if result not in exclude:  
                                vertices.append((x-min_coords[0],-(z-min_coords[2]),y-min_coords[1]))
                                # 将字符串id转换为相应的数字id
                                ids.append(id)
                    except:
                        pass

        id_map=register_blocks(list(set(ids)))
    else:
        IDCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/id_map.pkl"
        with open(IDCachePath, 'rb') as f:
            vertices,ids,id_map = pickle.load(f)
        id_map=registered_blocks(id_map)

    # 将顶点和顶点索引添加到网格中
    mesh.from_pydata(vertices, [], [])
    #给予顶点id
    for i, item in enumerate(obj.data.attributes['blockid'].data):
        item.value=id_map[ids[i]]
        #print(item.value)
    #群系上色
    for i, item in enumerate(obj.data.attributes['biome'].data):
        item.color[:]=(0.149,0.660,0.10,0.00)
    # 设置顶点索引
    mesh.update()
    
    # 检查是否有节点修改器，如果没有则添加一个
    has_nodes_modifier = False
    for modifier in obj.modifiers:
        if modifier.type == 'NODES':
            has_nodes_modifier = True
            break
    if not has_nodes_modifier:
        obj.modifiers.new(name="SchemToBlocks",type="NODES")
    nodes_modifier=obj.modifiers[0]
    
    # 复制 SchemToBlocks 节点组并重命名为 CollectionName
    try:
        original_node_group = bpy.data.node_groups['SchemToBlocks']
        new_node_group = original_node_group.copy()
        new_node_group.name = collection_name
    except KeyError:
        print("error")
    #设置几何节点        
    nodes_modifier.node_group = bpy.data.node_groups[collection_name]
    bpy.data.node_groups[collection_name].nodes["集合信息"].inputs[0].default_value = collection
    nodes_modifier.show_viewport = True    

    

def schem_chunk(level,chunks,x_list,filename="schem",position=(0,0,0)):
    # 获取最小和最大坐标
    min_coords = chunks[0]
    max_coords = chunks[1]
    current_frame = bpy.context.scene.frame_current

    # 创建顶点和顶点索引
    vertices = []
    ids = []  # 存储顶点id

    # 遍历范围内所有的坐标
    for x in range(x_list[current_frame][0], x_list[current_frame][1]):
        for y in range(min_coords[1], max_coords[1] + 1):
            for z in range(min_coords[2], max_coords[2] + 1):
                try:
                    # 获取坐标处的方块       
                    blc =level.get_version_block(x, y, z, "main",("java", (1, 20, 4)))
                    id =blc[0]
                    if isinstance(id,amulet.api.block.Block):
                        id = str(id).replace('"', '')
                        result = remove_brackets(id) 
                        if result not in exclude:  
                            vertices.append((x-min_coords[0],-(z-min_coords[2]),y-min_coords[1]))
                            # 将字符串id转换为相应的数字id
                            ids.append(id)
                except:
                    pass

    id_map=register_blocks(list(set(ids)))

    IDCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/chunk{}.pkl".format(current_frame)
    with open(IDCachePath, 'wb') as f:
        pickle.dump((vertices,ids,id_map), f)
    
    

#流体
def schem_liquid(level,chunks, filename="liquid", position=(0, 0, 0)):
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict = {}

    water_levels = {
        "minecraft:water[level=0]": 16,
        "minecraft:water[level=1]": 14,
        "minecraft:water[level=2]": 12,
        "minecraft:water[level=3]": 10,
        "minecraft:water[level=4]": 8,
        "minecraft:water[level=5]": 6,
        "minecraft:water[level=6]": 4,
        "minecraft:water[level=7]": 2,
        #流下的水,该级别等于它上方不会流下的水的级别加上8。
        "minecraft:water[level=8]": 16,
        "minecraft:water[level=9]": 16,
        "minecraft:water[level=10]": 16,
        "minecraft:water[level=11]": 16,
        "minecraft:water[level=12]": 16,
        "minecraft:water[level=13]": 16,
        "minecraft:water[level=14]": 16,
        "minecraft:water[level=15]": 16,
    }
    # 定义一个元组，存储六个方向的偏移量，按照 上下北南东西 的顺序排序
    offsets = ((0, 0, -1),  # 东
                (0, 0, 1),  # 西
                (-1, 0, 0),  # 北
                (1, 0, 0),  # 南
                (0, -1, 0),  # 下
                (0, 1, 0))  # 上
    min_coord = chunks[0]  # 最小坐标
    max_coord = chunks[1]  # 最大坐标

    # 遍历 x、y、z 三个轴上的所有坐标
    for x in range(min_coord[0], max_coord[0] + 1):
        for y in range(min_coord[1], max_coord[1] + 1):
            for z in range(min_coord[2], max_coord[2] + 1):
                # 获取坐标处的方块
                id = level.get_block(x, y, z, "main")
                if isinstance(id,amulet.api.block.Block):
                    if id.extra_blocks !=():
                        id=str(level.translation_manager.get_("java", (1, 20, 4)).block.from_universal(id.extra_blocks[0])[0]).replace('"', '')
                    else:
                        id =str(level.translation_manager.get_version("java", (1, 20, 4)).block.from_universal(id)[0]).replace('"', '')
                    
                    result = remove_brackets(id) 
                    if result in liquid:
                        # 使用列表推导式生成相邻坐标
                        adjacent_coords = [(x + offset[0], y + offset[1], z + offset[2]) for offset in offsets]
                        # 使用 any 函数判断是否有流体方块
                        #最少面
                        #has_air = [adj_coord not in d or d[adj_coord].split('[')[0] =="minecraft:air" for adj_coord in adjacent_coords]

                        #体积水
                        #has_air = [adj_coord not in d or (d[adj_coord].split('[')[0] not in liquid and d[adj_coord].split('[')[0] not in sea_plants) for adj_coord in adjacent_coords]
                        # 判断是否有空气方块
                        has_air = [True] * 6  # 默认为 True
                        for i, adj_coord in enumerate(adjacent_coords):
                            name = level.get_block(adj_coord[0], adj_coord[1], adj_coord[2], "main")
                            if isinstance(name,amulet.api.block.Block):
                                if name.extra_blocks !=():
                                    extra_blocks=str(level.translation_manager.get_version("java", (1, 20, 4)).block.from_universal(name.extra_blocks[0])[0]).replace('"', '')
                                    # 找到等号的位置
                                    equal_index = extra_blocks.find('[')

                                    # 分离出 water 和 level=0
                                    if equal_index != -1:
                                        extra_blocks = extra_blocks[:equal_index]
                                    if extra_blocks in liquid:
                                        has_air[i] = False
                                        continue
                                name =str(level.translation_manager.get_version("java", (1, 20, 4)).block.from_universal(name)[0]).replace('"', '')
                                # 找到等号的位置
                                equal_index = name.find('[')

                                # 分离出 water 和 level=0
                                if equal_index != -1:
                                    name = name[:equal_index]
                                    #level = name[equal_index:]
                                # 如果 parent 是 "block/cube"，将 has_air 设为 False
                                if name in liquid:
                                    has_air[i] = False

            

                        # 将 has_air 中的值按照 东西北南上下 的顺序排列
                        has_air = [has_air[2], has_air[3], has_air[0], has_air[1], has_air[5], has_air[4]]
                        key=[x-min_coord[0],z-min_coord[2],y-min_coord[1]]
                        # 计算哪些面需要生成
                        faces_to_generate = [i for i, has_air_face in enumerate(has_air) if has_air_face]

                        if faces_to_generate:
                            result = remove_brackets(id)
                            if result in sea_plants:
                                result="minecraft:water"
                                id ="minecraft:water[level=0]"
                            if result in liquid:
                                water_level = water_levels.get(id, 0)
                                z_offset = water_level / 16 
                                key = (key[0], -key[1]-1, key[2])
                                for face_index in faces_to_generate:
                                    if face_index == 5:
                                        coords = np.array([
                                            (key[0], key[1], key[2]), #0
                                            (key[0]+1, key[1], key[2]), #1
                                            (key[0]+1, key[1]+1, key[2]), #2
                                            (key[0], key[1]+1, key[2]) #3
                                        ])
                                        for coord in coords:
                                            coord = tuple(coord)
                                            if coord not in vertices_dict:
                                                vertices_dict[coord] = len(vertices_dict)
                                                vertices.append(coord)
                                        faces.append([
                                            vertices_dict[tuple(coords[0])],
                                            vertices_dict[tuple(coords[1])],
                                            vertices_dict[tuple(coords[2])],
                                            vertices_dict[tuple(coords[3])]
                                        ])
                                    elif face_index == 0:
                                        coords = np.array([
                                            (key[0], key[1]+1, key[2]), #3
                                            (key[0], key[1]+1, key[2]+z_offset),#7
                                            (key[0], key[1], key[2]+z_offset), #4
                                            (key[0], key[1], key[2]) #0
                                        ])
                                        for coord in coords:
                                            coord = tuple(coord)
                                            if coord not in vertices_dict:
                                                vertices_dict[coord] = len(vertices_dict)
                                                vertices.append(coord)
                                        faces.append([
                                            vertices_dict[tuple(coords[0])],
                                            vertices_dict[tuple(coords[1])],
                                            vertices_dict[tuple(coords[2])],
                                            vertices_dict[tuple(coords[3])]
                                        ])
                                    elif face_index == 3:
                                        coords = np.array([
                                            (key[0], key[1], key[2]), #0
                                            (key[0], key[1], key[2]+z_offset), #4
                                            (key[0]+1, key[1], key[2]+z_offset), #5
                                            (key[0]+1, key[1], key[2]) #1
                                        ])
                                        for coord in coords:
                                            coord = tuple(coord)
                                            if coord not in vertices_dict:
                                                vertices_dict[coord] = len(vertices_dict)
                                                vertices.append(coord)
                                        faces.append([
                                            vertices_dict[tuple(coords[0])],
                                            vertices_dict[tuple(coords[1])],
                                            vertices_dict[tuple(coords[2])],
                                            vertices_dict[tuple(coords[3])]
                                        ])
                                    elif face_index == 1:
                                        coords = np.array([
                                            (key[0]+1, key[1], key[2]), #1
                                            (key[0]+1, key[1], key[2]+z_offset), #5
                                            (key[0]+1, key[1]+1, key[2]+z_offset), #6
                                            (key[0]+1, key[1]+1, key[2]) #2
                                        ])
                                        for coord in coords:
                                            coord = tuple(coord)
                                            if coord not in vertices_dict:
                                                vertices_dict[coord] = len(vertices_dict)
                                                vertices.append(coord)
                                        faces.append([
                                            vertices_dict[tuple(coords[0])],
                                            vertices_dict[tuple(coords[1])],
                                            vertices_dict[tuple(coords[2])],
                                            vertices_dict[tuple(coords[3])]
                                        ])
                                    elif face_index == 2:
                                        coords = np.array([
                                            (key[0]+1, key[1]+1, key[2]), #2
                                            (key[0], key[1]+1, key[2]), #3
                                            (key[0], key[1]+1, key[2]+z_offset),#7
                                            (key[0]+1, key[1]+1, key[2]+z_offset)#5
                                        ])
                                        for coord in coords:
                                            coord = tuple(coord)
                                            if coord not in vertices_dict:
                                                vertices_dict[coord] = len(vertices_dict)
                                                vertices.append(coord)
                                        faces.append([
                                            vertices_dict[tuple(coords[0])],
                                            vertices_dict[tuple(coords[1])],
                                            vertices_dict[tuple(coords[2])],
                                            vertices_dict[tuple(coords[3])]
                                        ])
                                    elif face_index == 4:
                                        coords = np.array([
                                            (key[0]+1, key[1]+1, key[2]+z_offset),#6
                                            (key[0]+1, key[1], key[2]+z_offset), #5
                                            (key[0], key[1], key[2]+z_offset), #4
                                            (key[0], key[1]+1, key[2]+z_offset)#7
                                        ])
                                        for coord in coords:
                                            coord = tuple(coord)
                                            if coord not in vertices_dict:
                                                vertices_dict[coord] = len(vertices_dict)
                                                vertices.append(coord)
                                        faces.append([
                                            vertices_dict[tuple(coords[0])],
                                            vertices_dict[tuple(coords[1])],
                                            vertices_dict[tuple(coords[2])],
                                            vertices_dict[tuple(coords[3])]
                                        ])

    collection = bpy.context.collection
    mesh_name = filename
    mesh = create_mesh(mesh_name)
    obj = add_mesh_to_collection(collection, mesh)
    obj.location = position

    bm = bmesh.new()
    for v in vertices:
        bm.verts.new(v)
    bm.verts.ensure_lookup_table()

    uv_layer = bm.loops.layers.uv.new()  # Add UV layer

    for face_index, f in enumerate(faces):
        verts_list=[]
        for i in f:
            vert =bm.verts[i]
            if vert not in verts_list:
                verts_list.append(vert)
        existing_face = bm.faces.get(verts_list)
        if existing_face is not None:
            face = existing_face
        elif len(verts_list)>2:
            face = bm.faces.new(verts_list)
        else:
            continue


    bm.faces.ensure_lookup_table()

    bm.to_mesh(mesh)
    bm.free()

