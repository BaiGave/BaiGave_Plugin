import os
import bpy
from ..block import block
import numpy as np
import importlib
from ... import colors
import time
from .tip import ShowMessageBox
from collections import defaultdict
from amulet_nbt import TAG_Compound, TAG_Int, ByteArrayTag ,IntArrayTag,ShortTag
from ..blockstates import get_model

# 全局缓存来存储计算结果
distance_cache = {}


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
    #创建一个新的选中区域
    with open(file_path, "wb") as f:
        schem.save_to(f)

def create_or_clear_collection(collection_name):
    # 检查集合是否已存在
    if collection_name in bpy.data.collections:
        existing_collection = bpy.data.collections.get(collection_name)
        try:
            bpy.context.scene.collection.children.link(existing_collection)
        except:
            pass
        
        # 删除集合中的所有物体
        # for obj in existing_collection.objects:
        #     bpy.data.objects.remove(obj)
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
    mesh.attributes.new(name='biome', type="FLOAT_COLOR", domain="POINT")
    obj = bpy.data.objects.new(name, mesh)

    # 将对象添加到场景中
    scene = bpy.context.scene
    scene.collection.objects.link(obj)
    # 创建一个新的集合
    collection_name="Blocks"
    create_or_clear_collection(collection_name)
    collection =bpy.data.collections.get(collection_name)
    id_map = {}  # 用于将字符串id映射到数字的字典
    next_id = 0  # 初始化 next_id
    if not collection.objects:
        filename=str(next_id)+"#"+str("minecraft:air")
        textures,elements,rotation,_ =get_model("minecraft:air")
        position = [0, 0, 0]
        has_air = [True, True, True, True, True, True]
        bloc=block(textures, elements, position,rotation, filename, has_air,collection)
        bloc.data.attributes.new(name='blockname', type="STRING", domain="FACE")
        for i, item in enumerate(bloc.data.attributes['blockname'].data):
            item.value="minecraft:air"
        id_map["minecraft:air"] = next_id
        next_id =next_id+1
    elif collection.objects:
        # 遍历集合中的每个物体
        for ob in collection.objects:
            # 假设属性名称为 'blockname'，如果属性存在
            if 'blockname' in ob.data.attributes:
                # 获取属性值
                try:
                    attr_value = ob.data.attributes['blockname'].data[0].value
                except:
                    attr_value = "minecraft:air"
                # 获取物体ID（假设ID是以#分隔的字符串的第一个部分）
                obj_id = ob.name.split('#')[0]
                # 将字符串类型的ID转换为整数
                try:
                    obj_id_int = int(obj_id)
                    # 找到最大ID
                    if obj_id_int > next_id:
                        next_id = obj_id_int
                except ValueError:
                    pass
                # 将 ID 与属性值关联起来并存储到字典中
                id_map[attr_value] = int(obj_id)
        next_id =next_id+1
    
    nodetree_target = "SchemToBlocks"

    #导入几何节点
    try:
        nodes_modifier.node_group = bpy.data.node_groups[collection_name]
    except:
        file_path =bpy.context.scene.geometrynodes_blend_path
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
    for coord, id_str in d.items():
        # 将字符串id映射到数字，如果id_str已经有对应的数字id，则使用现有的数字id
        if id_str not in id_map:
            filename=str(next_id)+"#"+str(id_str)
            textures,elements,rotation,_ =get_model(id_str)
            position = [0, 0, 0]
            has_air = [True, True, True, True, True, True]
            bloc=block(textures, elements, position,rotation, filename, has_air,collection)
            bloc.data.attributes.new(name='blockname', type="STRING", domain="FACE")
            for i, item in enumerate(bloc.data.attributes['blockname'].data):
                item.value=id_str
            id_map[id_str] = next_id
            next_id += 1

        vertices.append((coord[0],-coord[1],coord[2]))
        # 将字符串id转换为相应的数字id
        ids.append(id_map[id_str])
    # 将顶点和顶点索引添加到网格中
    mesh.from_pydata(vertices, [], [])
    for i, item in enumerate(obj.data.attributes['blockid'].data):
        item.value=ids[i]
    #群系上色
    for i, item in enumerate(obj.data.attributes['biome'].data):
        item.color[:]=(0.149,0.660,0.10,0.00)
    

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

