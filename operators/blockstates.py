import json
import os
from .model import extract_vertices_from_elements
from .functions import get_file_path, get_all_data

def blockstates(coord, d, vertices, faces, direction, texture_list, uv_list, uv_rotation_list, vertices_dict):
    # 如果坐标在字典中，获取对应的方块 ID
    if coord in d:
        id = d[coord]
        # 定义一个元组，存储六个方向的偏移量，按照 上下北南东西 的顺序排序
        offsets = ((0, -1, 0),  # 东
                   (0, 1, 0),  # 西
                   (-1, 0, 0),  # 北
                   (1, 0, 0),  # 南
                   (0, 0, -1),  # 下
                   (0, 0, 1))  # 上
        # 使用列表推导式生成相邻坐标
        adjacent_coords = [(coord[0] + offset[0], coord[1] + offset[1], coord[2] + offset[2]) for offset in offsets]
        # 判断是否有空气方块
        has_air = [True] * 6  # 默认为 True
        for i, adj_coord in enumerate(adjacent_coords):
            if adj_coord in d:
                parent = get_parent(d[adj_coord])
                # 如果 parent 是 "block/cube"，将 has_air 设为 False
                if parent == "block/cube":
                    has_air[i] = False
                if parent =="yuushya:block/template_column":
                    has_air[i] = False
        if any(has_air):
            textures,elements,rotation =get_model(id)
            has_air = [has_air[2], has_air[3], has_air[0], has_air[1], has_air[5], has_air[4]]
            #旋转后判断生成面
            if rotation[0] == 0 and rotation[2]==0:
                has_air = [has_air[0], has_air[1], has_air[2], has_air[3], has_air[4], has_air[5]]
            elif rotation[0] == 0 and rotation[2]==270:
                has_air = [has_air[2], has_air[3], has_air[1], has_air[0], has_air[4], has_air[5]]
            elif rotation[0] == 0 and rotation[2]==180:
                has_air = [has_air[1], has_air[0], has_air[3], has_air[2], has_air[4], has_air[5]]
            elif rotation[0] == 0 and rotation[2]==90:
                has_air = [has_air[3], has_air[2], has_air[0], has_air[1], has_air[4], has_air[5]]
            elif rotation[0] == 180 and rotation[2]==0:
                has_air = [has_air[0], has_air[1], has_air[3], has_air[2], has_air[5], has_air[4]]
            elif rotation[0] == 180 and rotation[2]==270:
                has_air = [has_air[0], has_air[1], has_air[2], has_air[3], has_air[5], has_air[4]]
            elif rotation[0] == 180 and rotation[2]==180:
                has_air = [has_air[1], has_air[0], has_air[2], has_air[3], has_air[5], has_air[4]]
            elif rotation[0] == 180 and rotation[2]==90:
                has_air = [has_air[3], has_air[2], has_air[1], has_air[0], has_air[5], has_air[4]]
        else:
            return vertices,faces,direction,texture_list,uv_list,uv_rotation_list

    return extract_vertices_from_elements(textures, elements, has_air, coord, rotation, vertices, faces, direction, texture_list, uv_list, uv_rotation_list, vertices_dict)


# 使用字典来缓存已经计算过的方块ID与其对应的父方块ID，避免重复计算
cached_parents = {}

def get_parent(id):
    # 如果已经计算过该方块ID的父方块，直接返回缓存中的结果
    if id in cached_parents:
        return cached_parents[id]

    block_name = id.split('[')[0]
    filepath = get_file_path(block_name, 's')

    start_index = id.find('[')
    end_index = id.find(']')
    properties_dict = {}
    
    if start_index != -1 and end_index != -1:
        properties_str = id[start_index + 1:end_index]
        for prop in properties_str.split(','):
            try:
                key, value = prop.split('=')
                properties_dict[key.strip().replace('"', '')] = value.strip().replace('"', '')
            except:
                pass

    try:
        with open(filepath, "r") as f:
            data = json.load(f) 
            filepath = ""

            if "variants" in data:
                for key, value in data["variants"].items():
                    key_props = key.split(",")
                    flag = all(
                        key_prop.split("=")[1] == properties_dict[key_prop.split("=")[0]]
                        for key_prop in key_props
                        if key_prop.split("=")[0] in properties_dict
                    )

                    if flag:
                        filepath = value[0]["model"] if isinstance(value, list) else value["model"]
                        break
            elif "multipart" in data:
                for part in data["multipart"]:
                    if "when" in part:
                        when = part["when"]
                        flag = all(
                            when[key] == properties_dict[key] if key in properties_dict else False
                            for key in when
                        )

                        if flag:
                            apply = part["apply"]
                            filepath = apply["model"] if "model" in apply else ""
                            break

            if filepath == "":
                print("No matching model found")

        filepath = get_file_path(filepath, 'm')
        dirname, filename = os.path.split(filepath)
        dirname = dirname + '\\'
        _, _, parent = get_all_data(dirname, filename)

        # 将计算结果缓存起来
        cached_parents[id] = parent
        return parent

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# 使用字典来缓存已经计算过的方块ID与其对应的模型数据，避免重复调用
cached_models = {}

