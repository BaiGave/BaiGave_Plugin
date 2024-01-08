import bpy
import bmesh
from .model import create_mesh,add_mesh_to_collection,extract_vertices_from_elements,get_or_create_material,set_uv

def block(textures,elements,position,rot,filename,has_air,collection=None):
    if collection == None:
        collection = bpy.context.collection
    mesh_name = filename
    mesh = create_mesh(mesh_name)
    obj = add_mesh_to_collection(collection, mesh)
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}

    vertices,faces,direction,texture_list,uv_list,uv_rotation_list = extract_vertices_from_elements(textures, elements, has_air, None,rot, vertices, faces, direction, texture_list, uv_list, uv_rotation_list, vertices_dict)
    
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
    bpy.context.scene.cursor.location = (0, 0, 0)
    
    # 设置物体的原点中心位置为3D游标位置
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    obj.location = position
    obj.select_set(False)


    




