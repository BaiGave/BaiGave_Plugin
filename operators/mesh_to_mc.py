import re
import os
import bpy
from .block import block
import numpy as np
import time
import threading
from .tip import ShowMessageBox
from ..colors import color_cube_dict,color_inner_stairs_dict,color_outer_stairs_dict,color_slab_dict,color_slab_top_dict,color_stairs_dict
from collections import defaultdict
from amulet_nbt import TAG_Compound, TAG_Int, ByteArrayTag ,IntArrayTag,ShortTag
from .structure import nbt
from .blockstates import get_model

# 全局缓存来存储计算结果
distance_cache = {}

def distance(color1, color2):
    # 检查缓存，如果已计算过，直接返回缓存值
    if (color1, color2) in distance_cache:
        return distance_cache[(color1, color2)]
    elif (color2, color1) in distance_cache:
        return distance_cache[(color2, color1)]

    value = np.linalg.norm(np.array(color1) - np.array(color2))
    distance_cache[(color1, color2)] = value
    return value

def find_closest_color(target_color, color_dict):
    min_distance = float('inf')
    closest_color = None
    
    # 遍历颜色字典，寻找最接近的颜色
    for color_key in color_dict.keys():
        dist = distance(color_key, target_color)
        if dist < min_distance:
            min_distance = dist
            closest_color = color_key
    
    return color_dict[closest_color]

def get_surrounding_colors(coord, colors):
    surrounding_coords = [
        (coord[0] + 1, coord[1], coord[2]), (coord[0] - 1, coord[1], coord[2]),
        (coord[0], coord[1] + 1, coord[2]), (coord[0], coord[1] - 1, coord[2]),
        (coord[0], coord[1], coord[2] + 1), (coord[0], coord[1], coord[2] - 1)
    ]

    valid_surrounding_colors = []
    for surrounding_coord in surrounding_coords:
        if surrounding_coord in colors:
            valid_surrounding_colors.append(colors[surrounding_coord])

    return valid_surrounding_colors

def export_schem(dict,filename="file"):
    # 创建一个 NBT 复合标签来存储数据
    schem = TAG_Compound({
        'DataVersion': TAG_Int(3465),  # 数据版本，根据 Minecraft 版本设置
        'Version': TAG_Int(2),
        'Metadata': TAG_Compound({
            'WEOffsetX': TAG_Int(0),
            'WEOffsetY': TAG_Int(0),
            'WEOffsetZ': TAG_Int(0)
        }),
        'Palette':TAG_Compound({"minecraft:air":TAG_Int(0)}),
        'PaletteMax':TAG_Int(1),
        'Length':ShortTag(),
        'Height':ShortTag(),
        'Width':ShortTag(),
        "BlockData":ByteArrayTag([]),
        "Offset":IntArrayTag([0,0,0])
        })
    # 添加方块到 Palette 和 BlockData
    palette_index = 1  # 从 1 开始，因为 0 已被 "minecraft:air" 占用
    x_values = [coord[0] for coord in dict.keys()]
    y_values = [coord[1] for coord in dict.keys()]
    z_values = [coord[2] for coord in dict.keys()]

    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    min_z, max_z = min(z_values), max(z_values)

    Width = max_x - min_x + 1
    Length = max_y - min_y + 1
    Height = max_z - min_z + 1
    block_data = [0] * (Length * Width * Height)


    for position, block in dict.items():
        # 如果方块不在 Palette 中，添加它
        if block not in schem['Palette']:
            schem['Palette'][block] = TAG_Int(palette_index)
            palette_index += 1

        # 计算索引并放置对应的方块id
        x, z, y = position
        index = ((y - min_z) * Length + (z- min_y)) * Width + (x - min_x)
        block_data[index] = schem['Palette'][block].value


    # 更新 PaletteMax 和 BlockData
    schem['PaletteMax'] = TAG_Int(palette_index)
    schem['Height'] = ShortTag(Height)
    schem['Width'] = ShortTag(Width)
    schem['Length'] = ShortTag(Length)
    schem['BlockData'] = ByteArrayTag(block_data)
    # 将NBT数据写入.schem文件
    file_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "schem",filename+".schem") # 设置你想要保存的文件路径
    # # 创建一个新的选中区域
    with open(file_path, "wb") as f:
        schem.save_to(f)

