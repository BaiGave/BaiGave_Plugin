import json
import bpy
import os
from importlib import reload
from .merge_images import merger
from ... import config
file_data_cache = {}
global_filepath = bpy.utils.script_path_user()
json_file_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "icons", "modid.json")

def load_modid_list():
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)
    else:
        return []

mod_list = load_modid_list()

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
                    if path is not None and ctm is not None:
                        return path, ctm

def get_all_data(filepath, filename,rot=0):
    parent =None
    if (filepath, filename,rot) in file_data_cache:
        textures, elements,parent = file_data_cache[(filepath, filename,rot)]
    else:
        textures = {}
        elements = []
        def extract_textures_and_elements(data):
            data_textures = data.get("textures", {})
            for key, value in data_textures.items():
                if "#" in value:
                    textures[key] = textures[value[1:]]
                else:
                    if key not in textures:
                        textures[key] = value

            data_elements = data.get("elements", [])
            elements_to_add = [element for element in data_elements if not any(e for e in elements if e["from"] == element["from"] and e["to"] == element["to"])]
            elements.extend(elements_to_add)


        def process_data(data):
            nonlocal parent
            if "parent" not in data or data["parent"] == "block/block":
                extract_textures_and_elements(data)
                return textures, elements
            parent=data["parent"]
            with open(get_file_path(data["parent"], "m"), "r") as f:
                parent_data = json.load(f)
                extract_textures_and_elements(parent_data)
                return process_data(parent_data)

        with open(filepath + filename, "r") as f:
            data = json.load(f)
            extract_textures_and_elements(data)
            textures, elements = process_data(data)

        file_data_cache[(filepath, filename,rot)] = (textures, elements , parent)
    return textures, elements ,parent
def get_file_path(modid,type):
    reload(config)
    filepath = global_filepath + "\\addons\\BaiGave_Plugin\\temp\\"
    Pos = modid.find(":")
    mod = ""
    id = ""
    version =""
    if Pos != -1:
        mod = modid[0:Pos]
        id = modid[Pos + 1:]
    else:
        mod = "minecraft"
        id = modid
    
    if mod == "minecraft":
        version="\\"+config.config["version"]
    id = id.replace("/", "\\")


    directories = config.config["mod_list"]
    for directory in directories:
        if directory == "minecraft":
            path = filepath+directory+version+"\\assets\\"+mod
            if type == 's':
                temp_path=path + "\\blockstates\\" + id + ".json"
                if os.path.exists(temp_path):
                    return temp_path
                else:
                    continue
            elif type == 'm':
                temp_path =path + "\\models\\" + id + ".json"
                if os.path.exists(temp_path):
                    return temp_path
                else:
                    continue
            elif type == 't':
                temp_path = path + "\\textures\\" + id + ".png"
                if os.path.exists(temp_path):
                    return temp_path
                else:
                    continue
        elif directory =="资源包":
            path = filepath+directory
            directories_r = config.config["resourcepack_list"]
            for d in directories_r:
                path =path+"\\"+d+"\\assets\\"+mod
                if type == 's':
                    temp_path=path + "\\blockstates\\" + id + ".json"
                    if os.path.exists(temp_path):
                        return temp_path
                    else:
                        continue
                elif type == 'm':
                    temp_path=path + "\\models\\" + id + ".json"
                    if os.path.exists(temp_path):
                        return temp_path
                    else:
                        continue
                elif type == 't':
                    ctm_path=path + "\\optifine\\ctm\\"
                    
                    if os.path.exists(ctm_path):
                        result =search_ctm_properties(ctm_path,id)
                        if result:
                            pngs_path, ctm_value = result
                            merger(pngs_path+"\\")
                            
                            temp_path=pngs_path +"\\"+  id.split("\\")[-1] + ".png"
                            if os.path.exists(temp_path):
                                return temp_path
                            else:
                                continue
                        else:
                            temp_path=path + "\\textures\\" + id + ".png"
                            if os.path.exists(temp_path):
                                return temp_path
                            else:
                                continue
                    else:
                        temp_path=path + "\\textures\\" + id + ".png"
                        if os.path.exists(temp_path):
                            return temp_path
                        else:
                            continue
            
        else:
            path = filepath+directory+"\\assets\\"+mod
            if type == 's':
                temp_path=path + "\\blockstates\\" + id + ".json"
                if os.path.exists(temp_path):
                    return temp_path
                else:
                    continue
            elif type == 'm':
                temp_path=path + "\\models\\" + id + ".json"
                if os.path.exists(temp_path):
                    return temp_path
                else:
                    continue
            elif type == 't':
                temp_path=path + "\\textures\\" + id + ".png"
                if os.path.exists(temp_path):
                    return temp_path,None
                else:
                    continue
    

def get_frametime(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    frametime = data.get("animation", {}).get("frametime", 1)
    return frametime

def is_file_path_exists(file_path):
    return os.path.exists(file_path)





