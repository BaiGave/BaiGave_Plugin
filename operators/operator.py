import bpy
import os
import time
import random
import pickle
import threading
import subprocess
import re
import math

from .block import block
from .level import create_level
from .tip import button_callback

from .functions import get_all_data
#from .schem import schem,schem_p,schem_leaves,schem_liquid,schem_dirtgrass,schem_snow,schem_deepstone,schem_sandgravel
from .schem import schem_all,schem_liquid
from .generate import generate
from .chunk  import chunk as create_chunk
from .schem import schem_all

import gzip
import amulet
import amulet_nbt
import zipfile
import numpy as np
from collections import defaultdict
from ..colors import color_cube_dict,color_inner_stairs_dict,color_outer_stairs_dict,color_slab_dict,color_slab_top_dict,color_stairs_dict

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

#新功能 将普通网格体转换成mc的
class ObjToBlocks(bpy.types.Operator):
    bl_idname = "baigave.objtoblocks"
    bl_label = "ObjToBlocks"

    def execute(self, context):
        nodetree_target = "ObjToBlocks"
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
            value_brightness.outputs[0].default_value = 1.0
        colors = self.get_colors(context)
        # 将“值（明度）”参数设置值为0.5
        if value_brightness:
            value_brightness.outputs[0].default_value = 0.5
        
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
        schem_all(d)
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

class Read_mods_dir(bpy.types.Operator):
    """读取目录"""
    bl_idname = "baigave.read_mods_dir"
    bl_label = "读取目录"
    
    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        my_properties.mod_list.clear()

        path = scene.mods_dir  # 使用自定义路径

        for path, dirs, files in os.walk(path):
            for filename in files:
                if filename.lower().endswith(".jar"):  # 检查文件扩展名
                    # 将文件名添加到列表属性
                    item = my_properties.mod_list.add()
                    item.name = filename.replace(".jar", "")
        
        return {'FINISHED'}


# 定义 Operator 类 VIEW3D_read_dir
class Read_resourcepacks_dir(bpy.types.Operator):
    """读取目录"""
    bl_idname = "baigave.read_resourcepacks_dir"
    bl_label = "读取目录"
    
    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        my_properties.resourcepack_list.clear()

        path = scene.resourcepacks_dir  # 使用自定义路径

        for path, dirs, files in os.walk(path):
            for filename in files:
                if filename.lower().endswith(".zip"):  # 检查文件扩展名
                    # 将文件名添加到列表属性
                    item = my_properties.resourcepack_list.add()
                    item.name = filename.replace(".zip", "")
        return {'FINISHED'}
    

# 添加一个操作类来处理上下移动和删除模组
class MoveModItem(bpy.types.Operator):
    bl_idname = "my.move_mod_item"
    bl_label = "Move Mod Item"
    direction: bpy.props.StringProperty()  # 'UP' or 'DOWN'

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        mod_list = my_properties.mod_list
        index = my_properties.mod_list_index

        if self.direction == 'UP' and index > 0:
            mod_list.move(index, index - 1)
            my_properties.mod_list_index -= 1
        elif self.direction == 'DOWN' and index < len(mod_list) - 1:
            mod_list.move(index, index + 1)
            my_properties.mod_list_index += 1

        return {'FINISHED'}

class PRINT_SELECTED_ITEM(bpy.types.Operator):
    """打印选中的项目"""
    bl_idname = "view3d.print_selected_item"
    bl_label = "打印选中的项目"

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        selected_item = my_properties.resourcepack_list[my_properties.resourcepack_list_index]
        zip_file_path = context.scene.resourcepacks_dir + "\\" + selected_item.name + ".zip"  # 使用自定义路径
        mcmeta_content = ""

        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_file:
                if "pack.mcmeta" in zip_file.namelist():
                    with zip_file.open("pack.mcmeta") as mcmeta_file:
                        mcmeta_content = mcmeta_file.read().decode("utf-8")
                else:
                    self.report({'INFO'}, "文件 'pack.mcmeta' 不存在于.zip文件中。")
            self.report({'INFO'}, f"pack.mcmeta 内容：\n{mcmeta_content}")
        except Exception as e:
            self.report({'ERROR'}, f"无法打开或读取.zip文件: {e}")

        return {'FINISHED'}


