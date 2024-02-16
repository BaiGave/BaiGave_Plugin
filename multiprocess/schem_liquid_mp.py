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
    chunks,mp_chunks,schempath,interval,processnum = pickle.load(file)
bpy.ops.baigave.import_schem_liquid(filepath=schempath)