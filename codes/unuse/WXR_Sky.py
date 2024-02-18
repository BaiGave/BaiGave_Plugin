import bpy  

class SkyImport(bpy.types.Operator):
    """导入WXR的天空"""
    bl_idname = "baigave.sky_import"
    bl_label = "导入WXR的天空"
    def execute(self, context):
        scene = context.scene
        path = bpy.context.scene.wxr_sky_blend_path
        # 加载 .blend 文件
        with bpy.data.libraries.load(path) as (data_from, data_to):
            # 导入所有的世界环境
            data_to.worlds = data_from.worlds
            data_to.collections = data_from.collections

        # 设置当前场景的世界环境为导入的 WXRs Sky
        for world in data_to.worlds:
            if "WXRs Sky" in world.name:
                scene.world = world
                break
        # 追加导入的 WXRs Sky 集合到当前场景
        for collection in data_to.collections:
            if "WXR's Sky" in collection.name:
                scene.collection.children.link(collection)
                break
        return {'FINISHED'}
    

classes=[SkyImport]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)