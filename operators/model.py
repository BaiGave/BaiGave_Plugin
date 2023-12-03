import bpy
import numpy as np
from .shader_type import Type1,Type2,Type3
from .functions import get_frametime,is_file_path_exists,get_file_path
from mathutils import Matrix
from mathutils import Vector

import math
def create_node_material(texture_paths, mat_name,filename):
    mat_name = mat_name.replace("block/", "")
    if ':' not in mat_name:
        mat_name = "minecraft:" + mat_name
     # 尝试找到名为mat_name的材质
    mat = bpy.data.materials.get(mat_name)
    if mat is not None:
        # 找到了材质，将其重命名
        mat.name = mat_name
    elif mat_name == "minecraft:missing":
        #透明材质
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        for node in mat.node_tree.nodes:
            mat.node_tree.nodes.remove(node)
        shader_node = mat.node_tree.nodes.new('ShaderNodeBsdfTransparent')
        output_node = mat.node_tree.nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(shader_node.outputs['BSDF'], output_node.inputs['Surface'])
    else:
        if mat_name in Type1:
            shader_name = "树叶/草+灰度图着色器"
            # 导入shader
            shader = bpy.data.materials.get(shader_name)
            if shader is None:
                path = __file__.rsplit(
                    "\\", 1)[0]+"\\Material.blend"
                with bpy.data.libraries.load(path) as (data_from, data_to):
                    if shader_name in data_from.materials:
                        data_to.materials = [shader_name]
                # 获取shader
                shader = bpy.data.materials.get(shader_name)
            # 复制 shader，并将其重命名为 mat_name
            mat = shader.copy()
            mat.name = mat_name
            # 设置图像纹理节点的图片路径
            for node in mat.node_tree.nodes:
                if node.name =="色图":
                    node.image = bpy.data.images.get(filename+"_colormap")
                elif node.name == "默认图片":
                    node.image = bpy.data.images.load(texture_paths[0])
        elif mat_name in Type2:
            shader_name = "灰度图着色器"
            # 导入shader
            shader = bpy.data.materials.get(shader_name)
            if shader is None:
                path = __file__.rsplit(
                    "\\", 1)[0]+"\\Material.blend"
                with bpy.data.libraries.load(path) as (data_from, data_to):
                    if shader_name in data_from.materials:
                        data_to.materials = [shader_name]
                # 获取shader
                shader = bpy.data.materials.get(shader_name)
            # 复制 shader，并将其重命名为 mat_name
            mat = shader.copy()
            mat.name = mat_name
            # 设置图像纹理节点的图片路径
            for node in mat.node_tree.nodes:
                if node.name =="色图":
                    node.image = bpy.data.images.get(filename+"_colormap")
                elif node.name == "默认图片":
                    node.image = bpy.data.images.load(texture_paths[0])
        elif mat_name in Type3:
            image=bpy.data.images.load(texture_paths[0])
            # 获取图像的边长大小
            width = image.size[0]  # 宽度
            height = image.size[1]  # 高度
            if width/height != 1 and is_file_path_exists(texture_paths[0]+".mcmeta"):
                shader_name = "动态材质+树叶/草着色器"
                # 导入shader
                shader = bpy.data.materials.get(shader_name)
                if shader is None:
                    path = __file__.rsplit(
                        "\\", 1)[0]+"\\Material.blend"
                    with bpy.data.libraries.load(path) as (data_from, data_to):
                        if shader_name in data_from.materials:
                            data_to.materials = [shader_name]
                    # 获取shader
                    shader = bpy.data.materials.get(shader_name)
                # 复制 shader，并将其重命名为 mat_name
                mat = shader.copy()
                mat.name = mat_name
                
                # 设置图像纹理节点的图片路径
                for node in mat.node_tree.nodes:
                    if node.name == "默认图片":
                        node.image = image
                    elif node.name =="行":
                        node.outputs[0].default_value = height/width
                    elif node.name =="值":
                        node.outputs[0].default_value = get_frametime(texture_paths[0]+".mcmeta")
            else:   
                shader_name = "树叶/草着色器"
                # 导入shader
                shader = bpy.data.materials.get(shader_name)
                if shader is None:
                    path = __file__.rsplit(
                        "\\", 1)[0]+"\\Material.blend"
                    with bpy.data.libraries.load(path) as (data_from, data_to):
                        if shader_name in data_from.materials:
                            data_to.materials = [shader_name]
                    # 获取shader
                    shader = bpy.data.materials.get(shader_name)
                # 复制 shader，并将其重命名为 mat_name
                mat = shader.copy()
                mat.name = mat_name
                # 设置图像纹理节点的图片路径
                for node in mat.node_tree.nodes:
                    if node.name == "默认图片":
                        node.image = image
        elif is_file_path_exists(texture_paths[0].replace(".png","")+"_n.png") and is_file_path_exists(texture_paths[0].replace(".png","")+"_s.png"):
            image=bpy.data.images.load(texture_paths[0])
            image_n=bpy.data.images.load(texture_paths[0].replace(".png","")+"_n.png")
            image_s=bpy.data.images.load(texture_paths[0].replace(".png","")+"_s.png")
            shader_name = "PBR着色器"
            # 导入shader
            shader = bpy.data.materials.get(shader_name)
            if shader is None:
                path = __file__.rsplit(
                    "\\", 1)[0]+"\\Material.blend"
                with bpy.data.libraries.load(path) as (data_from, data_to):
                    if shader_name in data_from.materials:
                        data_to.materials = [shader_name]
                # 获取shader
                shader = bpy.data.materials.get(shader_name)
            # 复制 shader，并将其重命名为 mat_name
            mat = shader.copy()
            mat.name = mat_name
            # 设置图像纹理节点的图片路径
            for node in mat.node_tree.nodes:
                if node.name == "默认图片":
                    node.image = image
                elif node.name == "默认图片_s":
                    node.image = image_s
                elif node.name == "默认图片_n":
                    node.image = image_n
        elif not is_file_path_exists(texture_paths[0].replace(".png","")+"_n.png") and is_file_path_exists(texture_paths[0].replace(".png","")+"_s.png"):
            image=bpy.data.images.load(texture_paths[0])
            image_s=bpy.data.images.load(texture_paths[0].replace(".png","")+"_s.png")
            shader_name = "PBR着色器(仅s)"
            # 导入shader
            shader = bpy.data.materials.get(shader_name)
            if shader is None:
                path = __file__.rsplit(
                    "\\", 1)[0]+"\\Material.blend"
                with bpy.data.libraries.load(path) as (data_from, data_to):
                    if shader_name in data_from.materials:
                        data_to.materials = [shader_name]
                # 获取shader
                shader = bpy.data.materials.get(shader_name)
            # 复制 shader，并将其重命名为 mat_name
            mat = shader.copy()
            mat.name = mat_name
            # 设置图像纹理节点的图片路径
            for node in mat.node_tree.nodes:
                if node.name == "默认图片":
                    node.image = image
                elif node.name == "默认图片_s":
                    node.image = image_s
        elif is_file_path_exists(texture_paths[0].replace(".png","")+"_n.png") and not is_file_path_exists(texture_paths[0].replace(".png","")+"_s.png"):
            image=bpy.data.images.load(texture_paths[0])
            image_n=bpy.data.images.load(texture_paths[0].replace(".png","")+"_n.png")
            shader_name = "PBR着色器(仅n)"
            # 导入shader
            shader = bpy.data.materials.get(shader_name)
            if shader is None:
                path = __file__.rsplit(
                    "\\", 1)[0]+"\\Material.blend"
                with bpy.data.libraries.load(path) as (data_from, data_to):
                    if shader_name in data_from.materials:
                        data_to.materials = [shader_name]
                # 获取shader
                shader = bpy.data.materials.get(shader_name)
            # 复制 shader，并将其重命名为 mat_name
            mat = shader.copy()
            mat.name = mat_name
            # 设置图像纹理节点的图片路径
            for node in mat.node_tree.nodes:
                if node.name == "默认图片":
                    node.image = image
                elif node.name == "默认图片_n":
                    node.image = image_n
        elif is_file_path_exists(texture_paths[0].replace(".png","")+"_e.png"):
            image=bpy.data.images.load(texture_paths[0])
            image_e=bpy.data.images.load(texture_paths[0].replace(".png","")+"_e.png")
            shader_name = "自发光着色器"
            # 导入shader
            shader = bpy.data.materials.get(shader_name)
            if shader is None:
                path = __file__.rsplit(
                    "\\", 1)[0]+"\\Material.blend"
                with bpy.data.libraries.load(path) as (data_from, data_to):
                    if shader_name in data_from.materials:
                        data_to.materials = [shader_name]
                # 获取shader
                shader = bpy.data.materials.get(shader_name)
            # 复制 shader，并将其重命名为 mat_name
            mat = shader.copy()
            mat.name = mat_name
            # 设置图像纹理节点的图片路径
            for node in mat.node_tree.nodes:
                if node.name == "默认图片":
                    node.image = image
                elif node.name == "默认图片_e":
                    node.image = image_e
        else:
            image=bpy.data.images.load(texture_paths[0])
            # 获取图像的边长大小
            width = image.size[0]  # 宽度
            height = image.size[1]  # 高度
            if width/height != 1 and is_file_path_exists(texture_paths[0]+".mcmeta"):
                shader_name = "动态材质"
                # 导入shader
                shader = bpy.data.materials.get(shader_name)
                if shader is None:
                    path = __file__.rsplit(
                        "\\", 1)[0]+"\\Material.blend"
                    with bpy.data.libraries.load(path) as (data_from, data_to):
                        if shader_name in data_from.materials:
                            data_to.materials = [shader_name]
                    # 获取shader
                    shader = bpy.data.materials.get(shader_name)
                # 复制 shader，并将其重命名为 mat_name
                mat = shader.copy()
                mat.name = mat_name
                # 设置图像纹理节点的图片路径
                for node in mat.node_tree.nodes:
                    if node.name == "默认图片":
                        node.image = image
                    elif node.name =="行":
                        node.outputs[0].default_value = height/width
                    elif node.name =="值":
                        node.outputs[0].default_value = get_frametime(texture_paths[0]+".mcmeta")
            else:
                shader_name = "默认着色器"
                # 导入shader
                shader = bpy.data.materials.get(shader_name)
                if shader is None:
                    path = __file__.rsplit(
                        "\\", 1)[0]+"\\Material.blend"
                    with bpy.data.libraries.load(path) as (data_from, data_to):
                        if shader_name in data_from.materials:
                            data_to.materials = [shader_name]
                    # 获取shader
                    shader = bpy.data.materials.get(shader_name)
                # 复制 shader，并将其重命名为 mat_name
                mat = shader.copy()
                mat.name = mat_name
                # 设置图像纹理节点的图片路径
                for node in mat.node_tree.nodes:
                    if node.name == "默认图片":
                        node.image = image

    return mat


