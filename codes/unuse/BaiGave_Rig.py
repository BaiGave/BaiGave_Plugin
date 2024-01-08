import bpy
import os

from ..functions.tip import button_callback


#检查是不是已经生成人模
def check_armature(name):
    obj = bpy.context.scene.objects.get(name)
    if obj and obj.type == 'ARMATURE':
        return True
    else:
        return False

# 生成人模
class SPAWN_MODEL(bpy.types.Operator):
    """点击生成人模（限1个）"""
    bl_label ="生成人模"
    bl_idname ='spawn.model'
    
    def execute(self,context):
        # 拼接路径和文件名
        filepath = context.scene.rig_blend_path
        # 从文件中加载名为"BaiGave_Rig"的集合
        with bpy.data.libraries.load(filepath) as (data_from, data_to):
            data_to.collections = ["BaiGave_Rig"]
        # 将集合链接到当前场景
        for coll in data_to.collections:
             if coll is not None:
                  bpy.context.scene.collection.children.link(coll)
        # 定义一个要加载的网格名称列表
        mesh_names = ["S_Left Arm Layer_S","S_Left Arm_S","S_Right Arm Layer_S","S_Right Arm_S","S_3D_Left Arm Layer_S","S_3D_Right Arm Layer_S","3D_S_Body Layer", "3D_S_Hat Layer", "3D_S_Left Arm Layer", "3D_S_Left Arm Layer_S","3D_S_Left Leg Layer",
        "3D_S_Right Arm Layer","3D_S_Right Arm Layer_S","3D_S_Right Leg Layer","Body","Body Layer","Hat Layer","Head","Left Arm","Left Arm Layer","Left Arm Layer_S",
        "Left Arm_S","Left Leg","Left Leg Layer","Right Arm","Right Arm Layer","Right Arm Layer_S","Right Arm_S","Right Leg","Right Leg Layer"]
        # 从文件中加载网格并将它们追加到bpy.data.meshes中
        for mesh_name in mesh_names:
            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                # 使用列表推导式根据名称过滤网格
                data_to.meshes = [name for name in data_from.meshes if name == mesh_name]
            if data_to.meshes:
                # 使用一个变量来存储网格数据
                mesh_data = data_to.meshes[0]
                if mesh_name not in bpy.data.meshes:
                    bpy.data.meshes.append(mesh_data)
                else:
                    pass
        return{'FINISHED'}

#切换为Alex形态
def alex(self,context):
    if bpy.context.scene.BaiGave.alex == True:
        bpy.context.scene.BaiGave.steve = False
        if check_armature("骨架")==True:
                if bpy.context.scene.BaiGave.vanllia == True:
                    objects = ["Right Arm Layer", "Right Arm", "Left Arm", "Left Arm Layer"]
                    meshes = objects.copy()
                    for i in range(len(objects)):
                        obj = bpy.data.objects[objects[i]]
                        mesh_data = bpy.data.meshes[meshes[i]]
                        obj.data = mesh_data
                else:
                    objects = ["Right Arm Layer", "Right Arm", "Left Arm", "Left Arm Layer"]
                    meshes = ["S_" + obj for obj in objects]
                    for i in range(len(objects)):
                        obj = bpy.data.objects[objects[i]]
                        mesh_data = bpy.data.meshes[meshes[i]]
                        obj.data = mesh_data
        else:
            button_callback(self, context,"更改角色需先生成人模")
    elif bpy.context.scene.BaiGave.steve == False and bpy.context.scene.BaiGave.alex == False:
        bpy.context.scene.BaiGave.alex = True

