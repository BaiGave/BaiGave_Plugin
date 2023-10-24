import bpy
import bmesh
from .model import create_mesh,add_mesh_to_collection,get_or_create_material,set_uv
from .cullblocks import CullBlocks
from .blockstates import blockstates

from .classification import flowers,leaves,liquid,exclude
import numpy as np

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


def schem_p(d, filename="", position=(0, 0, 0)):
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}

    for key, value in d.items():
        result = remove_brackets(value)
        if result in flowers:
            has_air = [True, True,True, True, True,True]
            vertices,faces,direction,texture_list,uv_list,uv_rotation_list = blockstates(key, value,has_air,vertices,faces,direction,texture_list,uv_list,uv_rotation_list,vertices_dict)
            
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
        existing_face = bm.faces.get([bm.verts[i] for i in f])
        if existing_face is not None:
            face = existing_face
        else:
            face = bm.faces.new([bm.verts[i] for i in f])

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
                loop[uv_layer].uv = set_uv(uv_coords, i, rotation)

    bm.faces.ensure_lookup_table()

    bm.to_mesh(mesh)
    bm.free()

def schem_leaves(d,filename="",position=(0,0,0)):
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}

    for key, value in d.items():
        result = remove_brackets(value)
        if result in leaves:
            has_air = [True, True,True, True, True,True]
            vertices,faces,direction,texture_list,uv_list,uv_rotation_list = blockstates(key, value,has_air,vertices,faces,direction,texture_list,uv_list,uv_rotation_list,vertices_dict)
            
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
        existing_face = bm.faces.get([bm.verts[i] for i in f])
        if existing_face is not None:
            face = existing_face
        else:
            face = bm.faces.new([bm.verts[i] for i in f])

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
                loop[uv_layer].uv = set_uv(uv_coords, i, rotation)

    bm.faces.ensure_lookup_table()

    bm.to_mesh(mesh)
    bm.free()

#流体
def schem_liquid(d, filename="", position=(0, 0, 0)):
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
    
    for key, value in d.items():
        # 定义一个元组，存储六个方向的偏移量，按照 上下北南东西 的顺序排序
        offsets = ((0, 1, 0),  # 东
                (0, -1, 0),  # 西
                (-1, 0, 0),  # 北
                (1, 0, 0),  # 南
                (0, 0, -1),  # 下
                (0, 0, 1))  # 上
        # 使用列表推导式生成相邻坐标
        adjacent_coords = [(key[0] + offset[0], key[1] + offset[1], key[2] + offset[2]) for offset in offsets]
        # 使用 any 函数判断是否有流体方块
        #最少面
        #has_air = [adj_coord not in d or d[adj_coord].split('[')[0] =="minecraft:air" for adj_coord in adjacent_coords]

        #体积水
        has_air = [adj_coord not in d or d[adj_coord].split('[')[0] not in liquid for adj_coord in adjacent_coords]

        # 将 has_air 中的值按照 东西北南上下 的顺序排列
        has_air = [has_air[2], has_air[3], has_air[0], has_air[1], has_air[5], has_air[4]]

        # 计算哪些面需要生成
        faces_to_generate = [i for i, has_air_face in enumerate(has_air) if has_air_face]

        if faces_to_generate:
            result = remove_brackets(value)
            if result in liquid:
                water_level = water_levels.get(value, 0)
                z_offset = water_level / 16 
                key = (key[0], key[1]-1, key[2])
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
        existing_face = bm.faces.get([bm.verts[i] for i in f])
        if existing_face is not None:
            face = existing_face
        else:
            face = bm.faces.new([bm.verts[i] for i in f])


    bm.faces.ensure_lookup_table()

    bm.to_mesh(mesh)
    bm.free()





