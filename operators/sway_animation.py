import bpy

def add_sway_animation(selected_objects, sway_strength=0.3):
    # 创建纹理
    texture = bpy.data.textures.new(name="sway", type='CLOUDS')
    
    # 创建空对象
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    
    # 添加驱动程序
    empty_object = bpy.context.object
    for i in range(3):
        myDriver = empty_object.driver_add('location', i)
        myDriver.driver.expression = 'frame / 250'
    
    # 遍历选定的对象
    for obj in selected_objects:
        if obj.type != 'EMPTY':
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            
            # 添加位移修饰符
            bpy.ops.object.modifier_add(type='DISPLACE')
            displace_modifier = obj.modifiers[-1]
            displace_modifier.strength = sway_strength
            displace_modifier.texture = texture
            displace_modifier.texture_coords = 'OBJECT'
            displace_modifier.texture_coords_object = bpy.data.objects["空物体"]
# 添加按钮来调用函数
class SwayAnimationOperator(bpy.types.Operator):
    bl_idname = "object.add_sway_animation"
    bl_label = "Add Sway Animation"

    def execute(self, context):
        # 调用你的函数并传递所需参数
        add_sway_animation(selected_objects=bpy.context.selected_objects)
        return {'FINISHED'}




        