def rot(origin, position, coords,rotation= [0,0,0], rotation_matrix=None):
    scale_factor = 1/16
    if rotation_matrix is not None:
        coords = [tuple(np.dot(rotation_matrix, (point - origin)) + origin) for point in coords]

    if rotation != [0, 0, 0] or rotation is not None:
        center = Vector((8, 8, 8))
        # 将原点平移到方块的中心
        coords = [Vector(point) - center for point in coords]
        # 构建旋转矩阵
        rotation_matrix = Matrix.Rotation(math.radians(rotation[2]), 3, 'Z') @ \
                        Matrix.Rotation(math.radians(rotation[1]), 3, 'Y') @ \
                        Matrix.Rotation(math.radians(rotation[0]+90), 3, 'X')

        # 对坐标列表中的每个点应用旋转矩阵
        coords = [tuple(rotation_matrix @ Vector(point)) for point in coords]

        # 将坐标还原回原始坐标
        coords = [tuple(Vector(point) + center) for point in coords]
    else:
        rotation_matrix_x = np.array([
            [1, 0, 0],
            [0, 0, -1],
            [0, 1, 0]
        ])
        
        coords = [tuple(np.dot(rotation_matrix_x, point)) for point in coords]


    coords = [tuple(np.array(point)*scale_factor) for point in coords]       
    
    if position is not None:
        coords = [(point[0] + position[0], point[1] - position[1]-1, point[2] + position[2]) for point in coords]
    return coords