def create_points_from_dictionary(d,name):
    # 创建一个新的网格对象
    mesh = bpy.data.meshes.new(name=name)
    mesh.attributes.new(name='blocktype', type="INT", domain="POINT")
    obj = bpy.data.objects.new(name, mesh)

    # 将对象添加到场景中
    scene = bpy.context.scene
    scene.collection.objects.link(obj)
    # 创建一个新的集合
    id_map = {}  # 用于将字符串id映射到数字的字典
    next_id = 0  # 初始化 next_id
 
    # 创建顶点和顶点索引
    vertices = []
    ids = []  # 存储顶点id
    for coord, id_str in d.items():
        # 将字符串id映射到数字，如果id_str已经有对应的数字id，则使用现有的数字id
        if id_str not in id_map:
            id_map[id_str] = next_id
            next_id += 1

        vertices.append((coord[0],-coord[1],coord[2]))
        # 将字符串id转换为相应的数字id
        ids.append(id_str)
    # 将顶点和顶点索引添加到网格中
    mesh.from_pydata(vertices, [], [])
    for i, item in enumerate(obj.data.attributes['blocktype'].data):
        item.value=ids[i]
    for i, item in enumerate(obj.data.attributes['blocktype'].data):
        print(item.value)
    
def create_node(color_dict, node_groups, node_type, next_id, id_map, collection):
    node_0 = None
    for color, color_value in color_dict.items():
        if color_value not in id_map:
            # 获取名为 node_type 的节点组
            node_group = None
            for group in node_groups:
                if group.name == node_type:
                    node_group = group

            # 如果找到了 node_type 节点组
            if node_group:
                if node_0 is None:
                    node_0 = node_group.nodes.get("0")
                node_1 = node_group.nodes.new(type=node_0.bl_idname)
                node_1.location = (node_0.location.x + 200, node_0.location.y)
                node_1.node_tree = bpy.data.node_groups.get(node_0.node_tree.name)
                node_1.name = str(next_id)
                node_1.inputs[3].default_value = next_id
                node_1.inputs[4].default_value = color

                # 连接节点的前三个输入口
                for i in range(3):
                    input_socket_0 = node_0.outputs[i]
                    output_socket_1 = node_1.inputs[i]
                    node_group.links.new(output_socket_1, input_socket_0)

                if node_type == node_type:
                    output_socket_1 = node_1.outputs[2]
                    node_output = node_group.nodes.get("组输出")
                    node_output.location = (node_1.location.x + 200, node_1.location.y)
                    input_socket_output = node_output.inputs[0]
                    node_group.links.new(input_socket_output, output_socket_1)

                node_0 = node_1

            # 创建 block
            filename = f"{next_id}#{color_value}"
            textures, elements, rotation, _ = get_model(color_value)
            position = [0, 0, 0]
            has_air = [True, True, True, True, True, True]
            bloc = block(textures, elements, position, rotation, filename, has_air, collection)
            bloc.data.attributes.new(name='blockname', type="STRING", domain="FACE")

            for i, item in enumerate(bloc.data.attributes['blockname'].data):
                item.value = color_value
            id_map[color_value] = next_id
            next_id += 1
    return next_id,id_map
