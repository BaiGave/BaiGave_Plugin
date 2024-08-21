import bpy
import importlib

if "install" in locals():
	importlib.reload(install)
else:
	from . import install
if "property" in locals():
	importlib.reload(property)
else:
	from .codes import property
if "color_dict" in locals():
	importlib.reload(color_dict)
else:
	from .codes import color_dict
if "sway_animation" in locals():
	importlib.reload(sway_animation)
else:
	from .codes.functions import sway_animation
	
if "importfile" in locals():
	importlib.reload(importfile)
else:
	from .codes import importfile

if "exportfile" in locals():
	importlib.reload(exportfile)
else:
	from .codes import exportfile

if "create_world" in locals():
	importlib.reload(create_world)
else:
	from .codes import create_world

if "search_file" in locals():
	importlib.reload(search_file)
else:
	from .codes.functions import search_file

if "mesh_to_mc" in locals():
	importlib.reload(mesh_to_mc)
else:
	from .codes.functions import mesh_to_mc

if "BaiGave_Rig" in locals():
	importlib.reload(BaiGave_Rig)
else:
	from .codes.unuse import BaiGave_Rig
	
if "surface_optimization" in locals():
	importlib.reload(surface_optimization)
else:
	from .codes.functions import surface_optimization

if "WXR_Sky" in locals():
	importlib.reload(WXR_Sky)
else:
	from .codes.unuse import WXR_Sky
	
if "ui" in locals():
	importlib.reload(ui)
else:
	from . import ui
	
module_list = (
	property,
	color_dict,
	sway_animation,
	BaiGave_Rig,
	surface_optimization,
	WXR_Sky,
	search_file,
	importfile,
	exportfile,
	create_world,
	mesh_to_mc,
	ui
)


def register():
	for mod in module_list:
		mod.register()



def unregister():
	for mod in reversed(module_list):
		mod.unregister()
	del bpy.types.Scene.BaiGave