def get_model(id):
    # 如果已经计算过该方块ID的模型数据，直接返回缓存中的结果
    if id in cached_models:
        return cached_models[id]

    block_name = id.split('[')[0]
    filepath = get_file_path(block_name, 's')
    rotation = [0, 0, 0]
    properties_dict = {}

    start_index = id.find('[')
    end_index = id.find(']')

    if start_index != -1 and end_index != -1:
        properties_str = id[start_index + 1:end_index]
        for prop in properties_str.split(','):
            try:
                key, value = prop.split('=')
                properties_dict[key.strip().replace('"', '')] = value.strip().replace('"', '')
            except:
                pass

    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            filepath = ""
            textures = {}
            elements = []
            if "variants" in data:
                for key, value in data["variants"].items():
                    key_props = key.split(",")
                    flag = all(
                        key_prop.split("=")[1] == properties_dict[key_prop.split("=")[0]]
                        for key_prop in key_props
                        if key_prop.split("=")[0] in properties_dict
                    )

                    if flag:
                        filepath = value[0]["model"] if isinstance(value, list) else value["model"]
                        if "y" in value:
                            rotation[2] = 360 - value["y"]
                        if "x" in value:
                            rotation[0] = value["x"]
                        filepath = get_file_path(filepath, 'm')
                        dirname, filename = os.path.split(filepath)
                        dirname = dirname + '\\'
                        t, e, _ = get_all_data(dirname, filename)
                        textures.update(t)
                        elements.extend(e)
            #这里有问题
            elif "multipart" in data:
                temp_ele= []
                for part in data["multipart"]:
                    if "when" in part:
                        when = part["when"]
                        flag = all(
                            when[key] == properties_dict[key] if key in properties_dict else False
                            for key in when
                        )
                        if flag:
                            apply = part["apply"]
                            filepath = apply["model"] if "model" in apply else ""
                            filepath = get_file_path(filepath, 'm')
                            dirname, filename = os.path.split(filepath)
                            dirname = dirname + '\\'
                            t, e, _ = get_all_data(dirname, filename)
                            if "y" in apply:
                                temp_element = []
                                for item in e:
                                    item["rotation"] = {"angle": 360 - apply["y"],"axis": "y","origin": [8, 8, 8]}
                                    temp_element.append(item)
                                    #print(temp_element)
                            textures.update(t)
                            #elements.extend(e)
                            for t in temp_element:
                                #print(t)
                                temp_ele.append(t)
                            print(temp_ele)
                        
                    elif "when" not in part:
                        apply = part["apply"]
                        filepath = apply["model"] if "model" in apply else ""
                        filepath = get_file_path(filepath, 'm')
                        dirname, filename = os.path.split(filepath)
                        dirname = dirname + '\\'
                        t, e, _ = get_all_data(dirname, filename)
                        textures.update(t)
                        elements.extend(e)
                
            if filepath == "":
                print("No matching model found")

        # filepath = get_file_path(filepath, 'm')
        # dirname, filename = os.path.split(filepath)
        # dirname = dirname + '\\'
        # textures, elements, _ = get_all_data(dirname, filename)

        # 将模型数据缓存起来
        cached_models[id] = (textures, elements, rotation)
        #print(elements)
        return textures, elements, rotation

    except Exception as e:
        print(f"An error occurred: {e}")
        textures = {}
        elements = []
        return textures, elements, rotation