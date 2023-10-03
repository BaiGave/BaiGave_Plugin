import bpy
import os
import numpy as np
from .classification import NeedsToBeColored,Leaves

def create_nodes(nodes, texture_paths, links):
    tex_nodes = []
    bsdf_nodes = []
    for i, texture_path in enumerate(texture_paths):
        image_name = os.path.basename(texture_path)
        image = bpy.data.images.get(image_name)
        if image is None:
            image = bpy.data.images.load(texture_path)
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.location = (-400 if i == 1 else 0, 200)
        tex_node.image = image
        tex_node.interpolation = 'Closest'
        tex_nodes.append(tex_node)
        bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf_node.location = (200, 200)
        bsdf_nodes.append(bsdf_node)

        links.new(tex_node.outputs['Color'], bsdf_node.inputs['Base Color'])
        links.new(tex_node.outputs['Alpha'], bsdf_node.inputs['Alpha'])

    return tex_nodes, bsdf_nodes

def create_node_material(texture_paths, mat_name, mix_shaders,filename):
    mat_name = mat_name.replace("block/", "")  # 去除"block/"部分
    mat = bpy.data.materials.get(mat_name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links

    # 清除默认的Diffuse BSDF节点和输出节点
    nodes_to_delete = [node for node in nodes if node.type in ['BSDF_PRINCIPLED', 'OUTPUT_MATERIAL']]
    for node in nodes_to_delete:
        nodes.remove(node)

    # 创建节点
    tex_nodes, bsdf_nodes = create_nodes(nodes, texture_paths, links)

    # 创建Mix Shader节点
    if mix_shaders:
        mix_node = nodes.new('ShaderNodeMixShader')
        mix_node.location = (600, 200)

        links.new(bsdf_nodes[0].outputs['BSDF'], mix_node.inputs[1])
        links.new(bsdf_nodes[1].outputs['BSDF'], mix_node.inputs[2])

        geometry = nodes.new(type='ShaderNodeNewGeometry')
        
        # 创建 UV 节点1
        uv_node_1 = nodes.new('ShaderNodeUVMap')
        uv_node_1.location = (-300, 0)
        uv_node_1.uv_map = "UVMap"

        # 创建 UV 节点2
        uv_node_2 = nodes.new('ShaderNodeUVMap')
        uv_node_2.location = (-300, 0)
        uv_node_2.uv_map = "UVMap_1"

        # 连接节点
        links.new(geometry.outputs[6], mix_node.inputs['Fac'])
        links.new(uv_node_1.outputs['UV'], tex_nodes[0].inputs['Vector'])
        links.new(uv_node_2.outputs['UV'], tex_nodes[1].inputs['Vector'])

        output_node = nodes.new('ShaderNodeOutputMaterial')
        output_node.location = (1000, 200)

        links.new(mix_node.outputs['Shader'], output_node.inputs['Surface'])
    else:
        if mat_name in NeedsToBeColored:
            mix_node = nodes.new('ShaderNodeMix')
            
            mix_node.data_type='RGBA'
            mix_node.blend_type='MULTIPLY'
            mix_node.inputs[0].default_value = 1.0
            
            mix_node.location = (-200, 500)
            
          # 创建纹理坐标节点
            texture_coordinate_node = nodes.new('ShaderNodeTexCoord')
            texture_coordinate_node.location = (-400, 200)

            # 创建材质纹理节点
            colormap_texture_node = nodes.new('ShaderNodeTexImage')
            colormap_texture_node.location = (-300, 200)
            colormap_texture_node.image = bpy.data.images.get(filename + "_colormap")  
            colormap_texture_node.interpolation = 'Closest'

            output_node = nodes.new('ShaderNodeOutputMaterial')
            output_node.location = (600, 200)
            links.new(tex_nodes[0].outputs['Color'], mix_node.inputs[6])
            links.new(colormap_texture_node.outputs['Color'], mix_node.inputs[7])
            links.new(texture_coordinate_node.outputs[0], colormap_texture_node.inputs[0])
            # 断开材质和BSDF之间的连接
            links.remove(links[0])  
            links.new(mix_node.outputs[2], bsdf_nodes[0].inputs[0])
            links.new(bsdf_nodes[0].outputs['BSDF'], output_node.inputs['Surface'])
            if mat_name in Leaves:
                mix_node1 = nodes.new('ShaderNodeMixShader')
                mix_node1.location = (600, 200)
                mix_node2 = nodes.new('ShaderNodeMixShader')
                mix_node2.location = (800, 200)
                mix_node1.inputs["Fac"].default_value = 0.2
                transparent_node = nodes.new(type='ShaderNodeBsdfTransparent')
                transparent_node.location = (800, -200)
                translucent_node = nodes.new(type="ShaderNodeBsdfTranslucent")
                translucent_node.location = (600, -200)
                links.remove(links[0])  

                links.new(bsdf_nodes[0].outputs['BSDF'], mix_node1.inputs[1])
                links.new(translucent_node.outputs[0], mix_node1.inputs[2])

                links.new(mix_node.outputs[2], translucent_node.inputs[0])

                links.new(tex_nodes[0].outputs['Alpha'], mix_node2.inputs[0])
                links.new(mix_node1.outputs[0], mix_node2.inputs[2])
                links.new(transparent_node.outputs[0], mix_node2.inputs[1])

                links.new(mix_node2.outputs[0], output_node.inputs['Surface'])


        else:
            output_node = nodes.new('ShaderNodeOutputMaterial')
            output_node.location = (600, 200)

            links.new(bsdf_nodes[0].outputs['BSDF'], output_node.inputs['Surface'])

    return mat


def rot(origin, display, position, coords, rotation_matrix=None):
    scale_factor = 1/16
    if rotation_matrix is not None:
        coords = [tuple(np.dot(rotation_matrix, (point - origin)) + origin) for point in coords]

    if 'fixed' in display:
        display_rotation = display.get('fixed', {}).get('rotation', [0,0,0])

        
        rotation_matrix_x = np.array([
            [1, 0, 0],
            [0, np.cos(np.radians(display_rotation[0])), -np.sin(np.radians(display_rotation[0]))],
            [0, np.sin(np.radians(display_rotation[0])), np.cos(np.radians(display_rotation[0]))]
        ])
        
        rotation_matrix_y = np.array([
            [np.cos(np.radians(display_rotation[1])), 0, np.sin(np.radians(display_rotation[1]))],
            [0, 1, 0],
            [-np.sin(np.radians(display_rotation[1])), 0, np.cos(np.radians(display_rotation[1]))]
        ])
        
        rotation_matrix_z = np.array([
            [np.cos(np.radians(display_rotation[2])), -np.sin(np.radians(display_rotation[2])), 0],
            [np.sin(np.radians(display_rotation[2])), np.cos(np.radians(display_rotation[2])), 0],
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

def fac(origin, display, position, element, vertices, faces, vertices_dict, directions, has_air, rotation_matrix=None):
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
            coords = rot(origin, display, position, coords, rotation_matrix)
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
            coords = rot(origin, display, position, coords, rotation_matrix)
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

def extract_vertices(element, display, has_air, vertices, faces, vertices_dict, position):
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

        fac(origin, display, position, element, vertices, faces, vertices_dict, directions, has_air, rotation_matrix)
    else:
        fac((0, 0, 0), display, position, element, vertices, faces, vertices_dict, directions, has_air)

    return directions
        
def extract_vertices_from_elements(textures, elements, display, has_air, position=None, vertices=[], faces=[], direction=[], texture_list=[], uv_list=[], uv_rotation_list=[], vertices_dict={}):
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
            directions = extract_vertices(element, display, has_air, vertices, faces, vertices_dict, position)
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
def get_or_create_material(texture, texture2, type,filename):
    mat_name = ""
    if type == 'cube':
        mat_name = f"{texture}"
    elif type == 'face':
        mat_name = f"{texture}_backface"

    if mat_name not in bpy.data.materials:
        if type == 'cube':
            mat = create_node_material([get_file_path(texture, "t")], mat_name,False,filename)
        elif type == 'face':
            mat = create_node_material([get_file_path(texture, "t"), get_file_path(texture2, "t")], mat_name,True,filename)
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
