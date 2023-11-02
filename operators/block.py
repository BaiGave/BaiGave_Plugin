import bpy
import bmesh
from .model import create_mesh,add_mesh_to_collection,extract_vertices_from_elements,get_or_create_material,set_uv
import math

def block(textures,elements,position,rot,filename,has_air):
    collection = bpy.context.collection
    mesh_name = filename
    mesh = create_mesh(mesh_name)
    obj = add_mesh_to_collection(collection, mesh)
    print(filename)
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}

    vertices,faces,direction,texture_list,uv_list,uv_rotation_list = extract_vertices_from_elements(textures, elements, has_air, None,[0,0,0], vertices, faces, direction, texture_list, uv_list, uv_rotation_list, vertices_dict)
    
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

        if texture_list[face_index] == "None":
            continue

        mat = get_or_create_material(texture_list[face_index],filename)
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

    # 设置3D游标位置
    bpy.context.scene.cursor.location = (0.5, -0.5, 0.5)
    # 设置物体的原点中心位置为3D游标位置
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    # 将对象的变换矩阵设置为单位矩阵
    obj.select_set(False)
    obj.location = position
    # 设置旋转（以弧度为单位）
    obj.rotation_euler = (math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2]))

    