class ImportNBT(bpy.types.Operator):
    bl_idname = "baigave.import_nbt"
    bl_label = "导入.nbt文件"
    
    # 定义一个属性来存储文件路径
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    # 定义一个属性来过滤文件类型，只显示.nbt文件
    filter_glob: bpy.props.StringProperty(default="*.nbt", options={'HIDDEN'})

    # 定义操作的执行函数
    def execute(self, context):
        # 获取文件路径
        filepath = self.filepath
        start_time = time.time()
        data = amulet_nbt.load(filepath)
        
        blocks =data["blocks"]
        entities = data["entities"]
        if "palette" in data:
            palette = data["palette"]
        elif "palettes" in data:
            palette = data["palettes"][3]
           

        size = data["size"]
        d = {}  

        for block in blocks:
            pos_tags = block['pos']  
            pos = tuple(tag.value for tag in pos_tags)  
            state = block['state'].value 
            block_name = palette[state]['Name'].value if 'Name' in palette[state] else palette[state]['nbt']['name'].value
            if 'Properties' in palette[state]:
                block_state = palette[state]['Properties'].value
                block_state = ', '.join([f'{k}={v}' for k, v in block_state.items()])
            elif 'nbt' in palette[state] and 'name' in palette[state]['nbt']:
                block_state = palette[state]['nbt']['name'].value
                block_state = ', '.join([f'{k}={v}' for k, v in block_state.items()])
            else:
                block_state = None
            
            if block_state is not None:
                d[(pos[0],pos[2],pos[1])] = str(block_name)+"["+block_state+"]"
            else:
                d[(pos[0],pos[2],pos[1])] = block_name
        end_time = time.time()
        print("代码块执行时间：", end_time - start_time, "秒")
        schem_all(d)
        
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# 定义一个导入.schem文件的操作类
class ImportSchem(bpy.types.Operator):
    bl_idname = "baigave.import_schem"
    bl_label = "导入.schem文件"
    
    # 定义一个属性来存储文件路径
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    # 定义一个属性来过滤文件类型，只显示.schem文件
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    # 定义操作的执行函数
    def execute(self, context):
        #清空缓存文件夹
        start_time = time.time()
        folder_path = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache"
        file_names = os.listdir(folder_path)
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            os.remove(file_path)
        
        
        # 遍历字典的键值对
        d = {}
        a = amulet.load_level(self.filepath)
        a.translation_manager.platforms()
        bounds =a.bounds("main").bounds
        chunks = [list(point) for point in bounds]

        nbt_data = amulet_nbt._load_nbt.load(self.filepath)
        size = {
            "x":int(nbt_data["Width"]),
            "y":int(nbt_data["Height"]),
            "z":int(nbt_data["Length"])
        }

        # 设置图片的大小和颜色
        image_width = int(size["z"])
        image_height = int(size["x"])
        default_color = (0.47, 0.75, 0.35, 1.0)  # RGBA颜色，对应#79c05a

        # 创建一个新的图片
        filename = os.path.basename(self.filepath)
        image = bpy.data.images.new("colormap", width=image_width, height=image_height)
        image.use_fake_user = True

        #设置默认颜色
        for y in range(image_height):
            for x in range(image_width):
                pixel_index = (y * image_width + x) * 4  # RGBA每个通道都是4个值
                image.pixels[pixel_index : pixel_index + 4] = default_color

        #小模型，直接导入
        if (chunks[1][0]-chunks[0][0])*(chunks[1][1]-chunks[0][1])*(chunks[1][2]-chunks[0][2])<10000:
            #print(chunks)
            # 遍历边界内的每个坐标
            for x in range(chunks[0][0], chunks[1][0]):
                for y in range(chunks[0][1], chunks[1][1]):
                    for z in range(chunks[0][2], chunks[1][2]):
                        # 获取坐标处的方块
                        id = a.get_block(x, y, z, "main")
                        id =str(a.translation_manager.get_version("java", (1, 20, 0)).block.from_universal(id)[0])
                        #block = convert_block_state(block)
                        # 将方块和坐标添加到字典中
                        d[(x-chunks[0][0], z-chunks[0][2], y-chunks[0][1])] = id.replace('"', '')
            
            #测试，把每个方块都单独作为一个物体生成出来
            schem_all(d)
            schem_liquid(d)
            #测试 单独导出自定义方块
            #schem(d)
            materials = bpy.data.materials
            for material in materials:
                try:
                    node_tree = material.node_tree
                    nodes = node_tree.nodes
                    for node in nodes:
                        if node.type == 'TEX_IMAGE':
                            if node.name == '色图':
                                node.image = bpy.data.images.get("colormap")
                except:
                    pass
            end_time = time.time()
            print("预处理时间：", end_time - start_time, "秒")

        #大模型，多进程
        else:
            n = (os.cpu_count())/2 #cpu核心数
            prime_factor = 2
            factors = []
            while prime_factor**2 <= n:
                if n % prime_factor:
                    prime_factor += 1
                else:
                    n //= prime_factor
                    factors.append(prime_factor)
            if n > 1:
                factors.append(n)

            factors.sort(reverse=True)  # 分解素因数，从大到小排序
            chunks.append(factors)  # 切割n个区块
            chunks=[chunks]
            while chunks[0][2] != []:
                i = 0
                while i < len(chunks):
                    subchunk = chunks[i]
                    dimensions = [subchunk[1][i] - subchunk[0][i] for i in range(3)]
                    max_dimension_index = dimensions.index(max(dimensions))
                    factor = subchunk[2].pop(0)
                    segment_length = dimensions[max_dimension_index] / factor
                    new_chunks = []
                    for j in range(int(factor)):
                        new_chunk = [list(subchunk[0]), list(subchunk[1]), list(subchunk[2])]
                        new_chunk[0][max_dimension_index] = math.floor(subchunk[0][max_dimension_index] + j * segment_length)
                        if j == factor - 1:  
                            new_chunk[1][max_dimension_index] = subchunk[1][max_dimension_index]
                        else:
                            new_chunk[1][max_dimension_index] = math.floor(new_chunk[0][max_dimension_index] + segment_length)
                        new_chunks.append(new_chunk)
                    chunks.pop(i)
                    chunks[i:i] = new_chunks
                    i += len(new_chunks)

            VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
            with open(VarCachePath, 'wb') as file:
                pickle.dump((chunks,self.filepath,bounds[0],filename),file)
            with open(VarCachePath, 'rb') as file:
                chunks,schempath,origin,filename = pickle.load(file)
        

            #多进程导入模型
            bpy.data.window_managers["WinMan"].bcp_max_connections = 64
            bpy.ops.wm.open_command_port()
            blender_path = bpy.app.binary_path
            ImportPath = bpy.utils.script_path_user()
            MultiprocessPath = ImportPath + "/addons/BaiGave_Plugin/multiprocess/schem_mp.py"

            #多进程实现方法：后台启动headless blender(-b)，只运行python代码(-P)，不显示界面
            for num in range(len(chunks)):
                ChunkIndex="import bpy;bpy.context.scene.frame_current = {}".format(num)
                subprocess.Popen([blender_path,"-b","--python-expr",ChunkIndex,"-P",MultiprocessPath])

        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


