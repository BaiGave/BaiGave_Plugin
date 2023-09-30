import bpy
import bmesh
from .model import create_mesh, add_mesh_to_collection, get_or_create_material, set_uv

def generate(x, z, vertices, faces, texture_list, uv_list, direction, uv_rotation_list):
    mesh_name = str(x) + "," + str(z)
    collection = bpy.context.collection
    mesh = create_mesh(mesh_name)
    obj = add_mesh_to_collection(collection, mesh)
    obj.location = (x * 16, z * 16, 0)
    bm = bmesh.new()
  
    for v in vertices:
        bm.verts.new(v)
    bm.verts.ensure_lookup_table()

    uv_layer = bm.loops.layers.uv.new()
    for face_index, f in enumerate(faces):
        existing_face = bm.faces.get([bm.verts[i] for i in f])
        if existing_face is not None:
            face = existing_face
        else:
            face = bm.faces.new([bm.verts[i] for i in f])

        mat = get_or_create_material(texture_list[face_index], texture_list[face_index], 'cube')
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
