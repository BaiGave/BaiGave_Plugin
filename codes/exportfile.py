import os
import bpy
import bmesh
import amulet
from amulet.api.block import Block
from amulet_nbt import TAG_Compound, TAG_Int, ByteArrayTag ,IntArrayTag,ShortTag,TAG_String
from .functions.tip import ShowMessageBox

class OpenSaves_FileManagerOperator(bpy.types.Operator):
    bl_idname = "baigave.open_saves_folder_s"
    bl_label = "打开文件管理器"

    def execute(self, context):
        # 构建路径
        folderpath = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "saves")

        # 打开文件管理器并导航到指定路径
        bpy.ops.wm.path_open(filepath=folderpath)

        return {'FINISHED'}

class OpenFileManagerOperator(bpy.types.Operator):
    bl_idname = "baigave.opem_schem_folder"
    bl_label = "打开文件管理器"

    def execute(self, context):
        # 构建路径
        folderpath = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "schem")

        # 打开文件管理器并导航到指定路径
        bpy.ops.wm.path_open(filepath=folderpath)

        return {'FINISHED'}
class ExportSchem(bpy.types.Operator):
    """导出选定的区域为.schem文件"""
    bl_idname = "baigave.export_schem"
    bl_label = "导出.schem文件"
    vertex_dict = {} 
    block_id_name_map = {}  # 创建一个字典来存储 ID 和方块名称的映射
    filename ="schem"

    def execute(self, context):
        self.filename = context.scene.schem_filename
         # 创建空字典来存储顶点数据
        selected_objects = bpy.context.selected_objects
        self.vertex_dict = {} 
        collection =bpy.data.collections.get("Blocks")
        if collection.objects:
            # 遍历集合中的每个物体
            for o in collection.objects:
                # 假设属性名称为 'blockname'，如果属性存在
                if 'blockname' in o.data.attributes:
                    # 获取属性值
                    try:
                        attr_value = o.data.attributes['blockname'].data[0].value
                    except:
                        # 获取物体ID（假设ID是以#分隔的字符串的第一个部分）
                        air_id = int(o.name.split('#')[0])
                        id =air_id
                        attr_value = "minecraft:air"
                    id = int(o.name.split('#')[0])
                    self.block_id_name_map[id] = attr_value
        for obj in selected_objects:
            if obj.type == 'MESH':
                mesh = obj.data
                vertices = mesh.vertices

                for vertex in vertices:
                    coord = tuple([int(coord) for coord in (obj.matrix_world @ vertex.co)])  # 将顶点坐标转换为元组，以便用作字典键

                    # 如果顶点坐标已经存在于字典中，则跳过
                    if coord in self.vertex_dict:
                        continue

                    # 获取顶点属性值（blockid）
                    blockid = obj.data.attributes['blockid'].data[vertex.index].value
                    if blockid == air_id:
                        continue
                    # 将顶点坐标与属性值关联存储到字典中
                    self.vertex_dict[coord] = blockid
        self.export_schem(context)
        ShowMessageBox("文件导出成功！","白给的插件",link_text="点击这里前往导出文件夹", link_operator=OpenFileManagerOperator)
        return {'FINISHED'}
    def create_mesh(self,context):
        # 创建一个新的网格对象
        mes = bpy.data.meshes.new(name="test")
        bm = bmesh.new()
        ids=list(self.vertex_dict.values()) 
        # 添加顶点和面到新网格
        for coord, blockid in self.vertex_dict.items():
            vert = bm.verts.new(coord)
        bm.to_mesh(mes)
        bm.free()
        mes.attributes.new(name='blockid', type="INT", domain="POINT")
        for i, item in enumerate(mes.attributes['blockid'].data):
            item.value=ids[i]
        # 创建一个新的对象，并将新网格链接到场景
        ob = bpy.data.objects.new("test", mes)
        bpy.context.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)

    def export_schem(self,context):
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
        x_values = [int(coord[0]) for coord in self.vertex_dict.keys()]
        y_values = [int(coord[1]) for coord in self.vertex_dict.keys()]
        z_values = [int(coord[2]) for coord in self.vertex_dict.keys()]

        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)
        min_z, max_z = min(z_values), max(z_values)

        Width = max_x - min_x + 1
        Length = max_y - min_y + 1
        Height = max_z - min_z + 1
        block_data = [0] * (Length * Width * Height)


        for position, block in self.vertex_dict.items():
            block =self.block_id_name_map[block]
            # 如果方块不在 Palette 中，添加它
            if block not in schem['Palette']:
                schem['Palette'][block] = TAG_Int(palette_index)
                palette_index += 1

            # 计算索引并放置对应的方块id
            x, z, y = position
            x=int(x)
            y=int(y)
            z=int(z)
            index = ((y - min_z) * Length + (z- min_y)) * Width + (x - min_x)
            block_data[index] = schem['Palette'][block].value

        self.vertex_dict = {} 
        # 更新 PaletteMax 和 BlockData
        schem['PaletteMax'] = TAG_Int(palette_index)
        schem['Height'] = ShortTag(Height)
        schem['Width'] = ShortTag(Width)
        schem['Length'] = ShortTag(Length)
        schem['BlockData'] = ByteArrayTag(block_data)
        # 将NBT数据写入.schem文件
        file_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "schem",self.filename+".schem") # 设置你想要保存的文件路径
        #创建一个新的选中区域
        with open(file_path, "wb") as f:
            schem.save_to(f)

