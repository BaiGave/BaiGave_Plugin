import shutil
import threading
import bpy
import os
import re

from ..property import unzip_mods_files,unzip_resourcepacks_files

class Read_mods_dir(bpy.types.Operator):
    """读取目录"""
    bl_idname = "baigave.read_mods_dir"
    bl_label = "读取目录"
    
    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        existing_items = [item.name for item in my_properties.mod_list]
        path = scene.mods_dir  # 使用自定义路径

        try:
            directories = next(os.walk(path))[1]  # 获取路径下的所有文件夹名称
        except StopIteration:
            directories = []

        # 添加不存在于列表属性的文件夹名称，并删除不存在于文件夹中的item
        for directory in directories:
            dir_name = directory
            if dir_name not in existing_items:
                item = my_properties.mod_list.add()
                item.name = dir_name
            else:
                existing_items.remove(dir_name)

        # 删除不存在于文件夹中的item
        items_to_remove = []
        for index, item in enumerate(my_properties.mod_list):
            if item.name not in directories:
                items_to_remove.append(index)

        items_to_remove.reverse()  # 从后向前移除，以避免索引错位
        for index in items_to_remove:
            my_properties.mod_list.remove(index)
        # 读取并更新 config.py 文件中的 config 字典
        config_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "config.py")
        with open(config_path, 'r') as file:
            lines = file.readlines()

        config_index = -1
        mod_list_str = ', '.join([f'"{item.name}"' for item in my_properties.mod_list])
        mod_list_str = f'    "mod_list": [{mod_list_str}],\n'

        for i, line in enumerate(lines):
            if "config={" in line:
                config_index = i
                break

        if config_index != -1:
            found_mod_list = False
            for i in range(config_index, len(lines)):
                if "mod_list" in lines[i]:
                    lines[i] = mod_list_str
                    found_mod_list = True
                    break

            if not found_mod_list:
                lines.insert(config_index + 1, mod_list_str)

        with open(config_path, 'w') as file:
            file.writelines(lines)

        return {'FINISHED'}

class Read_resourcepacks_dir(bpy.types.Operator):
    """读取目录"""
    bl_idname = "baigave.read_resourcepacks_dir"
    bl_label = "读取目录"
    
    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        existing_items = [item.name for item in my_properties.resourcepack_list]
        path = scene.resourcepacks_dir  # 使用自定义路径

        try:
            directories = next(os.walk(path))[1]  # 获取路径下的所有文件夹名称
        except StopIteration:
            directories = []

        # 添加不存在于列表属性的文件夹名称，并删除不存在于文件夹中的item
        for directory in directories:
            dir_name = directory
            if dir_name not in existing_items:
                item = my_properties.resourcepack_list.add()
                item.name = dir_name
            else:
                existing_items.remove(dir_name)

        # 删除不存在于文件夹中的item
        items_to_remove = []
        for index, item in enumerate(my_properties.resourcepack_list):
            if item.name not in directories:
                items_to_remove.append(index)

        items_to_remove.reverse()  # 从后向前移除，以避免索引错位
        for index in items_to_remove:
            my_properties.resourcepack_list.remove(index)
        # 读取并更新 config.py 文件中的 config 字典
        config_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "config.py")
        with open(config_path, 'r') as file:
            lines = file.readlines()

        config_index = -1
        resourcepack_list_str = ', '.join([f'"{item.name}"' for item in my_properties.resourcepack_list])
        resourcepack_list_str = f'    "resourcepack_list": [{resourcepack_list_str}],\n'

        for i, line in enumerate(lines):
            if "config={" in line:
                config_index = i
                break

        if config_index != -1:
            found_resourcepack_list = False
            for i in range(config_index, len(lines)):
                if "resourcepack_list" in lines[i]:
                    lines[i] = resourcepack_list_str
                    found_resourcepack_list = True
                    break

            if not found_resourcepack_list:
                lines.insert(config_index + 1, resourcepack_list_str)

        with open(config_path, 'w') as file:
            file.writelines(lines)
        return {'FINISHED'}
    