def fac(origin, position, element, vertices, faces, vertices_dict, directions, has_air, rotation,rotation_matrix=None):
    from_coord = np.array(element['from'])
    to_coord = np.array(element['to'])
    coords = None
    directions_map = {
        'south': abs(from_coord[2] - to_coord[2]) <= 0.01,
        'up': abs(from_coord[1] - to_coord[1]) <= 0.01,
        'east': abs(from_coord[0] - to_coord[0]) <= 0.01
    }

    for direction, condition in directions_map.items():
        if condition:
            if direction == 'up':
                coords = np.array([
                    (from_coord[0], from_coord[1], from_coord[2]),
                    (to_coord[0], from_coord[1], from_coord[2]),
                    (to_coord[0], to_coord[1], to_coord[2]),
                    (from_coord[0], to_coord[1], to_coord[2])
                ])
            else:
                coords = np.array([
                    (from_coord[0], from_coord[1], from_coord[2]),
                    (to_coord[0], from_coord[1], to_coord[2]),
                    (to_coord[0], to_coord[1], to_coord[2]),
                    (from_coord[0], to_coord[1], from_coord[2])
                ])
            coords = rot(origin, position, coords,rotation, rotation_matrix)
            for coord in coords:
                if coord not in vertices_dict:
                    vertices_dict[coord] = len(vertices_dict)
                    vertices.append(coord)
            
            if direction == 'up':
                faces.append([
                    vertices_dict[coords[0]],
                    vertices_dict[coords[1]],
                    vertices_dict[coords[2]],
                    vertices_dict[coords[3]]
                ])
            else:
                faces.append([
                    vertices_dict[coords[2]],
                    vertices_dict[coords[3]],
                    vertices_dict[coords[0]],
                    vertices_dict[coords[1]]
                ])

            directions.append(direction)
            return

    face_visibility = {
        "down": True,
        "up": True,
        "north": True,
        "south": True,
        "west": True,
        "east": True
    }

    for face_name, face_info in element['faces'].items():
        if face_name in ["down", "up", "north", "south", "west", "east"]:
            index = ["east", "west", "north", "south", "up", "down"].index(face_name)
            if not has_air[index]:
                cullface = face_info.get("cullface")
                face_visibility[cullface] = False
    
    coord_patterns = {
        "down": [
            (from_coord[0], from_coord[1], to_coord[2]), 
            (to_coord[0], from_coord[1], to_coord[2]), 
            (from_coord[0], from_coord[1], from_coord[2]), 
            (to_coord[0], from_coord[1], from_coord[2])
        ],
        "up": [
            (from_coord[0], to_coord[1], to_coord[2]), 
            (to_coord[0], to_coord[1], to_coord[2]), 
            (from_coord[0], to_coord[1], from_coord[2]), 
            (to_coord[0], to_coord[1], from_coord[2])
        ],
        "east": [
            (from_coord[0], from_coord[1], from_coord[2]),
            (from_coord[0], from_coord[1], to_coord[2]),
            (from_coord[0], to_coord[1], from_coord[2]),
            (from_coord[0], to_coord[1], to_coord[2])
        ],
        "west": [
            (to_coord[0], from_coord[1], from_coord[2]),
            (to_coord[0], from_coord[1], to_coord[2]),
            (to_coord[0], to_coord[1], from_coord[2]),
            (to_coord[0], to_coord[1], to_coord[2])
        ],
        "south": [
            (to_coord[0], from_coord[1], to_coord[2]),
            (from_coord[0], from_coord[1], to_coord[2]),
            (to_coord[0], to_coord[1], to_coord[2]),
            (from_coord[0], to_coord[1], to_coord[2])
        ],
        "north": [
            (from_coord[0], from_coord[1], from_coord[2]),
            (to_coord[0], from_coord[1], from_coord[2]),
            (from_coord[0], to_coord[1], from_coord[2]),
            (to_coord[0], to_coord[1], from_coord[2])
        ]
    }
    for face_direction, face_visible in face_visibility.items():
        if face_visible and face_direction in element['faces']:
            coords = coord_patterns[face_direction]
            coords = rot(origin, position, coords,rotation, rotation_matrix)
            for coord in coords:
                if coord not in vertices_dict:
                    vertices_dict[coord] = len(vertices_dict)
                    vertices.append(coord)
            faces.append([
                vertices_dict[coords[3]],
                vertices_dict[coords[2]],
                vertices_dict[coords[0]],
                vertices_dict[coords[1]]
            ])
            directions.append(face_direction)

