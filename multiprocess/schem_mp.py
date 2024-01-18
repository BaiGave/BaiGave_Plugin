import bpy
import addon_utils
import pickle
import socket
import time
import threading

loaded_default, loaded_state = addon_utils.check("BaiGave_Plugin")
if not loaded_state:
    addon_utils.enable("BaiGave_Plugin")
loaded_default, loaded_state = addon_utils.check("blender_command_port")
if not loaded_state:
    addon_utils.enable("Blender_Command_Port")
VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
with open(VarCachePath, 'rb') as file:
    chunks,mp_chunks,schempath,interval,processnum = pickle.load(file)
bpy.ops.baigave.import_schem_mp(filepath=schempath)

def send_command(command):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 5001))
    clientsocket.sendall(command.encode())
    while True:
        res = clientsocket.recv(4096)
        if not res:
            break
    clientsocket.close()

def send_command_pool(command):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 5002))
    clientsocket.sendall(command.encode())
    while True:
        res = clientsocket.recv(4096)
        if not res:
            break
    clientsocket.close()

current_frame = bpy.context.scene.frame_current
def thread1():
    send_command_pool("""
import bpy
import os
import pickle
import time
import subprocess
blender_path = bpy.app.binary_path
ImportPath = bpy.utils.script_path_user()
MultiprocessPath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_mp.py"
VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
with open(VarCachePath, 'rb') as file:
    chunks,mp_chunks,schempath,interval,processnum = pickle.load(file)

#多进程实现方法:后台启动headless blender(-b),只运行python代码(-P),不显示界面
bpy.context.scene.frame_current += 1
num = bpy.context.scene.frame_current
if num > len(mp_chunks):
    for i in range(1,10000000):
        j=0
        j+=i**0.5
    CacheFolder = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/"
    for filename in os.listdir(CacheFolder):
        if any(char.isdigit() for char in filename):
            os.remove(os.path.join(CacheFolder, filename))
    print("所有区块导入完成")
    bpy.ops.wm.close_command_port()
    bpy.ops.wm.quit_blender()
ChunkIndex = f"import bpy;bpy.context.scene.frame_current = {num}"
subprocess.Popen([blender_path,"-b","--python-expr",ChunkIndex,"-P",MultiprocessPath])
time.sleep(interval)
if num%16 == 0:
    time.sleep(5)
""")

def thread2():
    send_command("""
import bpy
import os
ImportPath = bpy.utils.script_path_user()
BlendFile=ImportPath + "/addons/BaiGave_Plugin/schemcache/chunk{0}.blend"
FolderPath=ImportPath + "/addons/BaiGave_Plugin/schemcache/"
with bpy.data.libraries.load(BlendFile) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects if name == "Schemetics"]
for obj in data_to.objects:
    bpy.context.scene.collection.objects.link(obj)
objects_to_join = [obj for obj in bpy.data.objects if "Schemetics" in obj.name]
if {0} % 16 == 0 or len(objects_to_join) == {1}:
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
    if len(objects_to_join) == {1}:
        material_variants = {{}}
        for material in materials:
            try:
                node_tree = material.node_tree
                nodes = node_tree.nodes
                for node in nodes:
                    if node.type == 'TEX_IMAGE':
                        if node.name == '色图':
                            node.image = bpy.data.images.get("colormap")
            except Exception as e:
                print("材质出错了:", e)
        try:
            LiquidPath=ImportPath + "/addons/BaiGave_Plugin/schemcache/liquid.blend"
            with bpy.data.libraries.load(BlendFile) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects if name == "liquid"]
            for obj in data_to.objects:
                bpy.context.scene.collection.objects.link(obj)
        except Exception as e:
            print("流体出错了:", e)
        bpy.ops.wm.close_command_port()
""".format(current_frame, len(mp_chunks)))
    
t1=threading.Thread(target=thread1)
t2=threading.Thread(target=thread2)
t1.start()
t2.start()
t1.join()
t2.join()
bpy.ops.wm.quit_blender()