def schem(d,filename="",position=(0,0,0)):
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}

    for key, value in d.items():
        result = remove_brackets(value)
        if result not in exclude:
            vertices,faces,direction,texture_list,uv_list,uv_rotation_list = CullBlocks(key, d,vertices,faces,direction,texture_list,uv_list,uv_rotation_list,vertices_dict)
            
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
        existing_face = bm.faces.get([bm.verts[i] for i in f])
        if existing_face is not None:
            face = existing_face
        else:
            face = bm.faces.new([bm.verts[i] for i in f])

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
                loop[uv_layer].uv = set_uv(uv_coords, i, rotation)

    bm.faces.ensure_lookup_table()
    bm.to_mesh(mesh)
    bm.free()


def schem_dirtgrass(d,filename="",position=(0,0,0)):
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}

    for key, value in d.items():
        result = remove_brackets(value)
        if result == "minecraft:dirt" or result == "minecraft:grass_block":
            vertices,faces,direction,texture_list,uv_list,uv_rotation_list = CullBlocks(key, d,vertices,faces,direction,texture_list,uv_list,uv_rotation_list,vertices_dict)
            
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
        existing_face = bm.faces.get([bm.verts[i] for i in f])
        if existing_face is not None:
            face = existing_face
        else:
            face = bm.faces.new([bm.verts[i] for i in f])

        mat = get_or_create_material(texture_list[face_index],filename)
        mat.blend_method = 'BLEND'
        mat.show_transparent_back = False
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
                loop[uv_layer].uv = set_uv(uv_coords, i, rotation)

    bm.faces.ensure_lookup_table()
    bm.to_mesh(mesh)
    bm.free()


def schem_deepstone(d,filename="",position=(0,0,0)):
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}

    for key, value in d.items():
        result = remove_brackets(value)
        if result == "minecraft:stone" or result == "minecraft:deepslate":
            vertices,faces,direction,texture_list,uv_list,uv_rotation_list = CullBlocks(key, d,vertices,faces,direction,texture_list,uv_list,uv_rotation_list,vertices_dict)
            
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
        existing_face = bm.faces.get([bm.verts[i] for i in f])
        if existing_face is not None:
            face = existing_face
        else:
            face = bm.faces.new([bm.verts[i] for i in f])

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
                loop[uv_layer].uv = set_uv(uv_coords, i, rotation)

    bm.faces.ensure_lookup_table()
    bm.to_mesh(mesh)
    bm.free()

def schem_sandgravel(d,filename="",position=(0,0,0)):
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}

    for key, value in d.items():
        result = remove_brackets(value)
        if result == "minecraft:sand" or result == "minecraft:gravel":
            vertices,faces,direction,texture_list,uv_list,uv_rotation_list = CullBlocks(key, d,vertices,faces,direction,texture_list,uv_list,uv_rotation_list,vertices_dict)
            
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
        existing_face = bm.faces.get([bm.verts[i] for i in f])
        if existing_face is not None:
            face = existing_face
        else:
            face = bm.faces.new([bm.verts[i] for i in f])

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
                loop[uv_layer].uv = set_uv(uv_coords, i, rotation)

    bm.faces.ensure_lookup_table()
    bm.to_mesh(mesh)
    bm.free()

def schem_snow(d,filename="",position=(0,0,0)):
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}

    for key, value in d.items():
        result = remove_brackets(value)
        if result == "minecraft:snow" or result == "minecraft:snow_block" or result == "minecraft:powder_snow":
            vertices,faces,direction,texture_list,uv_list,uv_rotation_list = CullBlocks(key, d,vertices,faces,direction,texture_list,uv_list,uv_rotation_list,vertices_dict)
            
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
        existing_face = bm.faces.get([bm.verts[i] for i in f])
        if existing_face is not None:
            face = existing_face
        else:
            face = bm.faces.new([bm.verts[i] for i in f])

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
                loop[uv_layer].uv = set_uv(uv_coords, i, rotation)

    bm.faces.ensure_lookup_table()
    bm.to_mesh(mesh)
    bm.free()