def extract_vertices(element, has_air, vertices, faces, vertices_dict, position,rotation):
    directions = []
    rotation_matrix = None
    origin = None
    angle = 0.0
    axis = ""
    
    if 'rotation' in element:
        origin = np.array(element['rotation']['origin'])
        angle = np.radians(element['rotation']['angle'])
        axis = element['rotation']['axis']

        # 对于所有的顶点坐标进行旋转和缩放
        if axis == 'x':
            rotation_matrix = np.array([
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)]
            ])
        elif axis == 'y':
            rotation_matrix = np.array([
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)]
            ])
        elif axis == 'z':
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1]
            ])
        else:
            raise ValueError('Invalid axis value')
        
        fac(origin, position, element, vertices, faces, vertices_dict, directions, has_air, rotation,rotation_matrix)
    else:
        fac((0, 0, 0), position, element, vertices, faces, vertices_dict, directions, has_air,rotation)

    return directions
        
def extract_vertices_from_elements(textures, elements, has_air, position=None,Rotation=None , vertices=[], faces=[], direction=[], texture_list=[], uv_list=[], uv_rotation_list=[], vertices_dict={}):
    v_from = set()
    v_to = set()
    directions = []
    for element in elements:
        if 'from' in element and 'to' in element:
            if tuple(element['from']) in v_from and tuple(element['to']) in v_to:
                element['from'][0] -= 0.01
                element['from'][1] -= 0.01
                element['from'][2] -= 0.01
                element['to'][0] += 0.01
                element['to'][1] += 0.01
                element['to'][2] += 0.01
            v_from.add(tuple(element['from']))
            v_to.add(tuple(element['to']))
            directions = extract_vertices(element, has_air, vertices, faces, vertices_dict, position,Rotation)
            for d in directions:
                direction.append(d)
                if d in element['faces']:
                    fac = element['faces'][d]
                    texture = fac.get('texture')
                    uv = fac.get('uv')
                    rotation = fac.get('rotation')
                    if texture is not None:
                        if texture.startswith('#'):
                            texture = texture[1:]
                            if texture == "missing":
                                pass
                            else:
                                try:
                                    texture = textures[texture]
                                except:
                                    texture = "missing"
                        else:
                            texture = f"block/{texture}"
                        texture_list.append(texture)
                    else:
                        texture_list.append('None')
                    if uv is not None:
                        uv_list.append(uv)
                    else:
                        uv_list.append('Auto')
                    if rotation is not None:
                        uv_rotation_list.append(rotation)
                    else:
                        uv_rotation_list.append(0)
                else:
                    texture_list.append('None')
                    uv_list.append('Auto')
                    uv_rotation_list.append(0)
    
    return vertices, faces, direction, texture_list, uv_list, uv_rotation_list