class Read_versions_dir(bpy.types.Operator):
    """读取目录"""
    bl_idname = "baigave.read_versions_dir"
    bl_label = "读取目录"
    
    def execute(self, context):
        scene = context.scene
        version_items = []
        path = scene.versions_dir  # 使用自定义路径

        try:
            directories = next(os.walk(path))[1]  # 获取路径下的所有文件夹名称
        except StopIteration:
            directories = []

        # 添加不存在于列表属性的文件夹名称，并删除不存在于文件夹中的item
        for filename in directories:
            version_items.append((filename, filename, ''))

        bpy.types.Scene.version_list = bpy.props.EnumProperty(
            name="版本",
            description="选择一个版本",
            items=version_items,
        )
        
        # 获取当前选中的版本
        selected_version = bpy.context.scene.version_list

        # 读取config.py文件
        config_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "config.py") 
        with open(config_path, 'r') as file:
            content = file.read()

        # 使用正则表达式找到"version"参数并替换其值
        pattern = r'("version":\s*")([^"]*)(")'
        new_content = re.sub(pattern, fr'\g<1>{selected_version}\g<3>', content)

        # 将更改后的内容写回config.py文件
        with open(config_path, 'w') as file:
            file.write(new_content)

        return {'FINISHED'}
    
class Read_saves_dir(bpy.types.Operator):
    """读取目录"""
    bl_idname = "baigave.read_saves_dir"
    bl_label = "读取目录"
    
    def execute(self, context):
        scene = context.scene
        save_items = []
        path = scene.saves_dir  # 使用自定义路径

        try:
            directories = next(os.walk(path))[1]  # 获取路径下的所有文件夹名称
            directories = [d for d in directories if os.path.exists(os.path.join(path, d, 'level.dat'))]
        except StopIteration:
            directories = []

        # 添加不存在于列表属性的文件夹名称，并删除不存在于文件夹中的item
        for filename in directories:
            save_items.append((filename, filename, ''))

        bpy.types.Scene.save_list = bpy.props.EnumProperty(
            name="存档",
            description="选择一个存档",
            items=save_items,
        )

        selected_save = getattr(bpy.context.scene, 'save_list', None)


        # 读取config.py文件
        config_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "config.py") 
        with open(config_path, 'r') as file:
            content = file.read()

        # 使用正则表达式找到"save"参数并替换其值
        pattern = r'("save":\s*")([^"]*)(")'
        new_content = re.sub(pattern, fr'\g<1>{selected_save}\g<3>', content)

        # 将更改后的内容写回config.py文件
        with open(config_path, 'w') as file:
            file.write(new_content)

        return {'FINISHED'}

class Read_colors_dir(bpy.types.Operator):
    """读取目录"""
    bl_idname = "baigave.read_colors_dir"
    bl_label = "读取目录"
    
    def execute(self, context):
        scene = context.scene
        color_items = []
        path = scene.colors_dir  # 使用自定义路径

        try:
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.py')]
        except FileNotFoundError:
            files = []

        # 添加不存在于列表属性的文件夹名称，并删除不存在于文件夹中的item
        for filename in files:
            color_items.append((filename, filename, ''))

        bpy.types.Scene.color_list = bpy.props.EnumProperty(
            name="颜色",
            description="选择一个颜色字典",
            items=color_items,
        )
        
        # 获取当前选中的版本
        selected_version = bpy.context.scene.color_list

        # 读取config.py文件
        config_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "config.py") 
        with open(config_path, 'r') as file:
            content = file.read()

        # 使用正则表达式找到"color"参数并替换其值
        pattern = r'("color":\s*")([^"]*)(")'
        new_content = re.sub(pattern, fr'\g<1>{selected_version}\g<3>', content)

        # 将更改后的内容写回config.py文件
        with open(config_path, 'w') as file:
            file.write(new_content)

        return {'FINISHED'}
    
