from .functions.get_data import get_file_path,get_all_data
from .functions.tip import ShowMessageBox
from collections import Counter
import bpy
import os
import json
def write_model_dict(file, dictionary):
    for key, value in dictionary.items():
        file.write(f"    '{key}': {value},\n")
        
def calculate_average_color(image_path):
    # 打开图片
    #img = Image.open(image_path)

    # 调整图片大小以便处理
    img = img.resize((1, 1))

    # 获取像素值
    pixel = img.getpixel((0, 0))

    # 转换为0-1之间的浮点数
    normalized_color = (round(pixel[0] / 255, 2), round(pixel[1] / 255, 2), round(pixel[2] / 255, 2) ,round(pixel[3] / 255, 2) if len(pixel) == 4 else 1.0)

    return normalized_color

def get_color(variant_value,dic, id):
    if 'model' in variant_value:
        model = variant_value['model']
        filepath = get_file_path(model, 'm')
        if filepath is None:
            return
        dirname, filename = os.path.split(filepath)
        dirname = dirname + '\\'
        try:
            t, _, _ = get_all_data(dirname, filename)
            texture_counter = Counter(t.values())
            most_common_texture = texture_counter.most_common(1)[0][0]

            processed_textures = set()

            for value in t.values():
                if value != most_common_texture:
                    continue

                if value in processed_textures:
                    continue
                processed_textures.add(value)

                texture = get_file_path(value, 't')
                average_color = calculate_average_color(texture)
                dic[id] = tuple(average_color)
                return  # 找到第一个图像的颜色平均值后立即返回

        except Exception as e:
            pass

