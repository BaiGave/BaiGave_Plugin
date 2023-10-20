import bpy
import numpy as np
from .shader_type import Type1,Type2,Type3


def create_node_material(texture_paths, mat_name,filename):
    mat_name = mat_name.replace("block/", "")  # 去除"block/"部分
     # 尝试找到名为mat_name的材质
    mat = bpy.data.materials.get(mat_name)
    if mat is not None:
        # 找到了材质，将其重命名
        mat.name = mat_name
    elif mat_name == "missing":
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
        elif mat_name not in Type3:
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
                    node.image = bpy.data.images.load(texture_paths[0])

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
                    node.image = bpy.data.images.load(texture_paths[0])

    return mat


def rot(origin, display, position, coords,rotation, rotation_matrix=None):
    scale_factor = 1/16
    if rotation_matrix is not None:
        coords = [tuple(np.dot(rotation_matrix, (point - origin)) + origin) for point in coords]

    if 'fixed' in display:
        display_rotation = display.get('fixed', {}).get('rotation', [0,0,0])

        
        rotation_matrix_x = np.array([
            [1, 0, 0],
            [0, np.cos(np.radians(display_rotation[0]+rotation[0])), -np.sin(np.radians(display_rotation[0]+rotation[0]))],
            [0, np.sin(np.radians(display_rotation[0]+rotation[0])), np.cos(np.radians(display_rotation[0]+rotation[0]))]
        ])

        rotation_matrix_y = np.array([
            [np.cos(np.radians(display_rotation[1]+rotation[1])), 0, np.sin(np.radians(display_rotation[1]+rotation[1]))],
            [0, 1, 0],
            [-np.sin(np.radians(display_rotation[1]+rotation[1])), 0, np.cos(np.radians(display_rotation[1]+rotation[1]))]
        ])

        rotation_matrix_z = np.array([
            [np.cos(np.radians(display_rotation[2]+rotation[2])), -np.sin(np.radians(display_rotation[2]+rotation[2])), 0],
            [np.sin(np.radians(display_rotation[2]+rotation[2])), np.cos(np.radians(display_rotation[2]+rotation[2])), 0],
            [0, 0, 1]
        ])
        
        rotation_matrix = np.dot(np.dot(rotation_matrix_x, rotation_matrix_z), rotation_matrix_y)

        if rotation_matrix is not None:
            coords = [tuple(np.dot(rotation_matrix, point)) for point in coords]

        rotation_matrix_x = np.array([
            [1, 0, 0],
            [0, 0, -1],
            [0, 1, 0]
        ])
        
        coords = [tuple(np.dot(rotation_matrix_x, point)) for point in coords]
    elif rotation != [0, 0, 0] or rotation is not None:
        # 计算旋转矩阵
        center = np.array([8, 8, 8])  # 旋转中心
        rotation_matrix_x = np.array([
            [1, 0, 0],
            [0, np.cos(np.radians(rotation[0])), -np.sin(np.radians(rotation[0]))],
            [0, np.sin(np.radians(rotation[0])), np.cos(np.radians(rotation[0]))]
        ])

        rotation_matrix_y = np.array([
            [np.cos(np.radians(rotation[1])), 0, np.sin(np.radians(rotation[1]))],
            [0, 1, 0],
            [-np.sin(np.radians(rotation[1])), 0, np.cos(np.radians(rotation[1]))]
        ])

        rotation_matrix_z = np.array([
            [np.cos(np.radians(rotation[2])), -np.sin(np.radians(rotation[2])), 0],
            [np.sin(np.radians(rotation[2])), np.cos(np.radians(rotation[2])), 0],
            [0, 0, 1]
        ])

        # 组合三个旋转矩阵
        rotation_matrix = np.dot(np.dot(rotation_matrix_x, rotation_matrix_y), rotation_matrix_z)

        if rotation_matrix is not None:
            # 对方块的每个顶点坐标减去旋转中心，应用旋转矩阵，再加上旋转中心
            coords = [tuple(np.dot(rotation_matrix, point - center) + center) for point in coords]

        rotation_matrix_x = np.array([
            [1, 0, 0],
            [0, 0, -1],
            [0, 1, 0]
        ])
    else:
        
        rotation_matrix_x = np.array([
            [1, 0, 0],
            [0, 0, -1],
            [0, 1, 0]
        ])
        
        coords = [tuple(np.dot(rotation_matrix_x, point)) for point in coords]

    coords = [tuple(np.array(point)*scale_factor) for point in coords]       
    
    if position is not None:
        coords = [(point[0] + position[0], point[1] + position[1], point[2] + position[2]) for point in coords]
    
    return coords

def fac(origin, display, position, element, vertices, faces, vertices_dict, directions, has_air,rotation, rotation_matrix=None):
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
            coords = rot(origin, display, position, coords, rotation,rotation_matrix)
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
            coords = rot(origin, display, position, coords,rotation, rotation_matrix)
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

def extract_vertices(element, display, has_air, vertices, faces, vertices_dict, position,rotation):
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

        fac(origin, display, position, element, vertices, faces, vertices_dict, directions, has_air,rotation, rotation_matrix)
    else:
        fac((0, 0, 0), display, position, element, vertices, faces, vertices_dict, directions, has_air,rotation)

    return directions
        
def extract_vertices_from_elements(textures, elements, display, has_air, position=None,Rotation=None, vertices=[], faces=[], direction=[], texture_list=[], uv_list=[], uv_rotation_list=[], vertices_dict={}):
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
            directions = extract_vertices(element, display, has_air, vertices, faces, vertices_dict, position,Rotation)
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
                            texture = textures[texture]
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
from .functions import get_file_path
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