class Calculate_Size(bpy.types.Operator):
    """计算大小"""
    bl_idname = "baigave.calculate_size"
    bl_label = "计算大小"
    vertex_dict = {} 
    block_id_name_map = {}  # 创建一个字典来存储 ID 和方块名称的映射

    def execute(self, context):
         # 创建空字典来存储顶点数据
        selected_objects = bpy.context.selected_objects
        self.vertex_dict = {} 
        collection =bpy.data.collections.get("Blocks")

        min_coords = [float('inf')] * 3  
        max_coords = [float('-inf')] * 3 
        if collection.objects:
            # 遍历集合中的每个物体
            for o in collection.objects:
                # 假设属性名称为 'blockname'，如果属性存在
                if 'blockname' in o.data.attributes:
                    # 获取属性值
                    try:
                        attr_value = o.data.attributes['blockname'].data[0].value
                    except:
                        # 获取物体ID（假设ID是以#分隔的字符串的第一个部分）
                        air_id = int(o.name.split('#')[0])
                        id =air_id
                        attr_value = "minecraft:air"
                    id = int(o.name.split('#')[0])
                    self.block_id_name_map[id] = attr_value
        for obj in selected_objects:
            if obj.type == 'MESH':
                mesh = obj.data
                vertices = mesh.vertices

                for vertex in vertices:
                    coord = tuple([int(coord) for coord in (obj.matrix_world @ vertex.co)])  # 将顶点坐标转换为元组，以便用作字典键
                    # 如果顶点坐标已经存在于字典中，则跳过
                    if coord in self.vertex_dict:
                        continue

                    # 获取顶点属性值（blockid）
                    blockid = obj.data.attributes['blockid'].data[vertex.index].value
                    if blockid == air_id:
                        continue

                    # 更新最小和最大坐标
                    min_coords = [min(min_coords[i], coord[i]) for i in range(3)]
                    max_coords = [max(max_coords[i], coord[i]) for i in range(3)]

                    # 将顶点坐标与属性值关联存储到字典中
                    self.vertex_dict[coord] = blockid
        self.vertex_dict = {} 
        # 将浮点数坐标转换为整数
        min_coords = [int(coord) for coord in min_coords]
        max_coords = [int(coord) for coord in max_coords]

        # 计算长、宽和高
        length = max_coords[0] - min_coords[0]+1
        width = max_coords[1] - min_coords[1]+1
        height = max_coords[2] - min_coords[2]+1
        size = (length, width, height)

        context.scene.schem_size = size
        context.scene.schem_location = min_coords
        return {'FINISHED'}

class ExportToSave(bpy.types.Operator):
    """导出到存档"""
    bl_idname = "baigave.export_to_save"
    bl_label = "导出到存档"
    vertex_dict = {} 
    block_id_name_map = {}  # 创建一个字典来存储 ID 和方块名称的映射
    foldername =""

    def execute(self, context):
        self.foldername = context.scene.save_list
        worldpath = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "saves",self.foldername)
        level = amulet.load_level(worldpath)
         # 创建空字典来存储顶点数据
        selected_objects = bpy.context.selected_objects
        self.vertex_dict = {} 
        collection =bpy.data.collections.get("Blocks")

        if collection.objects:
            # 遍历集合中的每个物体
            for o in collection.objects:
                # 假设属性名称为 'blockname'，如果属性存在
                if 'blockname' in o.data.attributes:
                    # 获取属性值
                    try:
                        attr_value = o.data.attributes['blockname'].data[0].value
                    except:
                        # 获取物体ID（假设ID是以#分隔的字符串的第一个部分）
                        air_id = int(o.name.split('#')[0])
                        id =air_id
                        attr_value = "minecraft:air"
                    id = int(o.name.split('#')[0])
                    self.block_id_name_map[id] = attr_value
        for obj in selected_objects:
            if obj.type == 'MESH':
                mesh = obj.data
                vertices = mesh.vertices
                for vertex in vertices:
                    coord = tuple([int(coord) for coord in (obj.matrix_world @ vertex.co)])  # 将顶点坐标转换为元组，以便用作字典键
                    # 如果顶点坐标已经存在于字典中，则跳过
                    if coord in self.vertex_dict:
                        continue

                    # 获取顶点属性值（blockid）
                    blockid = obj.data.attributes['blockid'].data[vertex.index].value
                    if blockid == air_id:
                        continue

                    # 将顶点坐标与属性值关联存储到字典中
                    self.vertex_dict[coord] = blockid

        # 遍历坐标表
        for coordinates, block_id in self.vertex_dict.items():
            x, y, z = coordinates

            # 获取方块名称
            block_name = self.block_id_name_map.get(block_id, 'minecraft:air')
            if block_name != "minecraft:air":
                namespace, path = block_name.split(':')
                # 处理带有方块属性的情况
                if '[' in path and ']' in path:
                    path, properties_str = path.split('[')
                    properties_str = properties_str.rstrip(']')
                    properties_list = properties_str.split(', ')
                    properties = {prop.split('=')[0]: TAG_String(prop.split('=')[1]) for prop in reversed(properties_list)}
                    block = Block(namespace, path, properties)
                else:
                    block = Block(namespace, path)

                # 在世界中放置方块
                level.set_version_block(x,z,-y,"minecraft:overworld",("java", (1, 20, 4)),block)

        # 保存修改后的世界
        level.save()
        level.close()
        ShowMessageBox("文件导出成功！","白给的插件",link_text="点击这里前往导出文件夹", link_operator=OpenSaves_FileManagerOperator)
        return {'FINISHED'}
       
classes=[OpenFileManagerOperator,OpenSaves_FileManagerOperator,ExportSchem,Calculate_Size,ExportToSave]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)