#每个进程调用一类功能，导入特定方块
class MultiprocessSchem(bpy.types.Operator):
    bl_idname = "baigave.import_schem_mp"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        start_time = time.time()
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            chunks,schempath,origin,filename = pickle.load(file)

        d={}
        a = amulet.load_level(schempath)
        current_frame = bpy.context.scene.frame_current
        subchunks=chunks[current_frame]
        for x in range(subchunks[0][0], subchunks[1][0]):
            for y in range(subchunks[0][1], subchunks[1][1]):
                for z in range(subchunks[0][2], subchunks[1][2]):
                    # 获取坐标处的方块
                    id = a.get_block(x, y, z, "main")
                    id =str(a.translation_manager.get_version("java", (1, 20, 0)).block.from_universal(id)[0])
                    #block = convert_block_state(block)
                    # 将方块和坐标添加到字典中
                    d[(x-subchunks[0][0], z-subchunks[0][2], y-subchunks[0][1])] = id.replace('"', '')
        
        size = {
            "x":int(subchunks[1][0]-subchunks[0][0]),
            "y":int(subchunks[1][1]-subchunks[0][1]),
            "z":int(subchunks[1][2]-subchunks[0][2])
        }
        #print(size)

        # 设置图片的大小和颜色
        image_width = int(size["z"])
        image_height = int(size["x"])
        default_color = (0.47, 0.75, 0.35, 1.0)  # RGBA颜色，对应#79c05a

        # 创建一个新的图片
        filename = os.path.basename(self.filepath)
        image = bpy.data.images.new(filename+"_colormap", width=image_width, height=image_height)

        #设置默认颜色
        for y in range(image_height):
            for x in range(image_width):
                pixel_index = (y * image_width + x) * 4  # RGBA每个通道都是4个值
                image.pixels[pixel_index : pixel_index + 4] = default_color

        schem_all(d)
        end_time = time.time()
        print("预处理时间：", end_time - start_time, "秒")

        obj = bpy.data.objects['Schemetics']
        obj.location = (subchunks[0][0]-origin[0],-(subchunks[0][2]-origin[2]),subchunks[0][1]-origin[1])
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/chunk{}.blend".format(current_frame)
        bpy.ops.wm.save_as_mainfile(filepath=ModelCachePath)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    