def make_color_dict(filepaths,name,blocktype):
    cube_dict = {}
    slab_dict = {}
    slab_top_dict = {}
    stairs_west_top_outer_left = {}
    stairs_east_top_outer_left = {}
    stairs_south_top_outer_left = {}
    stairs_north_top_outer_left = {}
    stairs_west_bottom_outer_left = {}
    stairs_east_bottom_outer_left = {}
    stairs_south_bottom_outer_left = {}
    stairs_north_bottom_outer_left = {}
    stairs_west_top_straight = {}
    stairs_east_top_straight = {}
    stairs_west_bottom_straight = {}
    stairs_east_bottom_straight = {}
    stairs_north_top_straight = {}
    stairs_south_top_straight = {}
    stairs_north_bottom_straight = {}
    stairs_south_bottom_straight = {}
    stairs_south_top_inner_left = {}
    stairs_north_top_inner_right = {}
    stairs_west_top_inner_left = {}
    stairs_west_top_inner_right = {}
    stairs_south_bottom_inner_left = {}
    stairs_north_bottom_inner_right = {}
    stairs_west_bottom_inner_left = {}
    stairs_west_bottom_inner_right = {}

    
    for index, file_path in enumerate(filepaths):
        if os.path.exists(file_path):
            dir = os.path.dirname(os.path.dirname(file_path)).split(os.path.sep)[-1]
            with open(file_path, 'r') as f:
                file = os.path.basename(file_path)
                data = json.load(f)
                if 'variants' in data:
                    variants = data['variants']
                    for variant_key, variant_value in variants.items():
                        id = str(dir + ":" + file.replace(".json", "") + "[" + variant_key + "]")
                        if blocktype[index]==-1:
                            if variant_key != "":
                                if variant_key =="type=bottom":
                                    get_color(variant_value,slab_dict,id)
                                    continue
                                elif variant_key =="type=top":
                                    get_color(variant_value,slab_top_dict,id)
                                    continue
                                elif variant_key =="facing=west,half=top,shape=outer_left":
                                    get_color(variant_value,stairs_west_top_outer_left,id)
                                    continue
                                elif variant_key =="facing=east,half=top,shape=outer_left":
                                    get_color(variant_value,stairs_east_top_outer_left,id)
                                    continue
                                elif variant_key =="facing=south,half=top,shape=outer_left":
                                    get_color(variant_value,stairs_south_top_outer_left,id)
                                    continue
                                elif variant_key =="facing=north,half=top,shape=outer_left":
                                    get_color(variant_value,stairs_north_top_outer_left,id)
                                    continue
                                elif variant_key =="facing=west,half=bottom,shape=outer_left":
                                    get_color(variant_value,stairs_west_bottom_outer_left,id)
                                    continue
                                elif variant_key =="facing=east,half=bottom,shape=outer_left":
                                    get_color(variant_value,stairs_east_bottom_outer_left,id)
                                    continue
                                elif variant_key =="facing=south,half=bottom,shape=outer_left":
                                    get_color(variant_value,stairs_south_bottom_outer_left,id)
                                    continue
                                elif variant_key =="facing=north,half=bottom,shape=outer_left":
                                    get_color(variant_value,stairs_north_bottom_outer_left,id)
                                    continue
                                elif variant_key =="facing=west,half=top,shape=straight":
                                    get_color(variant_value,stairs_west_top_straight,id)
                                    continue
                                elif variant_key =="facing=east,half=top,shape=straight":
                                    get_color(variant_value,stairs_east_top_straight,id)
                                    continue
                                elif variant_key =="facing=west,half=bottom,shape=straight":
                                    get_color(variant_value,stairs_west_bottom_straight,id)
                                    continue
                                elif variant_key =="facing=east,half=bottom,shape=straight":
                                    get_color(variant_value,stairs_east_bottom_straight,id)
                                    continue
                                elif variant_key =="facing=north,half=top,shape=straight":
                                    get_color(variant_value,stairs_north_top_straight,id)
                                    continue
                                elif variant_key =="facing=south,half=top,shape=straight":
                                    get_color(variant_value,stairs_south_top_straight,id)
                                    continue
                                elif variant_key =="facing=north,half=bottom,shape=straight":
                                    get_color(variant_value,stairs_north_bottom_straight,id)
                                    continue
                                elif variant_key =="facing=south,half=bottom,shape=straight":
                                    get_color(variant_value,stairs_south_bottom_straight,id)
                                    continue
                                elif variant_key =="facing=south,half=top,shape=inner_left":
                                    get_color(variant_value,stairs_south_top_inner_left,id)
                                    continue
                                elif variant_key =="facing=north,half=top,shape=inner_right":
                                    get_color(variant_value,stairs_north_top_inner_right,id)
                                    continue
                                elif variant_key =="facing=west,half=top,shape=inner_left":
                                    get_color(variant_value,stairs_west_top_inner_left,id)
                                    continue
                                elif variant_key =="facing=west,half=top,shape=inner_right":
                                    get_color(variant_value,stairs_west_top_inner_right,id)
                                    continue
                                elif variant_key =="facing=south,half=bottom,shape=inner_left":
                                    get_color(variant_value,stairs_south_bottom_inner_left,id)
                                    continue
                                elif variant_key =="facing=north,half=bottom,shape=inner_right":
                                    get_color(variant_value,stairs_north_bottom_inner_right,id)
                                    continue
                                elif variant_key =="facing=west,half=bottom,shape=inner_left":
                                    get_color(variant_value,stairs_west_bottom_inner_left,id)
                                    continue
                                elif variant_key =="facing=west,half=bottom,shape=inner_right":
                                    get_color(variant_value,stairs_west_bottom_inner_right,id)
                                    continue
                                

                            else:
                                id = str(dir + ":" + file.replace(".json", ""))

                            if 'model' in variant_value:
                                model = variant_value['model']

                                # if model in processed_models:
                                #     continue
                                # processed_models.add(model)
                                filepath = get_file_path(model, 'm')
                                if filepath is None:
                                    continue
                                dirname, filename = os.path.split(filepath)
                                dirname = dirname + '\\'
                                try:
                                    _, _, parent = get_all_data(dirname, filename)
                                    if parent == "block/cube":
                                        t, _, _ = get_all_data(dirname, filename)
                                        texture_counter = Counter(t.values())
                                        most_common_texture = texture_counter.most_common(1)[0][0]

                                        processed_textures = set()

                                        for value in t.values():
                                            if value != most_common_texture:
                                                continue

                                            if value in processed_textures:
                                                continue
                                            processed_textures.add(value)

                                            texture = get_file_path(value, 't')
                                            average_color = calculate_average_color(texture)
                                            cube_dict[id] = tuple(average_color)
                                            break
                                    
                                except Exception as e:
                                    print(e)
                        else:
                            if variant_key != "":
                                id = str(dir + ":" + file.replace(".json", "") + "[" + variant_key + "]")
                            else:
                                id = str(dir + ":" + file.replace(".json", ""))
                            if blocktype[index]==0:
                                if 'model' in variant_value:
                                    model = variant_value['model']

                                    # if model in processed_models:
                                    #     continue
                                    # processed_models.add(model)
                                    filepath = get_file_path(model, 'm')
                                    
                                    if filepath is None:
                                        continue
                                    dirname, filename = os.path.split(filepath)
                                    dirname = dirname + '\\'
                                    t, _, _ = get_all_data(dirname, filename)
                                    texture_counter = Counter(t.values())
                                    most_common_texture = texture_counter.most_common(1)[0][0]
                                    processed_textures = set()

                                    for value in t.values():
                                        if value != most_common_texture:
                                            continue

                                        if value in processed_textures:
                                            continue
                                        processed_textures.add(value)

                                        texture = get_file_path(value, 't')
                                        average_color = calculate_average_color(texture)
                                        cube_dict[id] = tuple(average_color)
                                        break
                            elif blocktype[index]==1:
                                get_color(variant_value,slab_dict,id)
                                get_color(variant_value,slab_top_dict,id)
                                continue
                            elif blocktype[index]==2:
                                get_color(variant_value,stairs_west_top_outer_left,id)
                                get_color(variant_value,stairs_east_top_outer_left,id)
                                get_color(variant_value,stairs_south_top_outer_left,id)
                                get_color(variant_value,stairs_north_top_outer_left,id)
                                get_color(variant_value,stairs_west_bottom_outer_left,id)
                                get_color(variant_value,stairs_east_bottom_outer_left,id)
                                get_color(variant_value,stairs_south_bottom_outer_left,id)
                                get_color(variant_value,stairs_north_bottom_outer_left,id)
                                get_color(variant_value,stairs_west_top_straight,id)
                                get_color(variant_value,stairs_east_top_straight,id)
                                get_color(variant_value,stairs_west_bottom_straight,id)
                                get_color(variant_value,stairs_east_bottom_straight,id)
                                get_color(variant_value,stairs_north_top_straight,id)
                                get_color(variant_value,stairs_south_top_straight,id)
                                get_color(variant_value,stairs_north_bottom_straight,id)
                                get_color(variant_value,stairs_south_bottom_straight,id)
                                get_color(variant_value,stairs_south_top_inner_left,id)
                                get_color(variant_value,stairs_north_top_inner_right,id)
                                get_color(variant_value,stairs_west_top_inner_left,id)
                                get_color(variant_value,stairs_west_top_inner_right,id)
                                get_color(variant_value,stairs_south_bottom_inner_left,id)
                                get_color(variant_value,stairs_north_bottom_inner_right,id)
                                get_color(variant_value,stairs_west_bottom_inner_left,id)
                                get_color(variant_value,stairs_west_bottom_inner_right,id)
                                continue
    # 获取文件路径
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"colors", name + ".py")

    with open(file_path, 'w') as models_file:
        dict_names = [
            "cube_dict",
            "slab_dict",
            "slab_top_dict",
            "stairs_west_top_outer_left",
            "stairs_east_top_outer_left",
            "stairs_south_top_outer_left",
            "stairs_north_top_outer_left",
            "stairs_west_bottom_outer_left",
            "stairs_east_bottom_outer_left",
            "stairs_south_bottom_outer_left",
            "stairs_north_bottom_outer_left",
            "stairs_west_top_straight",
            "stairs_east_top_straight",
            "stairs_west_bottom_straight",
            "stairs_east_bottom_straight",
            "stairs_north_top_straight",
            "stairs_south_top_straight",
            "stairs_north_bottom_straight",
            "stairs_south_bottom_straight",
            "stairs_south_top_inner_left",
            "stairs_north_top_inner_right",
            "stairs_west_top_inner_left",
            "stairs_west_top_inner_right",
            "stairs_south_bottom_inner_left",
            "stairs_north_bottom_inner_right",
            "stairs_west_bottom_inner_left",
            "stairs_west_bottom_inner_right",
        ]

        for dict_name in dict_names:
            models_file.write(f"{dict_name} = {{\n")
            write_model_dict(models_file, locals()[dict_name])
            models_file.write("}\n")

    print("finish")
    return blocktype

