import os
import bpy
import bmesh
import numpy as np
import re
from .tip import ShowMessageBox
from ..register import register_blocks,create_or_clear_collection
from collections import defaultdict
from amulet_nbt import TAG_Compound, TAG_Int, ByteArrayTag ,IntArrayTag,ShortTag

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
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"schem",filename+".schem") # 设置你想要保存的文件路径
    #创建一个新的选中区域
    with open(file_path, "wb") as f:
        schem.save_to(f)


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
    nodetree_target = "Schem"

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
    id_map=register_blocks(list(set(d.values())))
    for coord, id_str in d.items():
        vertices.append((coord[0],-coord[1],coord[2]))
        id_str =re.escape(id_str)
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
        obj.modifiers.new(name="Schem",type="NODES")
    nodes_modifier=obj.modifiers[0]
    
    # 复制 Schem 节点组并重命名为 CollectionName
    try:
        original_node_group = bpy.data.node_groups['Schem']
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
    return obj
    
def create_node(color_dict, node_groups, node_type, next_id, id_map,group_name="",blocktype=0):
    node_0 = None

    if id_map ==register_blocks(color_dict.keys()):
        for group in node_groups:
            if group.name == group_name:
                node_collection = group.nodes.get("方块集合")
                try:
                    node_collection.inputs[0].default_value = bpy.data.collections["Blocks"]
                except:
                    register_blocks(None)
        return next_id,id_map
    else:
        first_id=next_id
        for color in color_dict.values():
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
                node_1.inputs[0].default_value = next_id
                node_1.inputs[1].default_value = color
                node_1.inputs[3].default_value = blocktype

                input_socket_0 = node_0.outputs[0]
                output_socket_1 = node_1.inputs[2]
                node_group.links.new(output_socket_1, input_socket_0)

                
                node_0 = node_1
                next_id +=1
        id_map=register_blocks(color_dict.keys())
    next_id = max(id_map.values()) + 1
    if node_group:
        output_socket_1 = node_1.outputs[0]
        node_output = node_group.nodes.get("组输出")
        node_output.location = (node_1.location.x + 200, node_1.location.y)
        input_socket_output = node_output.inputs[0]
        node_group.links.new(input_socket_output, output_socket_1)

        node_input =node_group.nodes.get("Group Input")
        node_first =node_group.nodes.get(str(first_id))
        node_0 = node_group.nodes.get("0")
        node_group.nodes.remove(node_0)
        node_group.links.new(node_input.outputs[0], node_first.inputs[2])
        


    
    return next_id,id_map
 
#将普通网格体转换成mc
class ObjToBlocks(bpy.types.Operator):
    bl_idname = "baigave.objtoblocks"
    bl_label = "ObjToBlocks"

    def execute(self, context):
        nodetree_target = "ObjToBlocks"
        obj= context.active_object
        filename=obj.name+"点云"
        d = {}
        # 检查是否有节点修改器，如果没有则添加一个
        has_nodes_modifier = False
        for modifier in obj.modifiers:
            if modifier.type == 'NODES':
                has_nodes_modifier = True
                break
        if not has_nodes_modifier:
            bpy.ops.object.modifier_add(type='NODES')
        nodes_modifier=obj.modifiers[0]
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
            
            
        points =create_points_from_dictionary(d,filename)

        # 获取物体上的所有修改器并移除它们
        for modifier in obj.modifiers:
            obj.modifiers.remove(modifier)

        # 检查是否有节点修改器，如果没有则添加一个
        has_nodes_modifier = False
        for modifier in obj.modifiers:
            if modifier.type == 'NODES':
                has_nodes_modifier = True
                break
        if not has_nodes_modifier:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_add(type='NODES')
            
        nodes_modifier = obj.modifiers[0]
        nodes_modifier.name="模型转换"
        context_node_tree = obj.name
        node_groups = bpy.data.node_groups
        # 尝试导入几何节点
        try:
            nodes_modifier.node_group = node_groups[context_node_tree]
        except:
            # 如果 context_node_tree 不存在，则检查 nodetree_target 是否存在，不存在则添加，存在则复制
            if nodetree_target not in node_groups:
                file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"blend_files","BlockBlender++.blend")
                inner_path = 'NodeTree'
                object_name = nodetree_target
                bpy.ops.wm.append(
                    filepath=os.path.join(file_path, inner_path, object_name),
                    directory=os.path.join(file_path, inner_path),
                    filename=object_name
                )
                # 复制 nodetree_target 并重命名为 context_node_tree
                node_tree = node_groups[nodetree_target].copy()
                node_tree.name = context_node_tree
            else:
                # 复制 nodetree_target 并重命名为 context_node_tree
                node_tree = node_groups[nodetree_target].copy()
                node_tree.name = context_node_tree
        # 设置几何节点
        nodes_modifier.node_group = node_groups[context_node_tree]
        nodes_modifier.show_viewport = True

        # 遍历对象的所有修改器
        for modifier in obj.modifiers:
            # 检查修改器名称是否为“模型转换”
            if modifier.name == '模型转换':
                # 设置名为“UV”的字符串值为“UVMap”
                if 'Input_58' in modifier:
                    modifier['Input_58'] = obj.data.uv_layers.active.name

        for group in node_groups:
            if group.name == context_node_tree:
                node_collection = group.nodes.get("物体信息")
                try:
                    node_collection.inputs[0].default_value = points
                except:
                    pass


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