class Read_schems_dir(bpy.types.Operator):
    """读取schem目录"""
    bl_idname = "baigave.read_schems_dir"
    bl_label = "读取schem目录"
    
    def execute(self, context):
        scene = context.scene
        schem_items = []
        path = scene.schems_dir  # 使用自定义路径

        try:
            # 获取路径下的所有文件
            directories = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.schem')]
        except StopIteration:
            directories = []

        # 添加不存在于列表属性的文件夹名称，并删除不存在于文件夹中的item
        for filename in directories:
            schem_items.append((filename, filename, ''))

        bpy.types.Scene.schem_list = bpy.props.EnumProperty(
            name=".schem文件",
            description="选择一个.schem文件",
            items=schem_items,
        )
        
        selected_schem = getattr(bpy.context.scene, 'schem_list', None)



        # 读取config.py文件
        config_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "config.py") 
        with open(config_path, 'r') as file:
            content = file.read()

        # 使用正则表达式找到"schem"参数并替换其值
        pattern = r'("schem":\s*")([^"]*)(")'
        new_content = re.sub(pattern, fr'\g<1>{selected_schem}\g<3>', content)

        # 将更改后的内容写回config.py文件
        with open(config_path, 'w') as file:
            file.write(new_content)

        return {'FINISHED'}
    
    
# 添加一个操作类来处理上下移动和删除模组
class MoveModItem(bpy.types.Operator):
    bl_idname = "baigave.move_mod_item"
    bl_label = "移动"
    direction: bpy.props.StringProperty()  # type: ignore

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

# 添加一个操作类来处理上下移动和删除资源包
class MoveResourcepackItem(bpy.types.Operator):
    bl_idname = "baigave.move_resourcepack_item"
    bl_label = "移动"
    direction: bpy.props.StringProperty()   # type: ignore

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        resourcepack_list = my_properties.resourcepack_list
        index = my_properties.resourcepack_list_index

        if self.direction == 'UP' and index > 0:
            resourcepack_list.move(index, index - 1)
            my_properties.resourcepack_list_index -= 1
        elif self.direction == 'DOWN' and index < len(resourcepack_list) - 1:
            resourcepack_list.move(index, index + 1)
            my_properties.resourcepack_list_index += 1

        return {'FINISHED'}

class AddModOperator(bpy.types.Operator):
    bl_idname = "baigave.add_mod_operator"
    bl_label = "添加模组"

    # 定义一个属性来存储文件路径
    filepath: bpy.props.StringProperty(subtype="FILE_PATH") # type: ignore
    # 定义一个属性来过滤文件类型，只显示.jar文件
    filter_glob: bpy.props.StringProperty(default="*.jar", options={'HIDDEN'}) # type: ignore

    def execute(self, context):
        source_file = self.filepath
        destination_folder = bpy.context.scene.jars_dir  # 获取指定文件夹路径

        if source_file and destination_folder:
            try:
                shutil.copy(source_file, destination_folder)
                threading.Thread(target=unzip_mods_files).start()
                return {'FINISHED'}
            except Exception as e:
                self.report({'ERROR'}, f"Failed to copy file: {e}")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "File or destination folder not specified")
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class DeleteModOperator(bpy.types.Operator):
    bl_idname = "baigave.delete_mod_operator"
    bl_label = "删除模组"

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        mod_list = my_properties.mod_list
        index = my_properties.mod_list_index

        if 0 <= index < len(mod_list):
            jars_folder = bpy.context.scene.jars_dir  
            mods_folder = bpy.context.scene.mods_dir 
            # 获取名称
            selected_object_name = mod_list[index].name
            if selected_object_name != "资源包" and selected_object_name != "minecraft":
                # 构建要删除的文件夹路径
                folder_path = os.path.join(mods_folder, selected_object_name)
                # 检查文件夹是否存在并删除
                if os.path.exists(folder_path):
                    for root, dirs, files in os.walk(folder_path, topdown=False):
                        for file in files:
                            os.remove(os.path.join(root, file))
                        for dir in dirs:
                            os.rmdir(os.path.join(root, dir))
                    os.rmdir(folder_path)
                    print(f"已删除文件夹 '{selected_object_name}' 及其内容。")
                else:
                    print(f"文件夹 '{selected_object_name}' 不存在。无法删除。")

                # 构建要删除的文件路径
                file_path = os.path.join(jars_folder, selected_object_name+".jar")
                
                # 删除文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"文件 {file_path} 已删除")
                else:
                    print(f"文件 {file_path} 不存在")
            else:
                print("喂这个不能删啊！")
            
        return {'CANCELLED'}