def sort_type(filepaths,blocktype):
    for index, file_path in enumerate(filepaths):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                if 'variants' in data:
                    variants = data['variants']
                    for variant_key, variant_value in variants.items():
                        if blocktype[index]==-1:
                            if variant_key != "":
                                variant_key_1 = ["type=bottom", "type=top"]
                                variant_key_2 = [
                                    "facing=west,half=top,shape=outer_left", "facing=east,half=top,shape=outer_left",
                                    "facing=south,half=top,shape=outer_left", "facing=north,half=top,shape=outer_left",
                                    "facing=west,half=bottom,shape=outer_left", "facing=east,half=bottom,shape=outer_left",
                                    "facing=south,half=bottom,shape=outer_left", "facing=north,half=bottom,shape=outer_left",
                                    "facing=west,half=top,shape=straight", "facing=east,half=top,shape=straight",
                                    "facing=west,half=bottom,shape=straight", "facing=east,half=bottom,shape=straight",
                                    "facing=north,half=top,shape=straight", "facing=south,half=top,shape=straight",
                                    "facing=north,half=bottom,shape=straight", "facing=south,half=bottom,shape=straight",
                                    "facing=south,half=top,shape=inner_left", "facing=north,half=top,shape=inner_right",
                                    "facing=west,half=top,shape=inner_left", "facing=west,half=top,shape=inner_right",
                                    "facing=south,half=bottom,shape=inner_left", "facing=north,half=bottom,shape=inner_right",
                                    "facing=west,half=bottom,shape=inner_left", "facing=west,half=bottom,shape=inner_right"
                                ]

                                if variant_key in variant_key_1:
                                    blocktype[index] = 1
                                elif variant_key in variant_key_2:
                                    blocktype[index] = 2

                                
                            if 'model' in variant_value:
                                model = variant_value['model']

                                # if model in processed_models:
                                #     continue
                                # processed_models.add(model)
                                filepath = get_file_path(model, 'm')
                                if filepath is None:
                                    continue
                                dirname, filename = os.path.split(filepath)
                                dirname = dirname + '\\'
                                try:
                                    _, _, parent = get_all_data(dirname, filename)
                                    if parent == "block/cube":
                                        blocktype[index]=0
                                    
                                except Exception as e:
                                    print(e)
    return blocktype

