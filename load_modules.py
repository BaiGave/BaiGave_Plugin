import bpy
import importlib

if "sway_animation" in locals():
	importlib.reload(sway_animation)
else:
	from .operators import sway_animation
	
if "operator" in locals():
	importlib.reload(operator)
else:
	from .operators import operator

if "property" in locals():
	importlib.reload(property)
else:
	from .operators import property

if "BaiGave_Rig" in locals():
	importlib.reload(BaiGave_Rig)
else:
	from .operators import BaiGave_Rig
	
if "surface_optimization" in locals():
	importlib.reload(surface_optimization)
else:
	from .operators import surface_optimization

if "map" in locals():
	importlib.reload(map)
else:
	from .operators import map
	
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
	operator,
	ui
)


def register():
	for mod in module_list:
		mod.register()



def unregister():
	for mod in reversed(module_list):
		mod.unregister()
	del bpy.types.Scene.BaiGave
