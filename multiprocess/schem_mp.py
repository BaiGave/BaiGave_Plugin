import bpy
import addon_utils
import pickle
import socket
import time


loaded_default, loaded_state = addon_utils.check("BaiGave_Plugin")
if not loaded_state:
    addon_utils.enable("BaiGave_Plugin")
VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
with open(VarCachePath, 'rb') as file:
    chunks,schempath,origin,filename = pickle.load(file)
bpy.ops.baigave.import_schem_mp(filepath=schempath)

def send_command(command):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 5000))
    clientsocket.sendall(command.encode())
    while True:
        res = clientsocket.recv(4096)
        if not res:
            break
    clientsocket.close()

current_frame = bpy.context.scene.frame_current
time.sleep(current_frame*3)
send_command("""
import bpy
import os
ImportPath = bpy.utils.script_path_user()
BlendFile=ImportPath + "/addons/BaiGave_Plugin/schemcache/chunk{}.blend"
FolderPath=ImportPath + "/addons/BaiGave_Plugin/schemcache/"
with bpy.data.libraries.load(BlendFile) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects if name == "Schemetics"]
for obj in data_to.objects:
    bpy.context.scene.collection.objects.link(obj)
materials = bpy.data.materials  # 合并重名材质
material_variants = {{}}
for material in materials:
    if ':' in material.name:
        base_name = material.name.split(".")[0]
        if base_name not in material_variants:
            material_variants[base_name] = material
        else:
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    if obj.data.materials:
                        for i in range(len(obj.data.materials)):
                            if obj.data.materials[i] == material:
                                obj.data.materials[i] = material_variants[base_name]
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
objects_to_join = [obj for obj in bpy.data.objects if "Schemetics" in obj.name]
if len(objects_to_join) == (os.cpu_count())/2:
    material_variants = {{}}
    for material in materials:
        try:
            node_tree = material.node_tree
            nodes = node_tree.nodes
            for node in nodes:
                if node.type == 'TEX_IMAGE':
                    if node.name == '色图':
                        node.image = bpy.data.images.get("colormap")
        except:
            pass
    for obj in objects_to_join:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects_to_join[0]
    bpy.ops.object.join()
    #按材质分离
    bpy.context.view_layer.objects.active.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='MATERIAL')
    bpy.ops.object.mode_set(mode='OBJECT')
    #重命名
    for obj in bpy.context.selected_objects:
        for slot in obj.material_slots:
            if slot.material:
                parts = slot.material.name.split(':')
                if len(parts) > 1:
                    obj.name = parts[1]
                break
""".format(current_frame))

