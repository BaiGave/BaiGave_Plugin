import bpy
import addon_utils
import pickle
import socket
import time

loaded_default, loaded_state = addon_utils.check("BaiGave_Plugin")
if not loaded_state:
    addon_utils.enable("BaiGave_Plugin")
loaded_default, loaded_state = addon_utils.check("blender_command_port")
if not loaded_state:
    addon_utils.enable("Blender_Command_Port")
bpy.ops.baigave.multiprocess_pool()