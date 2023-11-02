import bpy  
import os

class MapOptimize(bpy.types.Operator):
    """优化面"""
    bl_idname = "baigave.map_optimize"
    bl_label = "优化面"
    def execute(self, context):
        scene = context.scene
        is_weld = scene.is_weld 
        objs = context.selected_objects
        nodetree_target = "UV"
        for obj in objs:
            obj.select_set(True)
            context.view_layer.objects.active = obj
            for md in context.active_object.modifiers:
                context.active_object.modifiers.remove(md)
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            #是否合并重叠的顶点
            if is_weld:
                bpy.ops.mesh.remove_doubles(threshold=0.001)
            #精简面
            bpy.ops.mesh.dissolve_limited(
                angle_limit=0.0872665, use_dissolve_boundaries=False, delimit={'MATERIAL'})
            bpy.ops.object.mode_set(mode='OBJECT')
            #添加几何节点修改器
            bpy.ops.object.modifier_add(type='NODES')
            mg = context.active_object.modifiers[0]
            context.active_object.modifiers.active = mg


            #导入几何节点
            try:
                mg.node_group = bpy.data.node_groups[nodetree_target]
            except:
                
                file_path = __file__.rsplit(
                    "\\", 1)[0]+"\\GeometryNodes.blend"
                inner_path = 'NodeTree'
                object_name = 'UV'
                bpy.ops.wm.append(
                    filepath=os.path.join(file_path, inner_path, object_name),
                    directory=os.path.join(file_path, inner_path),
                    filename=object_name
                )
                
                
            #设置几何节点        
            mg.node_group = bpy.data.node_groups[nodetree_target]

            #设置修改器，应用修改器
            obj.modifiers[0]["Output_2_attribute_name"] = obj.data.uv_layers.active.name
            bpy.ops.object.modifier_apply(modifier=mg.name)

            atts = obj.data.attributes
            max = len(atts)
            i = 0
            blender_version = bpy.app.version
            version_string = f"{blender_version[0]}.{blender_version[1]}{blender_version[2]:02}"
            version_float = float(version_string)



            while i < max:
                if atts[i].data_type == "FLOAT_VECTOR" and atts[i].domain == "CORNER":
                    atts.active_index = i
                    if version_float < 3.4:
                        bpy.ops.geometry.attribute_convert(mode='UV_MAP')
                    else:
                        bpy.ops.geometry.attribute_convert(
                            mode='GENERIC', domain='CORNER', data_type="FLOAT2")

                    max -= 1
                    continue
                if atts[i].data_type == "FLOAT_COLOR" and atts[i].domain == "CORNER":
                    atts.active_index = i
                    bpy.ops.geometry.attribute_convert(
                        mode='GENERIC', domain='CORNER', data_type="BYTE_COLOR")
                    max -= 1
                    continue
                i += 1
            obj.select_set(False)
        return {'FINISHED'}