def OpenCDict(filename):
    # 创建一个字典来存储文件中的变量
    local_vars = {}

    # 读取并执行 Python 文件
    with open(filename, 'r') as file:
        exec(file.read(), {}, local_vars)
    
    # 提取 cube_dict, slab_dict, 和 stairs_west_top_outer_left
    cube_dict = local_vars.get("cube_dict", {})
    slab_dict = local_vars.get("slab_dict", {})
    stairs_west_top_outer_left = local_vars.get("stairs_west_top_outer_left", {})
    
    # 定义一个函数来提取字典中的值和键，并添加类型
    def extract_values_and_keys(dictionary, type_value):
        extracted_dict = {}
        for key, value in dictionary.items():
            # 提取 "minecraft:" 后面的字符串
            if isinstance(key, str) and ":" in key:
                extracted_value = key.split("[")[0]
                extracted_dict[extracted_value] = {"value":value , "type": type_value}
        return extracted_dict
    
    # 提取三个字典中的值和键并合并到一个字典中
    combined_dict = {}
    
    combined_dict.update(extract_values_and_keys(cube_dict, 0))
    combined_dict.update(extract_values_and_keys(slab_dict, 1))
    combined_dict.update(extract_values_and_keys(stairs_west_top_outer_left, 2))
    return combined_dict