class PrepareBlocks(bpy.types.Operator):
    bl_idname = "baigave.prepareblocks"
    bl_label = "PrepareBlocks"

    def execute(self, context):
        importlib.reload(colors)
        
        # 创建一个新的集合
        collection_name="Blocks"
        create_or_clear_collection(collection_name)
        collection =bpy.data.collections.get(collection_name)
        id_map = {}  # 用于将字符串id映射到数字的字典
        next_id = 0  # 初始化 next_id
        if not collection.objects:
            filename=str(next_id)+"#"+str("minecraft:air")
            textures,elements,rotation,_ =get_model("minecraft:air")
            position = [0, 0, 0]
            has_air = [True, True, True, True, True, True]
            bloc=block(textures, elements, position,rotation, filename, has_air,collection)
            bloc.data.attributes.new(name='blockname', type="STRING", domain="FACE")
            for i, item in enumerate(bloc.data.attributes['blockname'].data):
                item.value="minecraft:air"
            id_map["minecraft:air"] = next_id
            next_id += 1
        elif collection.objects:
            # 遍历集合中的每个物体
            for ob in collection.objects:
                # 假设属性名称为 'blockname'，如果属性存在
                if 'blockname' in ob.data.attributes:
                    # 获取属性值
                    try:
                        attr_value = ob.data.attributes['blockname'].data[0].value
                    except:
                        attr_value = "minecraft:air"
                    # 获取物体ID（假设ID是以#分隔的字符串的第一个部分）
                    obj_id = ob.name.split('#')[0]
                    # 将字符串类型的ID转换为整数
                    try:
                        obj_id_int = int(obj_id)
                        # 找到最大ID
                        if obj_id_int > next_id:
                            next_id = obj_id_int
                    except ValueError:
                        pass
                    # 将 ID 与属性值关联起来并存储到字典中
                    id_map[attr_value] = int(obj_id)
                
            next_id =next_id+1
        nodetree_target = "Blockblender"
        # 检查几何节点是否存在
        if nodetree_target not in bpy.data.node_groups.keys():
            # 指定节点组名称
            nodetree_target = "Blockblender"
            # 加载.blend文件
            with bpy.data.libraries.load(os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "codes","blend_files","BlockBlender.blend")) as (data_from, data_to):
                # 导入指定的节点组
                data_to.node_groups = [nodetree_target]
        node_groups = bpy.data.node_groups

        #设置几何节点        
        if "集合信息" in bpy.data.node_groups:
            bpy.data.node_groups["集合信息"].nodes["节点名称"].inputs[0].default_value = collection

        # 处理 cube
        next_id,id_map =create_node(colors.cube_dict, node_groups, "cube", next_id, id_map, collection)

        # 处理 slab
        next_id,id_map =create_node(colors.slab_dict, node_groups, "slab", next_id, id_map, collection)

        # 处理 slab_top
        next_id,id_map =create_node(colors.slab_top_dict, node_groups, "slab_top", next_id, id_map, collection)

        next_id,id_map =create_node(colors.stairs_west_top_outer_left, node_groups, "stairs_west_top_outer_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_east_top_outer_left, node_groups, "stairs_east_top_outer_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_south_top_outer_left, node_groups, "stairs_south_top_outer_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_north_top_outer_left, node_groups, "stairs_north_top_outer_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_west_bottom_outer_left, node_groups, "stairs_west_bottom_outer_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_east_bottom_outer_left, node_groups, "stairs_east_bottom_outer_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_south_bottom_outer_left, node_groups, "stairs_south_bottom_outer_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_north_bottom_outer_left, node_groups, "stairs_north_bottom_outer_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_west_top_straight, node_groups, "stairs_west_top_straight", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_east_top_straight, node_groups, "stairs_east_top_straight", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_west_bottom_straight, node_groups, "stairs_west_bottom_straight", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_east_bottom_straight, node_groups, "stairs_east_bottom_straight", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_north_top_straight, node_groups, "stairs_north_top_straight", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_south_top_straight, node_groups, "stairs_south_top_straight", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_north_bottom_straight, node_groups, "stairs_north_bottom_straight", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_south_bottom_straight, node_groups, "stairs_south_bottom_straight", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_south_top_inner_left, node_groups, "stairs_south_top_inner_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_north_top_inner_right, node_groups, "stairs_north_top_inner_right", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_west_top_inner_left, node_groups, "stairs_west_top_inner_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_west_top_inner_right, node_groups, "stairs_west_top_inner_right", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_south_bottom_inner_left, node_groups, "stairs_south_bottom_inner_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_north_bottom_inner_right, node_groups, "stairs_north_bottom_inner_right", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_west_bottom_inner_left, node_groups, "stairs_west_bottom_inner_left", next_id, id_map,  collection)
        next_id,id_map =create_node(colors.stairs_west_bottom_inner_right, node_groups, "stairs_west_bottom_inner_right", next_id, id_map,  collection)

        return {'FINISHED'}
#将普通网格体转换成mc
class ObjToBlocks(bpy.types.Operator):
    bl_idname = "baigave.objtoblocks"
    bl_label = "ObjToBlocks"

    def execute(self, context):
        start_time = time.time()
        nodetree_target = "ObjToBlocks"
        filename=context.active_object.name
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
            file_path =bpy.context.scene.geometrynodes_blend_path
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
        # 获取坐标信息
        coords = self.get_coords(context)
        #遍历坐标并根据布尔值列表进行判断
        for coord, values in coords.items():
            if values == [True, True, True, True, True, True, True, True]:
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = 0# "block"
            #4F
            elif values == [False, False, False, True, False, True, True, True]:
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))]  =1# "block_slab[type=bottom]"
            elif values == [True, True, True, False, True, False, False, False] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))]  =2# "block_slab[type=top]"
            #3F
            elif values == [True, True, True, False, True, False, False, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =3# "block_stairs[facing=west,half=top,shape=outer_left]"
            elif values == [True, True, True, True, True, False, False, False] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =4# "block_stairs[facing=east,half=top,shape=outer_left]"
            elif values == [True, True, True, False, True, False, True, False] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =5# "block_stairs[facing=south,half=top,shape=outer_left]"
            elif values == [True, True, True, False, True, True, False, False] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =6# "block_stairs[facing=north,half=top,shape=outer_left]"
            elif values == [False, False, False, True, True, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =7# "block_stairs[facing=west,half=bottom,shape=outer_left]"
            elif values == [True, False, False, True, False, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =8# "block_stairs[facing=east,half=bottom,shape=outer_left]"
            elif values == [False, False, True, True, False, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =9#  "block_stairs[facing=south,half=bottom,shape=outer_left]"
            elif values == [False, True, False, True, False, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =10# "block_stairs[facing=north,half=bottom,shape=outer_left]"
            #2F 
            elif values == [True, True, True, False, True, True, False, True] :#3 6
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =11#  "block_stairs[facing=west,half=top,shape=straight]"
            elif values == [True, True, True, True, True, False, True, False] :#5 7
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =12#"block_stairs[facing=east,half=top,shape=straight]"
            elif values == [False, True, False, True, True, True, True, True] :#0 2
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =13#"block_stairs[facing=west,half=bottom,shape=straight]"
            elif values == [True, False, True, True, False, True, True, True] :#1 4
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =14#"block_stairs[facing=east,half=bottom,shape=straight]"
            elif values == [True, True, True, True, True, True, False, False] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =15# "block_stairs[facing=north,half=top,shape=straight]"
            elif values == [True, True, True, False, True, False, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =16#"block_stairs[facing=south,half=top,shape=straight]"
            elif values == [True, True, False, True, False, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] = 17# "block_stairs[facing=north,half=bottom,shape=straight]"
            elif values == [False, False, True, True, True, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =18# "block_stairs[facing=south,half=bottom,shape=straight]"
            #1F
            elif values == [True, True, True, True, True, False, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =19#"block_stairs[facing=south,half=top,shape=inner_left]"
            elif values == [True, True, True, True, True, True, True, False] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =20# "block_stairs[facing=north,half=top,shape=inner_right]"
            elif values == [True, True, True, False, True, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =21# "block_stairs[facing=west,half=top,shape=inner_left]"
            elif values == [True, True, True, True, True, True, False, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =22# "block_stairs[facing=west,half=top,shape=inner_right]"

            elif values == [True, False, True, True, True, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =23# "block_stairs[facing=south,half=bottom,shape=inner_left]"
            elif values == [True, True, True, True, False, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =24#"block_stairs[facing=north,half=bottom,shape=inner_right]"
            elif values == [False, True, True, True, True, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =25# "block_stairs[facing=west,half=bottom,shape=inner_left]"
            elif values == [True, True, False, True, True, True, True, True] :
                d[(int(coord[0])-1, -int(coord[1]), int(coord[2]))] =26# "block_stairs[facing=west,half=bottom,shape=inner_right]"
            
            

        end_time = time.time()
        print("代码块执行时间：", end_time - start_time, "秒")

        start_time = time.time()
        create_points_from_dictionary(d,filename)
        end_time = time.time()
        print("代码块执行时间：", end_time - start_time, "秒")
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


#将普通网格体转换成mc
class BlockBlender(bpy.types.Operator):
    bl_idname = "baigave.blockblender"
    bl_label = "BlockBlender"

    def execute(self, context):
        nodetree_target = "BlockBlender1.41"
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
            file_path =os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "codes","blend_files","BlockBlender.blend")
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
        # 存储图像节点和对应的名称
        image_nodes = {}
        
        # 遍历物体的所有材质
        for slot in context.active_object.material_slots:
            material = slot.material
            if material:
                # 检查每个材质的节点
                if material.use_nodes:
                    nodes = material.node_tree.nodes
                    principled_node = None
                    image_node = None
                    # 遍历材质节点，寻找原理化 BSDF 和图像节点
                    for node in nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            principled_node = node
                        elif node.type == 'TEX_IMAGE':
                            image_node = node
                    # 如果找到了原理化 BSDF 和图像节点
                    if principled_node and image_node:
                        # 检查是否连接
                        connected = False
                        for link in material.node_tree.links:
                            if link.to_node == principled_node and link.to_socket == principled_node.inputs[0]:
                                connected = True
                                break
                        if connected:
                            image = image_node.image
                            if image:
                                image_nodes[slot.slot_index] = image
                            
        # 遍历组输入节点，将图像与之对应
        for group_input_name, image in image_nodes.items():
            # 假设 nodes_modifier 是您的几何节点修改器
            node_tree = nodes_modifier.node_group.nodes
            # 寻找对应的组输入节点
            for group_input in node_tree:
                if  group_input.name == f"图像{group_input_name+1}":
                    group_input.image = image
                    break
        return {'FINISHED'}
    
class AddFaceAttributeOperator(bpy.types.Operator):
    bl_idname = "baigave.add_face_attribute"
    bl_label = "添加面属性值"
    
    def execute(self, context):
        # 获取当前选中的对象
        obj = context.object
        obj.data.attributes.new(name='blockname', type="STRING", domain="FACE")
        for i, item in enumerate(obj.data.attributes['blockname'].data):
            item.value=obj.name.split("#", 1)[1]
        return {'FINISHED'}
classes=[PrepareBlocks,ObjToBlocks,AddFaceAttributeOperator,BlockBlender]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)