class BlockBlender(bpy.types.Operator):
    bl_idname = "baigave.blockblender"
    bl_label = "BlockBlender"

    def execute(self, context):
        nodetree_target = "模型转换"
        scene = context.scene
        path = scene.colors_dir  # 使用自定义路径

        selected_version = bpy.context.scene.color_list

        # 读取选定的文件
        selected_file_path = os.path.join(path, selected_version)
        if os.path.exists(selected_file_path) and selected_file_path.endswith('.py'):
            dict={}            
            # 导入选择的文件并将其内容加载到字典中
            with open(selected_file_path, 'r') as file:
                exec(file.read(), {}, dict)

        # 创建一个新的集合
        id_map=register_blocks(None)
        next_id = max(id_map.values()) + 1

        node_groups = bpy.data.node_groups
        # 遍历所选的每个物体
        for obj in context.selected_objects:
            # 检查是否有节点修改器，如果没有则添加一个
            has_nodes_modifier = False
            for modifier in obj.modifiers:
                if modifier.type == 'NODES':
                    has_nodes_modifier = True
                    break
            if not has_nodes_modifier:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_add(type='NODES')
                
            nodes_modifier = obj.modifiers[0]
            nodes_modifier.name="模型转换"
            context_node_tree = obj.name
            # 尝试导入几何节点
            try:
                nodes_modifier.node_group = node_groups[context_node_tree]
            except:
                # 如果 context_node_tree 不存在，则检查 nodetree_target 是否存在，不存在则添加，存在则复制
                if nodetree_target not in node_groups:
                    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"blend_files","BlockBlender++.blend")
                    inner_path = 'NodeTree'
                    object_name = nodetree_target
                    bpy.ops.wm.append(
                        filepath=os.path.join(file_path, inner_path, object_name),
                        directory=os.path.join(file_path, inner_path),
                        filename=object_name
                    )
                    # 复制 nodetree_target 并重命名为 context_node_tree
                    node_tree = node_groups[nodetree_target].copy()
                    node_tree.name = context_node_tree
                else:
                    # 复制 nodetree_target 并重命名为 context_node_tree
                    node_tree = node_groups[nodetree_target].copy()
                    node_tree.name = context_node_tree
            # 设置几何节点
            nodes_modifier.node_group = node_groups[context_node_tree]
            nodes_modifier.show_viewport = True


            # 遍历对象的所有修改器
            for modifier in obj.modifiers:
                # 检查修改器名称是否为“模型转换”
                if modifier.name == '模型转换':
                    # 设置名为“UV”的字符串值为“UVMap”
                    if 'Input_58' in modifier:
                        modifier['Input_58'] = obj.data.uv_layers.active.name
            for group in node_groups:
                if group.name == context_node_tree:
                    node_collection = group.nodes.get("方块集合")
                    try:
                        node_collection.inputs[0].default_value = bpy.data.collections["Blocks"]
                    except:
                        register_blocks(None)
                    node_number = group.nodes.get("普通方块数量")
                    node_number.inputs[0].default_value = len(dict['cube_dict'])

                    # 初始化总长度
                    all = 0

                    # 遍历主字典中的每个子字典，并将它们的长度相加
                    for key in dict:
                        all += len(dict[key])
                    node_number = group.nodes.get("所有数量")
                    node_number.inputs[0].default_value = all

            # 处理 cube
            next_id,id_map =create_node(dict['cube_dict'], node_groups, "普通方块", next_id, id_map,context_node_tree)
            # 处理 slab
            next_id,id_map =create_node(dict['slab_dict'], node_groups, "slab", next_id, id_map,blocktype=1)

            # 处理 slab_top
            next_id,id_map =create_node(dict['slab_top_dict'], node_groups, "slab_top", next_id, id_map,blocktype=2)

            next_id,id_map =create_node(dict['stairs_west_top_outer_left'], node_groups, "stairs_west_top_outer_left", next_id, id_map,blocktype=3)
            next_id,id_map =create_node(dict['stairs_east_top_outer_left'], node_groups, "stairs_east_top_outer_left", next_id, id_map,blocktype=4)
            next_id,id_map =create_node(dict['stairs_south_top_outer_left'], node_groups, "stairs_south_top_outer_left", next_id, id_map,blocktype=5)
            next_id,id_map =create_node(dict['stairs_north_top_outer_left'], node_groups, "stairs_north_top_outer_left", next_id, id_map,blocktype=6)
            next_id,id_map =create_node(dict['stairs_west_bottom_outer_left'], node_groups, "stairs_west_bottom_outer_left", next_id, id_map,blocktype=7)
            next_id,id_map =create_node(dict['stairs_east_bottom_outer_left'], node_groups, "stairs_east_bottom_outer_left", next_id, id_map,blocktype=8)
            next_id,id_map =create_node(dict['stairs_south_bottom_outer_left'], node_groups, "stairs_south_bottom_outer_left", next_id, id_map,blocktype=9)
            next_id,id_map =create_node(dict['stairs_north_bottom_outer_left'], node_groups, "stairs_north_bottom_outer_left", next_id, id_map,blocktype=10)
            next_id,id_map =create_node(dict['stairs_west_top_straight'], node_groups, "stairs_west_top_straight", next_id, id_map,blocktype=11)
            next_id,id_map =create_node(dict['stairs_east_top_straight'], node_groups, "stairs_east_top_straight", next_id, id_map,blocktype=12)
            next_id,id_map =create_node(dict['stairs_west_bottom_straight'], node_groups, "stairs_west_bottom_straight", next_id, id_map,blocktype=13)
            next_id,id_map =create_node(dict['stairs_east_bottom_straight'], node_groups, "stairs_east_bottom_straight", next_id, id_map,blocktype=14)
            next_id,id_map =create_node(dict['stairs_north_top_straight'], node_groups, "stairs_north_top_straight", next_id, id_map,blocktype=15)
            next_id,id_map =create_node(dict['stairs_south_top_straight'], node_groups, "stairs_south_top_straight", next_id, id_map,blocktype=16)
            next_id,id_map =create_node(dict['stairs_north_bottom_straight'], node_groups, "stairs_north_bottom_straight", next_id, id_map,blocktype=17)
            next_id,id_map =create_node(dict['stairs_south_bottom_straight'], node_groups, "stairs_south_bottom_straight", next_id, id_map,blocktype=18)
            next_id,id_map =create_node(dict['stairs_south_top_inner_left'], node_groups, "stairs_south_top_inner_left", next_id, id_map,blocktype=19)
            next_id,id_map =create_node(dict['stairs_north_top_inner_right'], node_groups, "stairs_north_top_inner_right", next_id, id_map,blocktype=20)
            next_id,id_map =create_node(dict['stairs_west_top_inner_left'], node_groups, "stairs_west_top_inner_left", next_id, id_map,blocktype=21)
            next_id,id_map =create_node(dict['stairs_west_top_inner_right'], node_groups, "stairs_west_top_inner_right", next_id, id_map,blocktype=22)
            next_id,id_map =create_node(dict['stairs_south_bottom_inner_left'], node_groups, "stairs_south_bottom_inner_left", next_id, id_map,blocktype=23)
            next_id,id_map =create_node(dict['stairs_north_bottom_inner_right'], node_groups, "stairs_north_bottom_inner_right", next_id, id_map,blocktype=24)
            next_id,id_map =create_node(dict['stairs_west_bottom_inner_left'], node_groups, "stairs_west_bottom_inner_left", next_id, id_map,blocktype=25)
            next_id,id_map =create_node(dict['stairs_west_bottom_inner_right'], node_groups, "stairs_west_bottom_inner_right", next_id, id_map,blocktype=26)

            for group in node_groups:
                if group.name == "改变id组":
                    node_group = group
            
                    
            # 尝试从 .blend 文件中获取文本数据
            text_data = bpy.data.texts.get("Blocks.py")
            if not text_data:  # 如果文本数据不存在，则创建一个新的文本数据对象
                text_data = bpy.data.texts.new("Blocks.py")

            # 从文本数据中读取字典 id_map
            id_map_content = text_data.as_string()
            try:
                id_map = eval(id_map_content)  # 尝试解析文件内容为字典
            except SyntaxError:  # 如果解析失败，即文件内容不是有效的Python字典表示
                id_map = {}  # 初始化为空字典
            node_0 = None
            for index in range(len(id_map)):
                if node_group:
                    if node_0 is None:
                        node_0 = node_group.nodes.get("-1")
                        if node_0 == None:
                            return {'FINISHED'}
                    node_1 = node_group.nodes.new(type=node_0.bl_idname)
                    node_1.location = (node_0.location.x + 200, node_0.location.y)
                    node_1.node_tree = bpy.data.node_groups.get(node_0.node_tree.name)
                    node_1.name = str(index)
                    node_1.inputs[0].default_value = index
                    node_1.inputs[1].default_value = index

                    input_socket_0 = node_0.outputs[0]
                    output_socket_1 = node_1.inputs[2]
                    node_group.links.new(output_socket_1, input_socket_0)
                    node_0 = node_1
            if node_group:
                output_socket_1 = node_1.outputs[0]
                node_output = node_group.nodes.get("组输出")
                node_output.location = (node_1.location.x + 200, node_1.location.y)
                input_socket_output = node_output.inputs[0]
                node_group.links.new(input_socket_output, output_socket_1)

                node_input =node_group.nodes.get("组输入")
                node_first =node_group.nodes.get("0")
                node_0 = node_group.nodes.get("-1")
                node_group.nodes.remove(node_0)
                node_group.links.new(node_input.outputs[0], node_first.inputs[2])
                


        return {'FINISHED'}



