import json
import bpy
import os

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


def get_file_path(modid, type):
    filepath = global_filepath + "\\addons\\BaiGave_Plugin\\temp\\"
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

    if type == 's':
        return filepath + mod +"\\assets\\"+mod+ "\\blockstates\\" + id + ".json"
    elif type == 'm':
        return filepath + mod +"\\assets\\"+mod + "\\models\\" + id + ".json"
    elif type == 't':
        return filepath + mod +"\\assets\\"+mod + "\\textures\\" + id + ".png"

def get_frametime(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    frametime = data.get("animation", {}).get("frametime", 1)
    return frametime

def is_file_path_exists(file_path):
    return os.path.exists(file_path)





