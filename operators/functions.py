import json
import bpy

file_data_cache = {}
global_filepath = bpy.utils.script_path_user()

def get_all_data(filepath, filename):
    if (filepath, filename) in file_data_cache:
        textures, elements, display = file_data_cache[(filepath, filename)]
    else:
        textures = {}
        elements = []
        display = {}

        def extract_textures_and_elements(data):
            data_textures = data.get("textures", {})
            for key, value in data_textures.items():
                if "#" in value:
                    textures[key] = textures[value[1:]]
                else:
                    textures[key] = value

            data_elements = data.get("elements", [])
            elements_to_add = [element for element in data_elements if not any(e for e in elements if e["from"] == element["from"] and e["to"] == element["to"])]
            elements.extend(elements_to_add)

            display.update(data.get("display", {}))

        def process_data(data):
            if "parent" not in data or data["parent"] == "block/block":
                extract_textures_and_elements(data)
                return textures, elements

            with open(get_file_path(data["parent"], "m"), "r") as f:
                parent_data = json.load(f)
                extract_textures_and_elements(parent_data)
                return process_data(parent_data)

        with open(filepath + filename, "r") as f:
            data = json.load(f)
            extract_textures_and_elements(data)
            textures, elements = process_data(data)

        file_data_cache[(filepath, filename)] = (textures, elements, display)
    return textures, elements, display


def get_file_path(modid, type):
    filepath = global_filepath + "\\addons\\BaiGave_Plugin\\assets\\"
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
        return filepath + mod + "\\blockstates\\" + id + ".json"
    elif type == 'm':
        return filepath + mod + "\\models\\" + id + ".json"
    elif type == 't':
        return filepath + mod + "\\textures\\" + id + ".png"

def get_frametime(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    frametime = data.get("animation", {}).get("frametime", 1)
    return frametime