import bpy
texture = bpy.data.textures.new(name="sway", type='CLOUDS')
scene = bpy.context.scene
selected_objects = bpy.context.selected_objects
bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
myDriver = bpy.context.object.driver_add('location',0)
myDriver.driver.expression = 'frame/250'
myDriver = bpy.context.object.driver_add('location',1)
myDriver.driver.expression = 'frame/250'
myDriver = bpy.context.object.driver_add('location',2)
myDriver.driver.expression = 'frame/250'

for obj in selected_objects:
    if obj.type != 'EMPTY':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_add(type='DISPLACE')
        displace_modifier = obj.modifiers[-1]
        displace_modifier.strength = 0.3
        displace_modifier.texture = texture
        displace_modifier.texture_coords = 'OBJECT'
        displace_modifier.texture_coords_object = bpy.data.objects["空物体"]


        