class OpenColorDict(bpy.types.Operator):
    bl_idname = "baigave.open_color_dict"
    bl_label = "打开对照表"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH") # type: ignore # type: ignore
    filter_glob: bpy.props.StringProperty(default="*.py", options={'HIDDEN'}) # type: ignore

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        # 清空原有的 color_to_block_list
        my_properties.color_to_block_list.clear()
        my_properties.color_file_path =self.filepath
        # 创建一个存储文件路径的集合
        combined_dict = OpenCDict(self.filepath)
        for name, block_info in combined_dict.items():
            dir_name = name 
            item = my_properties.color_to_block_list.add()
            item.name = dir_name
            item.color = block_info["value"]
            item.type = block_info["type"]

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # 设置文件选择对话框的默认路径
        self.filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"colors","")
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class ClearColorDict(bpy.types.Operator):
    bl_idname = "baigave.clear_color_dict"
    bl_label = "清除对照表"


    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        # 清空原有的 color_to_block_list
        my_properties.color_to_block_list.clear()
        my_properties.color_file_path =""

        return {'RUNNING_MODAL'}

    
class MakeColorDict(bpy.types.Operator):
    bl_idname = "baigave.make_color_dict"
    bl_label = "新建对照表"

    n: bpy.props.StringProperty(name="文件名", default="") # type: ignore

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        color_to_block_list = my_properties.color_to_block_list
        self.color_file_path =my_properties.color_file_path
        # 创建一个存储文件路径的集合
        filepaths = []
        blocktypes=[]
        # 收集文件路径
        for block_info in color_to_block_list:
            filepath = block_info.filepath
            blocktype = block_info.type
            # 将文件路径添加到集合中
            filepaths.append(filepath)
            blocktypes.append(blocktype)

        blocktype=make_color_dict(filepaths,self.n,blocktypes)
        my_properties.color_to_block_list.clear()
        ShowMessageBox("颜色字典已成功更新", "完成", 'INFO')
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_props_dialog(self, width=400)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "n")

