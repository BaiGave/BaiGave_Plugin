import bpy
import os
import bmesh
import importlib
from .. import config
from .model import create_mesh,add_mesh_to_collection,extract_vertices_from_elements,get_or_create_material,set_uv
def search_ctm_properties(folder_path,id):
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".properties"):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    path = None
                    ctm = None
                    for line in lines:
                        if line.startswith("matchTiles="):
                            _, match_tiles_value = line.split("=")
                            match_tiles_value = match_tiles_value.strip()
                            if match_tiles_value == id.split("\\")[-1]:  # 修改为需要匹配的值
                                path =root
                        elif line.startswith("method="):
                            _, match_tiles_value = line.split("=")
                            match_tiles_value = match_tiles_value.strip()
                            if match_tiles_value == "ctm":  # 修改为需要匹配的值
                                ctm=1
                            elif match_tiles_value == "vertial":  # 修改为需要匹配的值
                                ctm=2
                            elif match_tiles_value == "horizonal":  # 修改为需要匹配的值
                                ctm=3
                            elif match_tiles_value == "ctm_compact":  # 修改为需要匹配的值
                                ctm=4
                            elif match_tiles_value == "repeat":  # 修改为需要匹配的值
                                ctm=5
                            elif match_tiles_value == "random":  # 修改为需要匹配的值
                                ctm=6
                    if path is not None and ctm is not None:
                        return path, ctm


                       


def get_ctm_value(modid):
    importlib.reload(config)
    filepath = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp")+"\\"
    Pos = modid.find(":")
    mod = ""
    id = ""
    if Pos != -1:
        mod = modid[0:Pos]
        id = modid[Pos + 1:]
    else:
        mod = "minecraft"
        id = modid
    
    id = id.replace("/", "\\")
    directories = config.config["mod_list"]
    for directory in directories:
        if directory =="资源包":
            path = filepath+directory
            directories_r = config.config["resourcepack_list"]
            for d in directories_r:
                path =path+"\\"+d+"\\assets\\"+mod
                ctm_path=path + "\\optifine\\ctm\\"
                if os.path.exists(ctm_path):
                    result =search_ctm_properties(ctm_path,id)
                    if result:
                        return result[1]
                    else:
                        return 0




            
def block(textures,elements,position,rot,filename,has_air,collection=None):
    if collection == None:
        collection = bpy.context.collection
    ctm =0
    # for value in textures.values():
    #     ctm_value = get_ctm_value(value)
    #     if ctm_value != 0 and ctm_value is not None:
    #         ctm = ctm_value
    #         break
    mesh_name = filename
    mesh = create_mesh(mesh_name.split('#')[0]+"#"+str(ctm)+mesh_name.split('#')[1])
    obj = add_mesh_to_collection(collection, mesh)
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict ={}
    
    vertices,faces,direction,texture_list,uv_list,uv_rotation_list = extract_vertices_from_elements(textures, elements, has_air,None,rot, vertices, faces, direction, texture_list, uv_list, uv_rotation_list, vertices_dict)
    
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

    return obj


    




