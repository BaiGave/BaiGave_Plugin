import bpy
import bmesh
from .model import create_mesh,add_mesh_to_collection,get_or_create_material,set_uv
from .blockstates import d_blockstates
from .classification import exclude

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

def nbt(d,filename="nbt",position=(0,0,0)):
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
            vertices,faces,direction,texture_list,uv_list,uv_rotation_list = d_blockstates(key, d, vertices, faces, direction, texture_list, uv_list, uv_rotation_list, vertices_dict)
            
    collection =bpy.context.scene.collection
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
                loop[uv_layer].uv = set_uv(uv_coords, i, rotation)

    bm.faces.ensure_lookup_table()
    bm.to_mesh(mesh)
    bm.free()