def contains_chinese(text):
    """检测文本是否包含中文字符"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
    return bool(chinese_pattern.search(text))

def create_or_clear_collection(collection_name):
    # 检查集合是否已存在
    if collection_name in bpy.data.collections:
        existing_collection = bpy.data.collections.get(collection_name)
        try:
            bpy.context.scene.collection.children.link(existing_collection)
        except:
            pass
        # 删除集合中的所有物体
        for obj in existing_collection.objects:
            bpy.data.objects.remove(obj)
        # 隐藏集合
        existing_collection.hide_render = True
        existing_collection.hide_viewport = True
    else:
        # 创建一个新的集合
        new_collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(new_collection)
        # 隐藏集合
        new_collection.hide_render = True
        new_collection.hide_viewport = True

def create_mesh_from_dictionary(d,name):
    # 创建一个新的网格对象
    mesh = bpy.data.meshes.new(name=name)
    mesh.attributes.new(name='blockid', type="INT", domain="POINT")
    obj = bpy.data.objects.new(name, mesh)

    # 将对象添加到场景中
    scene = bpy.context.scene
    scene.collection.objects.link(obj)
    # 创建一个新的集合
    collection_name=name+"_Blocks"
    create_or_clear_collection(collection_name)
    collection =bpy.data.collections.get(collection_name)

    nodetree_target = "SchemToBlocks"

    #导入几何节点
    try:
        nodes_modifier.node_group = bpy.data.node_groups[collection_name]
    except:
        file_path = __file__.rsplit(
            "\\", 1)[0]+"\\GeometryNodes.blend"
        inner_path = 'NodeTree'
        object_name = nodetree_target
        bpy.ops.wm.append(
            filepath=os.path.join(file_path, inner_path, object_name),
            directory=os.path.join(file_path, inner_path),
            filename=object_name
        )
    # 创建顶点和顶点索引
    vertices = []
    ids = []  # 存储顶点id
    id_map = {}  # 用于将字符串id映射到数字的字典
    next_id = 0  # 下一个可用的数字id

    for coord, id_str in d.items():
        # 将字符串id映射到数字，如果id_str已经有对应的数字id，则使用现有的数字id
        if id_str not in id_map:
            filename=str(next_id)+str(id_str)
            textures,elements,rotation,_ =get_model(id_str)
            position = [0, 0, 0]
            has_air = [True, True, True, True, True, True]
            block(textures, elements, position,rotation, filename, has_air,collection)
            id_map[id_str] = next_id
            next_id += 1

        vertices.append((coord[0],-coord[1],coord[2]))
        # 将字符串id转换为相应的数字id
        ids.append(id_map[id_str])
    # 将顶点和顶点索引添加到网格中
    mesh.from_pydata(vertices, [], [])
    for i, item in enumerate(obj.data.attributes['blockid'].data):
        item.value=ids[i]
    # 设置顶点索引
    mesh.update()
    
    # 检查是否有节点修改器，如果没有则添加一个
    has_nodes_modifier = False
    for modifier in obj.modifiers:
        if modifier.type == 'NODES':
            has_nodes_modifier = True
            break
    if not has_nodes_modifier:
        obj.modifiers.new(name="SchemToBlocks",type="NODES")
    nodes_modifier=obj.modifiers[0]
    
    # 复制 SchemToBlocks 节点组并重命名为 CollectionName
    try:
        original_node_group = bpy.data.node_groups['SchemToBlocks']
        new_node_group = original_node_group.copy()
        new_node_group.name = collection_name
    except KeyError:
        print("error")
    #设置几何节点        
    nodes_modifier.node_group = bpy.data.node_groups[collection_name]
    bpy.data.node_groups[collection_name].nodes["集合信息"].inputs[0].default_value = collection
    nodes_modifier.show_viewport = True

#将普通网格体转换成mc
class ObjToBlocks(bpy.types.Operator):
    bl_idname = "baigave.objtoblocks"
    bl_label = "ObjToBlocks"

    def execute(self, context):
        start_time = time.time()
        nodetree_target = "ObjToBlocks"
        filename=context.active_object.name
        if contains_chinese(filename):
            message = "文件名包含中文字符，请改名!"
            ShowMessageBox(message)
            return {'FINISHED'}
        d = {}
        # 检查是否有节点修改器，如果没有则添加一个
        has_nodes_modifier = False
        for modifier in context.active_object.modifiers:
            if modifier.type == 'NODES':
                has_nodes_modifier = True
                break
        if not has_nodes_modifier:
            bpy.ops.object.modifier_add(type='NODES')
        nodes_modifier=context.active_object.modifiers[0]
        #导入几何节点
        try:
            nodes_modifier.node_group = bpy.data.node_groups[nodetree_target]
        except:
            file_path = __file__.rsplit(
                "\\", 1)[0]+"\\GeometryNodes.blend"
            inner_path = 'NodeTree'
            object_name = nodetree_target
            bpy.ops.wm.append(
                filepath=os.path.join(file_path, inner_path, object_name),
                directory=os.path.join(file_path, inner_path),
                filename=object_name
            )
        #设置几何节点        
        nodes_modifier.node_group = bpy.data.node_groups[nodetree_target]
        nodes_modifier.show_viewport = True


        # 在节点树中查找名为“值（明度）”的参数
        value_brightness = None
        for node in nodes_modifier.node_group.nodes:
            if node.type == 'VALUE':
                value_brightness = node
                break
         # 将“值（明度）”参数设置值为0.5
        if value_brightness:
            value_brightness.outputs[0].default_value = 0.5
        colors = self.get_colors(context)
        
        # 再次获取坐标信息
        coords = self.get_coords(context)
        #遍历坐标并根据布尔值列表进行判断
        for coord, values in coords.items():
            if values == [True, True, True, True, True, True, True, True]:
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_cube_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_cube_dict)
                    else:
                        closest_block_id = "minecraft:stone"

                #print(colors[coord]) #获取该方块的颜色值
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            #4F
            elif values == [False, False, False, True, False, True, True, True]:
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_slab_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_slab_dict)
                    else:
                        closest_block_id = "minecraft:stone_slab[type=bottom]"
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, True, True, False, True, False, False, False] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_slab_top_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_slab_top_dict)
                    else:
                        closest_block_id = "minecraft:stone_slab[type=top]"
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            #3F
            elif values == [True, True, True, False, True, False, False, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_outer_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_outer_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=west,half=top,shape=outer_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=west,half=top,shape=outer_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, True, True, True, True, False, False, False] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_outer_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_outer_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=east,half=top,shape=outer_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=east,half=top,shape=outer_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, True, True, False, True, False, True, False] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_outer_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_outer_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=south,half=top,shape=outer_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=south,half=top,shape=outer_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, True, True, False, True, True, False, False] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_outer_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_outer_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=north,half=top,shape=outer_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=north,half=top,shape=outer_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [False, False, False, True, True, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_outer_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_outer_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=west,half=bottom,shape=outer_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=west,half=bottom,shape=outer_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, False, False, True, False, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_outer_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_outer_stairs_dict)
                    else:
                        closest_block_id ="minecraft:stone_stairs[facing=east,half=bottom,shape=outer_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=east,half=bottom,shape=outer_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [False, False, True, True, False, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_outer_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_outer_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=south,half=bottom,shape=outer_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=south,half=bottom,shape=outer_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [False, True, False, True, False, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_outer_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_outer_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=north,half=bottom,shape=outer_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=north,half=bottom,shape=outer_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            #2F 
            elif values == [True, True, True, False, True, True, False, True] :#3 6
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=west,half=top,shape=straight]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=west,half=top,shape=straight"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, True, True, True, True, False, True, False] :#5 7
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=east,half=top,shape=straight]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=east,half=top,shape=straight"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =closest_block_id
            elif values == [False, True, False, True, True, True, True, True] :#0 2
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=west,half=bottom,shape=straight]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=west,half=bottom,shape=straight"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =closest_block_id
            elif values == [True, False, True, True, False, True, True, True] :#1 4
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_stairs_dict)
                    else:
                        closest_block_id ="minecraft:stone_stairs[facing=east,half=bottom,shape=straight]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=east,half=bottom,shape=straight"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =closest_block_id
            elif values == [True, True, True, True, True, True, False, False] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=north,half=top,shape=straight]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=north,half=top,shape=straight"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, True, True, False, True, False, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=south,half=top,shape=straight]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=south,half=top,shape=straight"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =closest_block_id
            elif values == [True, True, False, True, False, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_stairs_dict)
                    else:
                        closest_block_id =  "minecraft:stone_stairs[facing=north,half=bottom,shape=straight]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=north,half=bottom,shape=straight"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [False, False, True, True, True, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_stairs_dict)
                    else:
                        closest_block_id ="minecraft:stone_stairs[facing=south,half=bottom,shape=straight]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=south,half=bottom,shape=straight"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            #1F
            elif values == [True, True, True, True, True, False, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_inner_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_inner_stairs_dict)
                    else:
                        closest_block_id ="minecraft:stone_stairs[facing=south,half=top,shape=inner_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=south,half=top,shape=inner_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
    
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =closest_block_id
            elif values == [True, True, True, True, True, True, True, False] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_inner_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_inner_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=north,half=top,shape=inner_right]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=north,half=top,shape=inner_right"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, True, True, False, True, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_inner_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_inner_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=west,half=top,shape=inner_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=west,half=top,shape=inner_left]"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, True, True, True, True, True, False, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_inner_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_inner_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=west,half=top,shape=inner_right]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=west,half=top,shape=inner_right"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id

            elif values == [True, False, True, True, True, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_inner_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_inner_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=south,half=bottom,shape=inner_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=south,half=bottom,shape=inner_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, True, True, True, False, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_inner_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_inner_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=north,half=bottom,shape=inner_right]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=north,half=bottom,shape=inner_right"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =closest_block_id
            elif values == [False, True, True, True, True, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_inner_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_inner_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=west,half=bottom,shape=inner_left]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=west,half=bottom,shape=inner_left"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            elif values == [True, True, False, True, True, True, True, True] :
                if coord in colors:
                    closest_block_id = find_closest_color(tuple(colors[coord]), color_inner_stairs_dict)
                else:
                    surrounding_colors = get_surrounding_colors(coord, colors)
                    if surrounding_colors:
                        avg_color = np.mean(surrounding_colors, axis=0)
                        closest_block_id = find_closest_color(tuple(avg_color), color_inner_stairs_dict)
                    else:
                        closest_block_id = "minecraft:stone_stairs[facing=west,half=bottom,shape=inner_right]"
                pattern = r"\[(.*?)\]"
                matches = re.search(pattern, closest_block_id)

                if matches:
                    original_content = matches.group(1)
                    new_content = "facing=west,half=bottom,shape=inner_right"
                    closest_block_id = closest_block_id.replace(f"[{original_content}]", f"[{new_content}]")
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = closest_block_id
            
            

                #print(-int(coord[0]), -int(coord[1]), int(coord[2]))
        end_time = time.time()
        print("代码块执行时间：", end_time - start_time, "秒")

        start_time = time.time()
        create_mesh_from_dictionary(d,filename)
        end_time = time.time()
        print("代码块执行时间：", end_time - start_time, "秒")
        threading.Thread(target=export_schem, args=(d,filename,)).start()
        # 启动线程
        #nbt(d)
        # export_schem(d)
        # level = amulet.load_level(file_path)
        
        # for position, block in d.items():
        #     parts = block.split(':')
        #     block =amulet.api.block.Block(parts[0],parts[1])
        #     level.set_version_block(position[0],position[1],position[2],"main",("java", (1, 20, 0)),block)
        # level.save()
        # level.close()
        nodes_modifier.show_viewport = False
        return {'FINISHED'}
    

    # 获取顶点坐标
    def get_coords(self,context):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj = bpy.context.active_object.evaluated_get(depsgraph)
        
        # 获取顶点坐标
        coords = np.zeros(len(obj.data.vertices) * 3, dtype=float)
        obj.data.vertices.foreach_get("co", coords)
        coords = coords.reshape(len(obj.data.vertices), 3)
        # 获取所有向下取整后的坐标
        rounded_coords = [tuple(np.floor(coord).astype(int)) for coord in coords]
        
        # 创建字典来存储向下取整后的坐标及其情况
        coord_dict = defaultdict(lambda: [False] * 8)
        for rounded_coord in rounded_coords:
            coord_dict[rounded_coord]
        
        for rounded_coord in rounded_coords:
            x, y, z = rounded_coord
            coord_dict[(x, y, z)][0] = True
            coord_dict[(x + 1, y, z)][1] = True
            coord_dict[(x, y + 1, z)][2] = True
            coord_dict[(x, y, z + 1)][3] = True
            coord_dict[(x + 1, y + 1, z)][4] = True
            coord_dict[(x + 1, y, z + 1)][5] = True
            coord_dict[(x, y + 1, z + 1)][6] = True
            coord_dict[(x + 1, y + 1, z + 1)][7] = True
        
        return dict(coord_dict)
    def get_colors(self, context):
        colors = {}  # 创建空字典以存储坐标和颜色值

        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj = bpy.context.active_object.evaluated_get(depsgraph)

        # 检查 'color' 属性是否存在并且不为空
        if 'color' in obj.data.attributes and obj.data.attributes['color'].data:
            # 获取 'color' 属性列表
            color_attr = obj.data.attributes['color'].data

            # 获取顶点坐标
            coords = np.zeros(len(obj.data.vertices) * 3, dtype=float)
            obj.data.vertices.foreach_get("co", coords)
            coords = coords.reshape(len(obj.data.vertices), 3)

            # 将坐标和颜色值对应存储在字典中
            for i, item in enumerate(color_attr):
                color_values = [round(c, 2) for c in item.color[:]]  # 取两位小数
                coord = tuple(coords[i])
                colors[coord] = color_values

        return colors


classes=[ObjToBlocks]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)