class EditColorDict(bpy.types.Operator):
    bl_idname = "baigave.edit_color_dict"
    bl_label = "编辑对照表"

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        color_to_block_list = my_properties.color_to_block_list
        color_file_path = my_properties.color_file_path

        local_vars = {}
        # 读取并执行 Python 文件
        with open(color_file_path, 'r') as file:
            exec(file.read(), {}, local_vars)
        
        # 提取 cube_dict, slab_dict, 和 slab_top_dict
        cube_dict = local_vars.get("cube_dict", {})
        slab_dict = local_vars.get("slab_dict", {})
        slab_top_dict = local_vars.get("slab_top_dict", {})
        # 初始化所有字典
        other_dicts = {
            "stairs_west_top_outer_left": local_vars.get("stairs_west_top_outer_left", {}),
            "stairs_east_top_outer_left": local_vars.get("stairs_east_top_outer_left", {}),
            "stairs_south_top_outer_left": local_vars.get("stairs_south_top_outer_left", {}),
            "stairs_north_top_outer_left": local_vars.get("stairs_north_top_outer_left", {}),
            "stairs_west_bottom_outer_left": local_vars.get("stairs_west_bottom_outer_left", {}),
            "stairs_east_bottom_outer_left": local_vars.get("stairs_east_bottom_outer_left", {}),
            "stairs_south_bottom_outer_left": local_vars.get("stairs_south_bottom_outer_left", {}),
            "stairs_north_bottom_outer_left": local_vars.get("stairs_north_bottom_outer_left", {}),
            "stairs_west_top_straight": local_vars.get("stairs_west_top_straight", {}),
            "stairs_east_top_straight": local_vars.get("stairs_east_top_straight", {}),
            "stairs_west_bottom_straight": local_vars.get("stairs_west_bottom_straight", {}),
            "stairs_east_bottom_straight": local_vars.get("stairs_east_bottom_straight", {}),
            "stairs_north_top_straight": local_vars.get("stairs_north_top_straight", {}),
            "stairs_south_top_straight": local_vars.get("stairs_south_top_straight", {}),
            "stairs_north_bottom_straight": local_vars.get("stairs_north_bottom_straight", {}),
            "stairs_south_bottom_straight": local_vars.get("stairs_south_bottom_straight", {}),
            "stairs_south_top_inner_left": local_vars.get("stairs_south_top_inner_left", {}),
            "stairs_north_top_inner_right": local_vars.get("stairs_north_top_inner_right", {}),
            "stairs_west_top_inner_left": local_vars.get("stairs_west_top_inner_left", {}),
            "stairs_west_top_inner_right": local_vars.get("stairs_west_top_inner_right", {}),
            "stairs_south_bottom_inner_left": local_vars.get("stairs_south_bottom_inner_left", {}),
            "stairs_north_bottom_inner_right": local_vars.get("stairs_north_bottom_inner_right", {}),
            "stairs_west_bottom_inner_left": local_vars.get("stairs_west_bottom_inner_left", {}),
            "stairs_west_bottom_inner_right": local_vars.get("stairs_west_bottom_inner_right", {}),
        }

        # 更新字典的辅助函数
        def update_dict(target_dict, color, name):
            rounded_color = tuple(round(c, 2) for c in color[:])
            # 检查是否存在同名值
            existing_key = next((key for key, value in target_dict.items() if value == name), None)
            if existing_key:
                # 如果存在，将键改为 color
                del target_dict[existing_key]
                target_dict[name] = rounded_color
            else:
                # 如果不存在，新增一个 "颜色": name
                if rounded_color not in target_dict or not target_dict[rounded_color]:
                    target_dict[name] = rounded_color
                    

        # 删除不在 block_info 中的条目
        def clean_dict(target_dict, valid_names):
            keys_to_delete = [key for key, value in target_dict.items() if key not in valid_names]
            for key in keys_to_delete:
                del target_dict[key]

        # 收集文件路径
        cube_valid_names = set()  # 用于收集所有有效的 name
        slab_valid_names = set()  # 用于收集所有有效的 name
        stairs_valid_names = set()  # 用于收集所有有效的 name
        for block_info in color_to_block_list:
            name = block_info.name
            color = block_info.color
            blocktype = block_info.type
            filepath = block_info.filepath
            
           
            if blocktype ==-1:
                blocktype=sort_type([filepath],[-1])
                blocktype=blocktype[0]
            print(blocktype)
            # 根据类型写入不同的字典
            if blocktype == 0:
                cube_valid_names.add(name)  # 将 name 添加到有效集合中
                update_dict(cube_dict, color, name)
            elif blocktype == 1:
                slab_valid_names.add(name)  # 将 name 添加到有效集合中
                update_dict(slab_dict, color, name)
                update_dict(slab_top_dict, color, name)
            elif blocktype == 2:
                for key in other_dicts:
                    stairs_valid_names.add(name)  # 将 name 添加到有效集合中
                    update_dict(other_dicts[key], color, name)
            

        # 清理所有字典，删除无效的条目
        clean_dict(cube_dict, cube_valid_names)
        clean_dict(slab_dict, slab_valid_names)
        clean_dict(slab_top_dict, slab_valid_names)
        for key in other_dicts:
            clean_dict(other_dicts[key], stairs_valid_names)


        # 写回文件
        with open(color_file_path, 'w') as models_file:
            dict_names = ["cube_dict", "slab_dict", "slab_top_dict"] + list(other_dicts.keys())

            for dict_name in dict_names:
                models_file.write(f"{dict_name} = {{\n")
                write_model_dict(models_file, locals()[dict_name] if dict_name in ["cube_dict", "slab_dict", "slab_top_dict"] else other_dicts[dict_name])
                models_file.write("}\n")

        ShowMessageBox("颜色字典已成功更新", "完成", 'INFO')

        return {'RUNNING_MODAL'}

classes=[MakeColorDict,OpenColorDict,ClearColorDict,EditColorDict]




def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)