#切换为Steve形态
def steve(self,context):
    if bpy.context.scene.BaiGave.steve == True:
        bpy.context.scene.BaiGave.alex = False
        if check_armature("骨架")==True:
                if bpy.context.scene.BaiGave.vanllia == True:
                    objects = ["Right Arm Layer", "Right Arm", "Left Arm", "Left Arm Layer"]
                    meshes = [obj + "_S" for obj in objects]
                    for obj_name, mesh_name in zip(objects, meshes):
                        obj = bpy.data.objects[obj_name]
                        mesh_data = bpy.data.meshes[mesh_name]
                        obj.data = mesh_data
                else:
                    objects = ["Right Arm Layer", "Right Arm", "Left Arm", "Left Arm Layer"]
                    meshes = ["S_" + obj + "_S" for obj in objects]
                    for obj_name, mesh_name in zip(objects, meshes):
                        obj = bpy.data.objects[obj_name]
                        mesh_data = bpy.data.meshes[mesh_name]
                        obj.data = mesh_data
        else:
            button_callback(self, context,"更改角色需先生成人模")
        
    elif bpy.context.scene.BaiGave.steve == False and bpy.context.scene.BaiGave.alex == False:
        bpy.context.scene.BaiGave.steve = True

#切换为原版权重形态
def vanllia(self,context):
    if bpy.context.scene.BaiGave.vanllia == True:
        bpy.context.scene.BaiGave.normal = False
        if check_armature("骨架")==True:
            if bpy.context.scene.BaiGave.alex == True:
                obj_mesh_dict = {
                    "Body": "Body",
                    "Body Layer": "Body Layer",
                    "Hat Layer": "Hat Layer",
                    "Head": "Head",
                    "Left Arm": "Left Arm",
                    "Left Arm Layer": "Left Arm Layer",
                    "Left Leg": "Left Leg",
                    "Left Leg Layer": "Left Leg Layer",
                    "Right Arm": "Right Arm",
                    "Right Arm Layer": "Right Arm Layer",
                    "Right Leg": "Right Leg",
                    "Right Leg Layer": "Right Leg Layer"
                }

                # 使用循环来遍历字典中的键值对，并且更新对象数据
                for obj_name, mesh_name in obj_mesh_dict.items():
                  bpy.data.objects[obj_name].data = bpy.data.meshes[mesh_name]
            else:
                # 使用字典来存储对象名和网格数据名的对应关系
                obj_mesh_dict = {
                    "Body": "Body",
                    "Body Layer": "Body Layer",
                    "Hat Layer": "Hat Layer",
                    "Head": "Head",
                    "Left Arm": "Left Arm_S",
                    "Left Arm Layer": "Left Arm Layer_S",
                    "Left Leg": "Left Leg",
                    "Left Leg Layer": "Left Leg Layer",
                    "Right Arm": "Right Arm_S",
                    "Right Arm Layer": "Right Arm Layer_S",
                    "Right Leg": "Right Leg",
                    "Right Leg Layer": "Right Leg Layer"
                }

                # 使用循环来遍历字典中的键值对，并且更新对象数据
                for obj_name, mesh_name in obj_mesh_dict.items():
                  bpy.data.objects[obj_name].data = bpy.data.meshes[mesh_name]
        else:
            button_callback(self, context,"更改角色需先生成人模")
    elif bpy.context.scene.BaiGave.normal == False and bpy.context.scene.BaiGave.vanllia == False:
        bpy.context.scene.BaiGave.vanllia = True

