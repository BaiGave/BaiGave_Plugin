import bpy
import importlib

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

if "merge_images" in locals():
	importlib.reload(merge_images)
else:
	from .codes.functions import merge_images

if "mesh_to_mc" in locals():
	importlib.reload(mesh_to_mc)
else:
	from .codes.functions import mesh_to_mc

if "property" in locals():
	importlib.reload(property)
else:
	from .codes import property

if "BaiGave_Rig" in locals():
	importlib.reload(BaiGave_Rig)
else:
	from .codes.unuse import BaiGave_Rig
	
if "surface_optimization" in locals():
	importlib.reload(surface_optimization)
else:
	from .codes.functions import surface_optimization

if "map" in locals():
	importlib.reload(map)
else:
	from .codes.unuse import map
	
if "ui" in locals():
	importlib.reload(ui)
else:
	from . import ui
	
module_list = (
	property,
	sway_animation,
	BaiGave_Rig,
	surface_optimization,
	map,
	search_file,
	merge_images,
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