class ImportSchemLiquid(bpy.types.Operator):
    bl_idname = "baigave.import_schem_liquid"
    bl_label = "导入.schem文件"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.schem", options={'HIDDEN'})

    def execute(self, context):
        VarCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/var.pkl"
        with open(VarCachePath, 'rb') as file:
            d,schempath = pickle.load(file)
        schem_liquid(d,"liquid")
        ModelCachePath = bpy.utils.script_path_user() + "/addons/BaiGave_Plugin/schemcache/liquid.blend"
        bpy.ops.wm.save_as_mainfile(filepath=ModelCachePath)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class Importjson(bpy.types.Operator):
    """导入选定的json文件"""
    bl_idname = "baigave.import_json"
    bl_label = "导入json文件"

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        # 检查文件路径是否有效
        if os.path.isfile(self.filepath) and self.filepath.endswith(".json"):
            # 获取文件名
            filename = os.path.basename(self.filepath)
            textures, elements,parent = get_all_data(os.path.dirname(self.filepath)+"\\", filename)
            position = [0, 0, 0]
            has_air = [True, True, True, True, True, True]
            block(textures, elements, position,[0,0,0], filename, has_air)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "请选择有效的.json文件")
            return {'CANCELLED'}

    def invoke(self, context, event):
        # 打开文件选择对话框
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class GenerateWorld(bpy.types.Operator):
    """创建世界(未完成)"""
    bl_idname = "baigave.create_save"
    bl_label = "创建存档"

    # 定义操作的执行函数
    def execute(self, context):
        World_Name = "World1"
        SpawnX=0
        SpawnY=64
        SpawnZ=0
        hardcore=0
        Difficulty=0
        allowCommands=1
        LastPlayed = int(round(time.time() * 1000))
        DayTime=16000
        Seed = random.randint(0, 10000)


        folderpath = 'C:\\Users\\user\\Desktop\\白给的人模\\BaiGave_Plugin\\saves\\'+World_Name

        # 创建存档文件夹
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)
        level_dat = create_level(World_Name,SpawnX,SpawnY,SpawnZ,hardcore,Difficulty,allowCommands,LastPlayed,DayTime,Seed)
        # 将NBT数据写入文件
        filepath = 'C:\\Users\\user\\Desktop\\白给的人模\\BaiGave_Plugin\\saves\\'+World_Name+'\\level.dat'
        with gzip.open(filepath, 'wb') as file:
            level_dat.write(file)

        
        from amulet.api.chunk import Chunk
        from amulet.api.block import Block

        level = amulet.load_level("C:\\Users\\user\\Desktop\\白给的人模\\BaiGave_Plugin\\saves\\"+World_Name)
        new_chunk = Chunk(0, 0)
        stone = Block("minecraft", "stone")
        new_chunk.set_block(10,171,10,stone)
        new_chunk.changed = True
        level.put_chunk(new_chunk, "minecraft:overworld")

        level.save()

        level.close()

        
        return {'FINISHED'}
    