#切换为普通权重形态
def normal(self,context):
    if bpy.context.scene.BaiGave.normal == True:
        bpy.context.scene.BaiGave.vanllia = False
        if check_armature("骨架")==True:
            if bpy.context.scene.BaiGave.alex == True:
                # 使用字典来存储对象名和网格数据名的对应关系
                obj_mesh_dict = {
                    "Body": "S_Body",
                    "Body Layer": "S_Body Layer",
                    "Hat Layer": "S_Hat Layer",
                    "Head": "S_Head",
                    "Left Arm": "S_Left Arm",
                    "Left Arm Layer": "S_Left Arm Layer",
                    "Left Leg": "S_Left Leg",
                    "Left Leg Layer": "S_Left Leg Layer",
                    "Right Arm": "S_Right Arm",
                    "Right Arm Layer": "S_Right Arm Layer",
                    "Right Leg": "S_Right Leg",
                    "Right Leg Layer": "S_Right Leg Layer"
                }

                # 使用循环来遍历字典中的键值对，并且更新对象数据
                for obj_name, mesh_name in obj_mesh_dict.items():
                  bpy.data.objects[obj_name].data = bpy.data.meshes[mesh_name]
            else:
                # 使用字典来存储对象名和网格数据名的对应关系
                obj_mesh_dict = {
                    "Body": "S_Body",
                    "Body Layer": "S_Body Layer",
                    "Hat Layer": "S_Hat Layer",
                    "Head": "S_Head",
                    "Left Arm": "S_Left Arm_S",
                    "Left Arm Layer": "S_Left Arm Layer_S",
                    "Left Leg": "S_Left Leg",
                    "Left Leg Layer": "S_Left Leg Layer",
                    "Right Arm": "S_Right Arm_S",
                    "Right Arm Layer": "S_Right Arm Layer_S",
                    "Right Leg": "S_Right Leg",
                    "Right Leg Layer": "S_Right Leg Layer"
                }

                # 使用循环来遍历字典中的键值对，并且更新对象数据
                for obj_name, mesh_name in obj_mesh_dict.items():
                  bpy.data.objects[obj_name].data = bpy.data.meshes[mesh_name]
            
        else:
            button_callback(self, context,"更改角色需先生成人模")
    elif bpy.context.scene.BaiGave.normal == False and bpy.context.scene.BaiGave.vanllia == False:
        bpy.context.scene.BaiGave.normal = True

#切换为3d形态
def layer3d(self,context):
    if bpy.context.scene.BaiGave.Layer3d == True:
        bpy.context.scene.BaiGave.Layer2d = False
        if check_armature("骨架")==True:
            for obj in ["Body Layer", "Hat Layer", "Left Arm Layer", "Left Leg Layer", "Right Arm Layer", "Right Leg Layer"]:
                for mod in ["倒角", "实体化", "焊接", "遮罩", "顶点权重编辑", "拆边"]:
                    bpy.data.objects[obj].modifiers[mod].show_viewport = True      
            
        else:
            button_callback(self, context)
    elif bpy.context.scene.BaiGave.Layer3d == False and bpy.context.scene.BaiGave.Layer2d == False:
        bpy.context.scene.BaiGave.Layer3d = True
    
#切换为2d形态
def layer2d(self,context):
    if bpy.context.scene.BaiGave.Layer2d == True:
        bpy.context.scene.BaiGave.Layer3d = False
        if check_armature("骨架")==True:
            for obj in ["Body Layer", "Hat Layer", "Left Arm Layer", "Left Leg Layer", "Right Arm Layer", "Right Leg Layer"]:
                for mod in ["倒角", "实体化", "焊接", "遮罩", "顶点权重编辑", "拆边"]:
                    bpy.data.objects[obj].modifiers[mod].show_viewport = False      
        else:
            button_callback(self, context,"更改角色需先生成人模")
    elif bpy.context.scene.BaiGave.Layer3d == False and bpy.context.scene.BaiGave.Layer2d == False:
        bpy.context.scene.BaiGave.Layer2d = True


#属性
class Settings(bpy.types.PropertyGroup):
    steve : bpy.props.BoolProperty( name="史蒂夫", description="A simple bool property",
     default = False ,update = steve)
    alex : bpy.props.BoolProperty( name="艾利克斯", description="A simple bool property",
     default = True ,update = alex)
    vanllia : bpy.props.BoolProperty( name="原版", description="A simple bool property",
     default = True ,update = vanllia)
    normal : bpy.props.BoolProperty( name="普通", description="A simple bool property",
     default = False ,update = normal)
    Layer2d : bpy.props.BoolProperty( name="2d", description="A simple bool property",
     default = True ,update = layer2d)
    Layer3d : bpy.props.BoolProperty( name="3d", description="A simple bool property",
     default = False ,update = layer3d)
    
classes=[Settings,SPAWN_MODEL]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.BaiGave = bpy.props.PointerProperty(type = Settings)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    
        