class AddResourcepackOperator(bpy.types.Operator):
    bl_idname = "baigave.add_resourcepack_operator"
    bl_label = "添加模组"

    # 定义一个属性来存储文件路径
    filepath: bpy.props.StringProperty(subtype="FILE_PATH") # type: ignore # type: ignore
    # 定义一个属性来过滤文件类型，只显示.zip文件
    filter_glob: bpy.props.StringProperty(default="*.zip", options={'HIDDEN'}) # type: ignore

    def execute(self, context):
        source_file = self.filepath
        destination_folder = bpy.context.scene.zips_dir  # 获取指定文件夹路径

        if source_file and destination_folder:
            try:
                shutil.copy(source_file, destination_folder)
                threading.Thread(target=unzip_resourcepacks_files).start()
                return {'FINISHED'}
            except Exception as e:
                self.report({'ERROR'}, f"Failed to copy file: {e}")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "File or destination folder not specified")
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class DeleteResourcepackOperator(bpy.types.Operator):
    bl_idname = "baigave.delete_resourcepack_operator"
    bl_label = "删除模组"

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        resourcepack_list = my_properties.resourcepack_list
        index = my_properties.resourcepack_list_index

        if 0 <= index < len(resourcepack_list):
            zips_folder = bpy.context.scene.zips_dir  
            resourcepacks_folder = bpy.context.scene.resourcepacks_dir 
            # 获取名称
            selected_object_name = resourcepack_list[index].name
            # 构建要删除的文件夹路径
            folder_path = os.path.join(resourcepacks_folder, selected_object_name)
            # 检查文件夹是否存在并删除
            if os.path.exists(folder_path):
                for root, dirs, files in os.walk(folder_path, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(folder_path)
                print(f"已删除文件夹 '{selected_object_name}' 及其内容。")
            else:
                print(f"文件夹 '{selected_object_name}' 不存在。无法删除。")

            # 构建要删除的文件路径
            file_path = os.path.join(zips_folder, selected_object_name+".zip")
            
            # 删除文件
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"文件 {file_path} 已删除")
            else:
                print(f"文件 {file_path} 不存在")
            
        return {'CANCELLED'}

class AddColorToBlockOperator(bpy.types.Operator):
    bl_idname = "baigave.add_color_to_block_operator"
    bl_label = "添加方块"

    # 定义一个属性来存储文件路径
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")# type: ignore
    # 定义一个属性来过滤文件类型，只显示.json文件
    filter_glob: bpy.props.StringProperty(default="*.json", options={'HIDDEN'})# type: ignore

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup) # type: ignore

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        color_to_block_list = my_properties.color_to_block_list

        source_file = os.path.dirname(self.filepath) 
        
        for f in self.files:

            # 从文件路径中提取文件名
            filename = f.name.replace(".json","")

            # 检查文件名是否已经在列表中
            if not any(item.name == filename for item in color_to_block_list):
                # 文件名不在列表中，添加到列表
                item = color_to_block_list.add()
                item.name = filename
                item.filepath=source_file+"\\"+f.name

        return {'FINISHED'}

        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class DeleteColorToBlockOperator(bpy.types.Operator):
    bl_idname = "baigave.delete_color_to_block_operator"
    bl_label = "删除方块"

    def execute(self, context):
        scene = context.scene
        my_properties = scene.my_properties
        color_to_block_list = my_properties.color_to_block_list
        index = my_properties.color_to_block_list_index

        # 删除选定的颜色到方块映射
        if index < len(color_to_block_list):
            color_to_block_list.remove(index)

        return {'FINISHED'}



classes=[Read_resourcepacks_dir,Read_mods_dir, Read_versions_dir,Read_saves_dir,Read_colors_dir,Read_schems_dir,MoveModItem,MoveResourcepackItem,
         AddModOperator,DeleteModOperator,AddResourcepackOperator,DeleteResourcepackOperator,AddColorToBlockOperator,DeleteColorToBlockOperator]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)