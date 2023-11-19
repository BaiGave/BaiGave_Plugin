import logging
logging.getLogger("amulet").setLevel(logging.FATAL)
logging.getLogger("PyMCTranslate").setLevel(logging.FATAL)
import importlib

bl_info={
    "name":"BaiGave's Tool",
    "author":"BaiGave",
    "version":(1, 0),
    "blender":(4, 0, 0),
    "location":"View3d > Tool",
    "warning":"如果有任何问题请联系白给~我的bilbil账号:BaiGave",
    "category":"BaiGave's Tool"
}

if "load_modules" in locals():
	importlib.reload(load_modules)
else:
	from . import load_modules


def register():
	load_modules.register()


def unregister():
	load_modules.unregister()
	

if __name__ == "__main__":
	register()

