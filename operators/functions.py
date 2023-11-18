import json
import zipfile
import re
import toml
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
    # 检查 mod 是否存在于 mod_list 中
    matching_mods = [item[1] for item in mod_list if item[0] == mod]

    if matching_mods:
        # mod 存在于 mod_list 中，获取对应的 jar_file
        jar_file = matching_mods[0]
    else:
        return ""
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

def is_file_path_exists(file_path):
    return os.path.exists(file_path)

def extract_icons_from_jar(jar_path, mod_id, icon_filename):
    icons_dir = bpy.context.scene.icons_dir  # 获取注册的路径
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)

    with zipfile.ZipFile(jar_path, 'r') as jar:
        if icon_filename in jar.namelist():
            icon_data = jar.read(icon_filename)
            icon_path = os.path.join(icons_dir, icon_filename) 
            with open(icon_path, 'wb') as icon_file:
                icon_file.write(icon_data)
            
    return None

def read_jar_files_and_extract_data(directory):
    if not os.path.exists(directory):
        print(f"目录 {directory} 不存在")

    jar_files = [file for file in os.listdir(directory) if file.endswith('.jar')]
    if not jar_files:
        print(f"在目录 {directory} 下找不到任何 .jar 文件")
        
    versions = []  # 用于存储版本号
    modids = []  # 用于存储 modId
    icons = []  # 用于存储 icon
    names = []  # 用于存储 name
    descriptions = []  # 用于存储 description

    for jar_file in jar_files:
        jar_path = os.path.join(directory, jar_file)
        try:
            with zipfile.ZipFile(jar_path, 'r') as jar:
                if 'fabric.mod.json' in jar.namelist():
                    with jar.open('fabric.mod.json') as mod_json_file:
                        mod_json_content = mod_json_file.read()
                        mod_data = json.loads(mod_json_content.decode('utf-8'))
                        # 读取 "id" 字段的值
                        mod_id = mod_data.get("id")
                        icon = mod_data.get("icon").replace("/", "\\")
                        name = mod_data.get("name")
                        description = mod_data.get("description")
                elif 'META-INF/mods.toml' in jar.namelist():
                    with jar.open('META-INF/mods.toml') as mods_toml_file:
                        mods_toml_content = mods_toml_file.read()
                        mods_toml_data = toml.loads(mods_toml_content.decode('utf-8'))
                        if "mods" in mods_toml_data:
                            for mod_entry in mods_toml_data["mods"]:
                                mod_id = mod_entry["modId"]
                                icon = mod_entry.get("logoFile", "").replace("/", "\\")  # 添加默认值，防止没有 "logoFile" 字段时报错
                                name = mod_entry.get("displayName", "")  # 添加默认值，防止没有 "displayName" 字段时报错
                                description = mod_entry.get("description", "")  # 添加默认值，防止没有 "description" 字段时报错
                        else:
                            print(f"在 {jar_file} 中找不到 'mods' 条目")
                else:
                    # 使用正则表达式匹配版本号
                    version_match = re.search(r'\d+\.\d+(\.\d+)?', jar_file)
                    if version_match:
                        version_number = version_match.group()
                        versions.append(version_number)
                    else:
                        print(f"在 {jar_file} 中找不到 fabric.mod.json 或 META-INF/mods.toml 文件")

                if mod_id is not None:
                    extract_icons_from_jar(jar_path, mod_id, icon)
                    modids.append((mod_id,jar_file))
                    icons.append(icon)
                    names.append(name)
                    descriptions.append(description)
        except Exception as e:
            print(f"处理 {jar_file} 时出现错误：{str(e)}")

    return versions, modids, icons, names, descriptions