class SelectArea(bpy.types.Operator):
    """选择区域（性能有问题）"""
    bl_label = "选择区域"
    bl_idname = 'baigave.select'
    
    def execute(self, context):
        # 获取当前场景的名称
        current_scene = bpy.context.scene.name
        # 如果场景名称不为"地图"，则返回
        if current_scene != "地图":
            button_callback(self, context,"地图仍未创建！")
            return {'CANCELLED'}
        # 检查当前场景是否已经有名为"Map"的集合
        existing_collections = bpy.data.collections.values()
        for coll in existing_collections:
            if coll.name == "Map":
                button_callback(self, context,"已经存在选择框！(如果你删除了一些东西请连同集合一起删除）")
                return {'CANCELLED'}
        # 获取当前文件的路径
        current_path = os.path.dirname(os.path.abspath(__file__))
        # 拼接路径和文件名
        filepath = os.path.join(current_path, "Map.blend")
        # 从文件中加载名为"Map"的集合
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.collections = ["Map"]
        # 将集合链接到当前场景
        for coll in data_to.collections:
            if coll is not None:
                bpy.context.scene.collection.children.link(coll)
        return {'FINISHED'}


class ImportWorld(bpy.types.Operator):
    """导入世界(性能有问题)"""
    bl_label = "导入世界"
    bl_idname = 'baigave.import_world'

    current_chunk_index = 0  # 当前处理的区块索引

    def modal(self, context, event):
        if event.type == 'ESC':
            # 如果用户按下ESC键，停止模态操作
            return {'CANCELLED'}

        if self.current_chunk_index < len(self.processed_chunks):
            # 处理下一个区块
            chunk = self.processed_chunks[self.current_chunk_index]
            x = chunk.cx
            z = chunk.cz
            self.process_chunk(self.level,chunk, x, z)

            self.current_chunk_index += 1
        else:
            # 完成所有区块的处理
             # 获取当前时间
            end_time = time.time()

            # 计算代码块执行时间
            execution_time = end_time - self.start_time

            # 打印执行时间
            print("代码块执行时间：", execution_time, "秒")
            return {'FINISHED'}
        # 继续模态操作
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # 获取当前时间
        self.start_time = time.time()
        from .map import processed_chunks
        from .map import level
        self.level = level
        self.processed_chunks = []  # 重置处理过的区块列表

        # 获取选择区域的位置
        object_names = ["pos1", "pos2"]
        positions = {name: bpy.data.objects[name].matrix_world.translation * 1024 for name in object_names if name in bpy.data.objects}

        # 计算选择区域的范围
        x_values = [int(position.x) for position in positions.values()]
        z_values = [int(position.y) for position in positions.values()]
        min_x = min(x_values) // 16
        max_x = max(x_values) // 16
        min_z = min(z_values) // 16
        max_z = max(z_values) // 16

        # 获取需要处理的区块
        for chunk in processed_chunks:
            x = chunk.cx
            z = chunk.cz

            if min_x <= x <= max_x and min_z <= z <= max_z:
                self.processed_chunks.append(chunk)

        # 设置模态操作属性
        context.window_manager.modal_handler_add(self)

        # 启动模态操作
        return {'RUNNING_MODAL'}

    def process_chunk(self, level,chunk, x, z):
        vertices,faces,texture_list,uv_list,direction,uv_rotation_list = create_chunk(chunk, level)
        generate(x, z, vertices, faces, texture_list, uv_list, direction, uv_rotation_list)

classes=[ImportSchem,MultiprocessSchem,Importjson,ImportWorld,SelectArea, GenerateWorld,
         Read_resourcepacks_dir,Read_mods_dir, PRINT_SELECTED_ITEM,MoveModItem,ImportNBT,ObjToBlocks]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    