class MergeOverlappingFaces(bpy.types.Operator):
    bl_idname = "baigave.merge_overlapping_faces"
    bl_label = "合并重叠面"

    @classmethod
    def poll(cls, context):
        return context.selected_objects and all(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        # 创建一个集合用于存储面的数据
        face_data = {}
        
        # 遍历所有选中的网格体
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                mesh = obj.data
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')  # 切换到编辑模式
                bpy.ops.mesh.select_all(action='DESELECT')  # 取消选择所有面
                bm = bmesh.from_edit_mesh(mesh)
                bm.faces.ensure_lookup_table()
                
                # 遍历所有的面，将面的数据存储在字典中
                for face in bm.faces:
                    vertices = tuple(sorted((v.co.copy().freeze() for v in face.verts)))
                    if vertices not in face_data:
                        face_data[vertices] = {'faces': []}
                    face_data[vertices]['faces'].append((face, bm))

        # 遍历面数据字典，找到所有顶点都重合的面
        for vertices, data in face_data.items():
            if len(data['faces']) > 1:
                # 如果出现重复的面，则选择这些面
                for face in data['faces']:
                    bm =face[1]
                    bm.faces[face[0].index].select_set(True)

        # 删除重叠的面
        bpy.ops.mesh.delete(type='FACE')

        # 更新网格
        bmesh.update_edit_mesh(mesh)

        bpy.ops.object.mode_set(mode='OBJECT')  # 切换回对象模式

        return {'FINISHED'}



classes=[ObjToBlocks,BlockBlender,MergeOverlappingFaces]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)