def create_mesh(mesh_name):
    # 使用bpy.data.meshes.new()创建一个新的网格
    mesh = bpy.data.meshes.new(mesh_name)
    # 向网格添加一个名为“UVMap”的UV图层
    mesh.uv_layers.new(name="UVMap")
    # 向网格添加一个名为“UVMap”的UV图层
    #mesh.uv_layers.new(name="UVMap_1")
    # 返回新创建的网格
    return mesh

def add_mesh_to_collection(collection, mesh):
    # 创建一个新的 Blender 对象，使用给定的网格数据和名称
    obj = bpy.data.objects.new(mesh.name, mesh)
    # 将新对象添加到给定的对象集合中
    collection.objects.link(obj)
    # 返回新创建的对象
    return obj

def get_or_create_material(texture,filename):
    mat_name = ""
    mat_name = f"{texture}"
    if mat_name not in bpy.data.materials:
        mat = create_node_material([get_file_path(texture, "t")], mat_name,filename)

    else:
        mat = bpy.data.materials[mat_name]

    return mat

def set_uv(uv_coords, i, rotation):
    uv_conversions = {
        0: [(uv_coords[0]/16, 1-uv_coords[1]/16), (uv_coords[2]/16, 1-uv_coords[1]/16), (uv_coords[2]/16, 1-uv_coords[3]/16), (uv_coords[0]/16, 1-uv_coords[3]/16)],
        90: [(uv_coords[2]/16, 1-uv_coords[1]/16), (uv_coords[2]/16, 1-uv_coords[3]/16), (uv_coords[0]/16, 1-uv_coords[3]/16), (uv_coords[0]/16, 1-uv_coords[1]/16)],
        180: [(uv_coords[2]/16, 1-uv_coords[3]/16), (uv_coords[0]/16, 1-uv_coords[3]/16), (uv_coords[0]/16, 1-uv_coords[1]/16), (uv_coords[2]/16, 1-uv_coords[1]/16)],
        270: [(uv_coords[0]/16, 1-uv_coords[3]/16), (uv_coords[0]/16, 1-uv_coords[1]/16), (uv_coords[2]/16, 1-uv_coords[1]/16), (uv_coords[2]/16, 1-uv_coords[3]/16)]
    }
    u, v = uv_conversions[rotation][i]
    return u, v
