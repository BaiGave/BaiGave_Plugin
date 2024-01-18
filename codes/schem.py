import bpy
import bmesh
from .model import create_mesh,add_mesh_to_collection,get_or_create_material,set_uv
from .blockstates import blockstates
import amulet
from .classification_files.block_type import liquid,exclude,sea_plants
import numpy as np
import os
from .block import block
from .blockstates import get_model
from .functions.mesh_to_mc import create_or_clear_collection

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


def schem(level,chunks,filename="schem",position=(0,0,0)):
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
    id_map = {}  # 用于将字符串id映射到数字的字典
    next_id = 0  # 初始化 next_id
    if not collection.objects:
        filename=str(next_id)+"#"+str("minecraft:air")
        textures,elements,rotation,_ =get_model("minecraft:air")
        position = [0, 0, 0]
        has_air = [True, True, True, True, True, True]
        bloc=block(textures, elements, position,rotation, filename, has_air,collection)
        bloc.data.attributes.new(name='blockname', type="STRING", domain="FACE")
        for i, item in enumerate(bloc.data.attributes['blockname'].data):
            item.value="minecraft:air"
        id_map["minecraft:air"] = next_id
        next_id += 1
    elif collection.objects:
        # 遍历集合中的每个物体
        for ob in collection.objects:
            # 假设属性名称为 'blockname'，如果属性存在
            if 'blockname' in ob.data.attributes:
                # 获取属性值
                try:
                    attr_value = ob.data.attributes['blockname'].data[0].value
                except:
                    attr_value = "minecraft:air"
                # 获取物体ID（假设ID是以#分隔的字符串的第一个部分）
                obj_id = ob.name.split('#')[0]
                # 将字符串类型的ID转换为整数
                try:
                    obj_id_int = int(obj_id)
                    # 找到最大ID
                    if obj_id_int > next_id:
                        next_id = obj_id_int
                except ValueError:
                    pass
                # 将 ID 与属性值关联起来并存储到字典中
                id_map[attr_value] = int(obj_id)
            
        next_id =next_id+1
    
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
                            # 将字符串id映射到数字，如果id已经有对应的数字id，则使用现有的数字id
                            if id not in id_map:
                                filename=str(next_id)+"#"+str(id)
                                textures,elements,rotation,_ =get_model(id)
                                position = [0, 0, 0]
                                has_air = [True, True, True, True, True, True]
                                bloc=block(textures, elements, position,rotation, filename, has_air,collection)
                                bloc.data.attributes.new(name='blockname', type="STRING", domain="FACE")
                                for i, item in enumerate(bloc.data.attributes['blockname'].data):
                                    item.value=id
                                id_map[id] = next_id
                                next_id += 1

                            vertices.append((x-min_coords[0],-(z-min_coords[2]),y-min_coords[1]))
                            # 将字符串id转换为相应的数字id
                            ids.append(id_map[id])
                except:
                    pass

        
    # 将顶点和顶点索引添加到网格中
    mesh.from_pydata(vertices, [], [])
    for i, item in enumerate(obj.data.attributes['blockid'].data):
        item.value=ids[i]
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

    

def schem_chunk(level,chunks,i,filename="Schemetics",position=(0,0,0)):
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}

    for x in range(i[0]*16, i[0]*16+16):
        for y in range(chunks[0][1], chunks[1][1]):
            for z in range(i[1]*16, i[1]*16+16):
                # 获取坐标处的方块
                id = level.get_block(x, y, z, "main")
                if isinstance(id,amulet.api.block.Block):
                    id =str(level.translation_manager.get_version("java", (1, 20, 4)).block.from_universal(id)[0]).replace('"', '')
                    result = remove_brackets(id) 
                    if result not in exclude:  
                        vertices,faces,direction,texture_list,uv_list,uv_rotation_list = blockstates((x,y,z),chunks, level, vertices, faces, direction, texture_list, uv_list, uv_rotation_list, vertices_dict)
                   
    collection = bpy.context.collection
    mesh_name = filename
    mesh = create_mesh(mesh_name)
    obj = add_mesh_to_collection(collection, mesh)
    obj.location = position


    bm = bmesh.new()
    for v in vertices:
        bm.verts.new(v)
    bm.verts.ensure_lookup_table()

    uv_layer = bm.loops.layers.uv.new()  # 添加UV图层
    
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

        mat = get_or_create_material(texture_list[face_index],filename)
        mat.blend_method = 'CLIP'
        mat.shadow_method = 'CLIP'
        if mat.name not in obj.data.materials:
            obj.data.materials.append(mat)

        face.material_index = obj.data.materials.find(mat.name)

        if uv_list[face_index] == "Auto":
            for loop in face.loops:
                vertex = loop.vert
                uv = (vertex.co.y, vertex.co.z) if direction[face_index] in ['west', 'east'] \
                    else (vertex.co.x, vertex.co.z) if direction[face_index] in ['north', 'south'] \
                    else (vertex.co.x, vertex.co.y)
                loop[uv_layer].uv = uv
        else:
            rotation = uv_rotation_list[face_index]
            uv_coords = uv_list[face_index]
            for i, loop in enumerate(face.loops):
                #set_uv这个方法有问题 在使用stripped_oak_wood 方块时出错
                loop[uv_layer].uv = set_uv(uv_coords, i, rotation)

    bm.faces.ensure_lookup_table()
    bm.to_mesh(mesh)
    bm.free()


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

