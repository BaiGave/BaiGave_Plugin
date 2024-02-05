import bpy
import os
import zipfile
import threading
import functools
import numpy as np
import shutil
import toml
import json
import random
import importlib
from .functions.get_data import get_file_path,get_all_data
from .. import config
from collections import Counter
from PIL import Image
class ModInfo(bpy.types.PropertyGroup):
    icon: bpy.props.StringProperty(name="图标")
    name: bpy.props.StringProperty(name="名称")
    description: bpy.props.StringProperty(name="描述")

#属性
class Property(bpy.types.PropertyGroup):
    bpy.types.Scene.mods_dir = bpy.props.StringProperty(
        name="模组路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp")
    )
    bpy.types.Scene.jars_dir = bpy.props.StringProperty(
        name="jar文件路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "mods")
    )
    bpy.types.Scene.versions_dir = bpy.props.StringProperty(
        name="版本路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp","minecraft")
    )
    bpy.types.Scene.saves_dir = bpy.props.StringProperty(
        name="存档路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "saves")
    )
    bpy.types.Scene.colors_dir = bpy.props.StringProperty(
        name="颜色路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "colors")
    )
    bpy.types.Scene.schems_dir = bpy.props.StringProperty(
        name=".schem文件路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "schem")
    )
    bpy.types.Scene.zips_dir = bpy.props.StringProperty(
        name="zip文件路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "resourcepacks")
    )
    bpy.types.Scene.resourcepacks_dir = bpy.props.StringProperty(
        name="资源包路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp", "资源包")
    )
    bpy.types.Scene.rig_blend_path = bpy.props.StringProperty(
        name="人物绑定路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "codes","blend_files","BaiGave_Rig.blend")
    )
    bpy.types.Scene.material_blend_path = bpy.props.StringProperty(
        name="材质节点路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "codes","blend_files","Material.blend")
    )
    bpy.types.Scene.geometrynodes_blend_path = bpy.props.StringProperty(
        name="几何节点路径",
        default=os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "codes","blend_files","GeometryNodes.blend")
    )
    bpy.types.Scene.is_weld = bpy.props.BoolProperty(name="合并重叠顶点", default=True)

    JsonImportSpeed: bpy.props.FloatProperty(name="导入速度(秒每个）",description="Import speed",min=0.01, max=2.0,default=1.0)
    resourcepack_list: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    resourcepack_list_index: bpy.props.IntProperty()

    # 定义 mod_list 属性并附加到 my_properties
    mod_list: bpy.props.CollectionProperty(type=ModInfo)
    mod_list_index: bpy.props.IntProperty()
    bpy.types.Scene.min_coordinates = bpy.props.IntVectorProperty(name="最小坐标", size=3)
    bpy.types.Scene.max_coordinates = bpy.props.IntVectorProperty(name="最大坐标", size=3)

    bpy.types.Scene.schem_size = bpy.props.IntVectorProperty(name="结构大小", size=3)
    bpy.types.Scene.schem_location = bpy.props.IntVectorProperty(name="结构位置", size=3)


    # 定义一个 EnumProperty 作为下拉列表的选项
    bpy.types.Scene.version_list = bpy.props.EnumProperty(
        name="版本",
        description="选择一个版本",
        items=(),
    )
    bpy.types.Scene.save_list = bpy.props.EnumProperty(
        name="存档",
        description="选择一个存档",
        items=(),
    )
    bpy.types.Scene.schem_list = bpy.props.EnumProperty(
        name=".schem文件",
        description="选择一个.schem文件",
        items=(),
    )
    bpy.types.Scene.color_list = bpy.props.EnumProperty(
        name="color文件",
        description="选择一个颜色字典",
        items=(),
    )


    bpy.types.Scene.schem_filename = bpy.props.StringProperty(name=".schem文件名", default="file")

    bpy.types.Scene.world_name = bpy.props.StringProperty(name="World Name", default="World1")
    bpy.types.Scene.spawn_x = bpy.props.IntProperty(name="Spawn X", default=0)
    bpy.types.Scene.spawn_y = bpy.props.IntProperty(name="Spawn Y", default=64)
    bpy.types.Scene.spawn_z = bpy.props.IntProperty(name="Spawn Z", default=0)
    bpy.types.Scene.hardcore = bpy.props.EnumProperty(
        name="极限模式",
        items=[("0", "否", "否"), ("1", "是", "是")],
        default="0"
    )
    bpy.types.Scene.difficulty = bpy.props.EnumProperty(
        name="难度",
        items=[("0", "和平", "和平模式"), ("1", "简单", "简单模式"), ("2", "普通", "普通模式"), ("3", "困难", "困难模式")],
        default="0"
    )
    bpy.types.Scene.gametype = bpy.props.EnumProperty(
        name="游戏模式",
        items=[("0", "生存", "和平模式"), ("1", "创造", "创造模式"), ("2", "冒险", "冒险模式"), ("3", "旁观", "旁观模式")],
        default="1"
    )
    bpy.types.Scene.overworld_generator_type = bpy.props.EnumProperty(
        name="主世界生成类型",
        items=[("noise", "噪波", "一般世界"), ("flat", "平坦", "平坦世界"), ("debug", "DEBUG", "DEBUG")],
        default="noise"
    )
    bpy.types.Scene.allow_commands = bpy.props.EnumProperty(
        name="允许指令",
        items=[("0", "否", "否"), ("1", "是", "是")],
        default="1"
    )
    bpy.types.Scene.breaking_the_height_limit = bpy.props.EnumProperty(
        name="突破限高",
        items=[("0", "否", "否"), ("1", "是", "突破限高至2032！")],
        default="0"
    )

    # 布尔值
    bpy.types.Scene.announce_advancements = bpy.props.EnumProperty(
        name="Announce Advancements",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.block_explosion_drop_decay = bpy.props.EnumProperty(
        name="Block Explosion Drop Decay",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.command_block_output = bpy.props.EnumProperty(
        name="Command Block Output",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.disable_elytra_movement_check = bpy.props.EnumProperty(
        name="Disable Elytra Movement Check",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.disable_raids = bpy.props.EnumProperty(
        name="Disable Raids",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_daylight_cycle = bpy.props.EnumProperty(
        name="Do Daylight Cycle",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_entity_drops = bpy.props.EnumProperty(
        name="Do Entity Drops",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_fire_tick = bpy.props.EnumProperty(
        name="Do Fire Tick",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_immediate_respawn = bpy.props.EnumProperty(
        name="Do Immediate Respawn",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_insomnia = bpy.props.EnumProperty(
        name="Do Insomnia",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_limited_crafting = bpy.props.EnumProperty(
        name="Do Limited Crafting",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_mob_loot = bpy.props.EnumProperty(
        name="Do Mob Loot",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_mob_spawning = bpy.props.EnumProperty(
        name="Do Mob Spawning",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_patrol_spawning = bpy.props.EnumProperty(
        name="Do Patrol Spawning",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_tile_drops = bpy.props.EnumProperty(
        name="Do Tile Drops",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_trader_spawning = bpy.props.EnumProperty(
        name="Do Trader Spawning",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_vines_spread = bpy.props.EnumProperty(
        name="Do Vines Spread",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_warden_spawning = bpy.props.EnumProperty(
        name="Do Warden Spawning",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.do_weather_cycle = bpy.props.EnumProperty(
        name="Do Weather Cycle",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.drowning_damage = bpy.props.EnumProperty(
        name="Drowning Damage",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.fall_damage = bpy.props.EnumProperty(
        name="Fall Damage",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.fire_damage = bpy.props.EnumProperty(
        name="Fire Damage",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.forgive_dead_players = bpy.props.EnumProperty(
        name="Forgive Dead Players",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.freeze_damage = bpy.props.EnumProperty(
        name="Freeze Damage",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.global_sound_events = bpy.props.EnumProperty(
        name="Global Sound Events",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.keep_inventory = bpy.props.EnumProperty(
        name="Keep Inventory",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.lava_source_conversion = bpy.props.EnumProperty(
        name="Lava Source Conversion",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.log_admin_commands = bpy.props.EnumProperty(
        name="Log Admin Commands",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.mob_explosion_drop_decay = bpy.props.EnumProperty(
        name="Mob Explosion Drop Decay",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.mob_griefing = bpy.props.EnumProperty(
        name="Mob Griefing",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.natural_regeneration = bpy.props.EnumProperty(
        name="Natural Regeneration",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.reduced_debug_info = bpy.props.EnumProperty(
        name="Reduced Debug Info",
        items=[("False", "否", "否"), ("True", "是", "是")],
        default="False"
    )

    bpy.types.Scene.send_command_feedback = bpy.props.EnumProperty(
        name="Send Command Feedback",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.show_death_messages = bpy.props.EnumProperty(
        name="Show Death Messages",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.spectators_generate_chunks = bpy.props.EnumProperty(
        name="Spectators Generate Chunks",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.tnt_explosion_drop_decay = bpy.props.EnumProperty(
        name="TNT Explosion Drop Decay",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.universal_anger = bpy.props.EnumProperty(
        name="Universal Anger",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    bpy.types.Scene.water_source_conversion = bpy.props.EnumProperty(
        name="Water Source Conversion",
        items=[("True", "是", "是"), ("False", "否", "否")],
        default="True"
    )

    # 整数
    bpy.types.Scene.max_entity_cramming = bpy.props.IntProperty(name="Max Entity Cramming",default=12)
    bpy.types.Scene.snow_accumulation_height = bpy.props.IntProperty(name="Snow Accumulation Height",default=1)
    bpy.types.Scene.spawn_radius = bpy.props.IntProperty(name="Spawn Radius",default=10)
    bpy.types.Scene.players_sleeping_percentage = bpy.props.IntProperty(name="Players Sleeping Percentage",default=0)
    bpy.types.Scene.random_tick_speed = bpy.props.IntProperty(name="Random Tick Speed",default=0)
    bpy.types.Scene.command_modification_block_limit = bpy.props.IntProperty(name="Command Modification Block Limit",default=32768)
    bpy.types.Scene.max_command_chain_length = bpy.props.IntProperty(name="Max Command Chain Length",default=65536)
    bpy.types.Scene.day_time = bpy.props.IntProperty(name="Day Time", default=16000)
    bpy.types.Scene.seed = bpy.props.IntProperty(name="Seed", default=random.randint(0, 10000))

    bpy.types.Scene.flySpeed = bpy.props.FloatProperty(name="FlySpeed", default=0.05)
    bpy.types.Scene.flying = bpy.props.BoolProperty(name="Flying", default=False)
    bpy.types.Scene.instabuild = bpy.props.BoolProperty(name="instabuild", default=True)
    bpy.types.Scene.invulnerable = bpy.props.BoolProperty(name="invulnerable", default=True)
    bpy.types.Scene.mayBuild = bpy.props.BoolProperty(name="mayBuild", default=True)
    bpy.types.Scene.mayfly = bpy.props.BoolProperty(name="mayfly", default=True)

    bpy.types.Scene.walkSpeed = bpy.props.FloatProperty(name="walkSpeed", default=0.1)

    bpy.types.Scene.luck = bpy.props.FloatProperty(name="幸运值", default=0, min=-1024, max=1024)
    bpy.types.Scene.max_health = bpy.props.FloatProperty(name="最大生命值", default=20, min=1, max=1024)
    bpy.types.Scene.knockback_resistance = bpy.props.FloatProperty(name="击退抗性", default=0, min=0, max=1)
    bpy.types.Scene.movement_speed = bpy.props.FloatProperty(name="移动加速度", default=0, min=0, max=1024)
    bpy.types.Scene.armor = bpy.props.FloatProperty(name="盔甲值", default=0, min=0, max=30)
    bpy.types.Scene.armor_toughness = bpy.props.FloatProperty(name="盔甲韧性", default=0, min=0, max=20)
    bpy.types.Scene.attack_damage = bpy.props.FloatProperty(name="攻击伤害", default=0, min=0, max=2048)
    bpy.types.Scene.attack_speed = bpy.props.FloatProperty(name="攻击速度", default=0, min=0, max=1024)
    
def unzip_mods_files():
    # 指定的文件夹路径
    folder_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "mods")

    # 临时文件夹路径
    temp_dir = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp")

    # 遍历文件夹中的所有文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.jar'):
            # 构造完整的文件路径
            file_path = os.path.join(folder_path, file_name)

            # 解压文件
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                mod_id = None 
                for member in zip_ref.namelist():
                    if member == 'version.json':
                        with zip_ref.open(member) as mod_json_file:
                            mod_json_content = mod_json_file.read()
                            mod_data = json.loads(mod_json_content,strict=False)
                            # 读取 "id" 字段的值
                            mod_id = "minecraft"
                            version = mod_data.get("id","")
                            icon = None
                            name = mod_data.get("name","")
                            description = "我的世界原版"
                        new_folder_path = os.path.join(temp_dir,mod_id,version)
                        break  # 找到后终止循环
                    # 判断是否存在fabric.mod.json，若存在则读取其中的modid
                    elif member == 'fabric.mod.json':
                        with zip_ref.open(member) as mod_json_file:
                            mod_json_content = mod_json_file.read()
                            mod_data = json.loads(mod_json_content,strict=False)
                            # 读取 "id" 字段的值
                            mod_id = mod_data.get("id","")
                            icon = mod_data.get("icon","").replace("/", "\\")
                            name = mod_data.get("name","")
                            description = mod_data.get("description","")
                        try:
                            # 创建新文件夹以modid命名
                            new_folder_path = os.path.join(temp_dir, mod_id)
                        except:
                            pass
                        break  # 找到fabric.mod.json后终止循环
                    elif member == 'META-INF/mods.toml':
                        with zip_ref.open('META-INF/mods.toml') as mods_toml_file:
                            mods_toml_content = mods_toml_file.read()
                            mods_toml_data = toml.loads(mods_toml_content.decode('utf-8'))
                            if "mods" in mods_toml_data:
                                for mod_entry in mods_toml_data["mods"]:
                                    mod_id = mod_entry["modId"]
                                    icon = mod_entry.get("logoFile", "").replace("/", "\\")  # 添加默认值，防止没有 "logoFile" 字段时报错
                                    name = mod_entry.get("displayName", "")  # 添加默认值，防止没有 "displayName" 字段时报错
                                    description = mod_entry.get("description", "")  # 添加默认值，防止没有 "description" 字段时报错
                            else:
                                print(f"在 {file_name} 中找不到 'mods' 条目")
                        try:
                            # 创建新文件夹以modid命名
                            new_folder_path = os.path.join(temp_dir, mod_id)
                        except:
                            pass
                        break
                    elif member == 'mcmod.info':
                        with zip_ref.open('mcmod.info') as mcmod_file:
                            mcmod_content = mcmod_file.read()
                            mcmod_data = json.loads(mcmod_content)
                            if mcmod_data:
                                mod_info = mcmod_data[0]  
                                mod_id = mod_info.get("modid", "")
                                icon = mod_info.get("logoFile", "").replace("/", "\\") 
                                name = mod_info.get("name", "")  
                                description = mod_info.get("description", "")  
                        try:
                            # 创建新文件夹以modid命名
                            new_folder_path = os.path.join(temp_dir, mod_id)
                        except:
                            pass
                        break

                    
                if mod_id:
                    try:
                        if not os.path.exists(new_folder_path):
                            os.makedirs(new_folder_path)
                        elif os.path.exists(new_folder_path):
                            continue
                    except:
                        pass

                    # 将文件解压到新文件夹中
                    for member in zip_ref.namelist():
                        try:
                            # 提取第一层目录下的 assets 和 data 文件夹以及第一层文件夹下的 .json 和 .png 文件
                            if member.startswith('assets/') or member.startswith('data/'):
                                # 构造解压路径
                                extract_path = os.path.join(new_folder_path, member)
                                dir_extract_path = os.path.dirname(extract_path)+"/"
                                # 如果目标文件夹不存在，则创建
                                try:
                                    if not os.path.exists(dir_extract_path):
                                        os.makedirs(dir_extract_path)
                                except:
                                    pass
                                if not os.path.exists(extract_path):
                                    with zip_ref.open(member) as file_in_zip, open(extract_path, 'wb') as output_file:
                                        shutil.copyfileobj(file_in_zip, output_file)

                            elif not '/' in member:  # 第一级目录下的文件
                                if member.endswith('.json') or member.endswith('.png'):
                                    extract_path = os.path.join(new_folder_path, member)
                                    with zip_ref.open(member) as file_in_zip, open(extract_path, 'wb') as output_file:
                                        shutil.copyfileobj(file_in_zip, output_file)
                        except Exception as e:
                            print(f"An error occurred: {e}")
                            pass
                    try:
                        if mod_id!="minecraft":
                            new_name = os.path.join(folder_path, mod_id+".jar")
                            zip_ref.close()
                            os.rename(file_path, new_name)
                        elif mod_id == "minecraft":
                            new_name = os.path.join(folder_path, version+".jar")
                            zip_ref.close()
                            os.rename(file_path, new_name)
                    except Exception as e:
                        print(f"An error occurred while renaming: {e}")
        

def unzip_resourcepacks_files():
    # 指定的文件夹路径
    folder_path = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "resourcepacks")

    # 临时文件夹路径
    temp_dir = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp","资源包")

    # 遍历文件夹中的所有文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.zip'):
            # 构造完整的文件路径
            file_path = os.path.join(folder_path, file_name)

            # 解压文件
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                new_folder_path=os.path.join(temp_dir,file_name.replace('.zip', ''))
                try:
                    if not os.path.exists(new_folder_path):
                        os.makedirs(new_folder_path)
                    elif os.path.exists(new_folder_path):
                        continue
                except:
                    pass

                # 将文件解压到新文件夹中
                for member in zip_ref.namelist():
                    try:
                        # 提取第一层目录下的 assets 和 data 文件夹以及第一层文件夹下的 .json 和 .png 文件
                        if member.startswith('assets/') or member.startswith('data/'):
                            # 构造解压路径
                            extract_path = os.path.join(new_folder_path, member)
                            dir_extract_path = os.path.dirname(extract_path)+"/"
                            # 如果目标文件夹不存在，则创建
                            try:
                                if not os.path.exists(dir_extract_path):
                                    os.makedirs(dir_extract_path)
                            except:
                                pass
                            if not os.path.exists(extract_path):
                                with zip_ref.open(member) as file_in_zip, open(extract_path, 'wb') as output_file:
                                    shutil.copyfileobj(file_in_zip, output_file)

                        elif not '/' in member:  # 第一级目录下的文件
                            if member.endswith('.json') or member.endswith('.png'):
                                extract_path = os.path.join(new_folder_path, member)
                                with zip_ref.open(member) as file_in_zip, open(extract_path, 'wb') as output_file:
                                    shutil.copyfileobj(file_in_zip, output_file)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        pass
                

class UnzipModOperator(bpy.types.Operator):
    bl_idname = "baigave.unzip_mods_operator"
    bl_label = "加载模组包"

    def execute(self, context):
        thread = threading.Thread(target=unzip_mods_files)
        thread.start()

        bpy.app.timers.register(functools.partial(self.check_thread, thread), first_interval=1.0)
        return {'RUNNING_MODAL'}

    def check_thread(self, thread):
        # 检查线程是否在运行
        if not thread.is_alive():
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

class UnzipResourcepacksOperator(bpy.types.Operator):
    bl_idname = "baigave.unzip_resourcepacks_operator"
    bl_label = "加载模组包"

    def execute(self, context):
        thread = threading.Thread(target=unzip_resourcepacks_files)
        thread.start()

        bpy.app.timers.register(functools.partial(self.check_thread, thread), first_interval=1.0)
        return {'RUNNING_MODAL'}

    def check_thread(self, thread):
        # 检查线程是否在运行
        if not thread.is_alive():
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

def write_model_dict(file, model_dict):
    for key, value in model_dict.items():
        file.write(f"    {key}: \"{value}\",\n")
def calculate_average_color(image_path):
    # 打开图片
    img = Image.open(image_path)

    # 调整图片大小以便处理
    img = img.resize((1, 1))

    # 获取像素值
    pixel = img.getpixel((0, 0))

    # 转换为0-1之间的浮点数
    normalized_color = (round(pixel[0] / 255, 2), round(pixel[1] / 255, 2), round(pixel[2] / 255, 2) ,round(pixel[3] / 255, 2) if len(pixel) == 4 else 1.0)

    return normalized_color

def get_color(variant_value,processed_models,dic,id):
    if 'model' in variant_value:
        model = variant_value['model']
        filepath = get_file_path(model, 'm')
        if filepath is None:
            return
        dirname, filename = os.path.split(filepath)
        dirname = dirname + '\\'
        try:
            _, _, parent = get_all_data(dirname, filename)
            t, _, _ = get_all_data(dirname, filename)
            texture_counter = Counter(t.values())
            most_common_texture = texture_counter.most_common(1)[0][0]

            all_average_colors = []
            processed_textures = set()

            for value in t.values():
                if value != most_common_texture:
                    continue

                if value in processed_textures:
                    continue
                processed_textures.add(value)

                texture = get_file_path(value, 't')
                average_color = calculate_average_color(texture)
                all_average_colors.append(average_color)

            if all_average_colors:
                overall_average_color = np.mean(all_average_colors, axis=0)
                overall_average_color = np.round(overall_average_color, 2)
                dic[tuple(overall_average_color)] = id
                return
        except Exception as e:
            pass
def read_blockstate_files(directory,version):
    cube_dict = {}
    slab_dict = {}
    slab_top_dict = {}
    stairs_west_top_outer_left = {}
    stairs_east_top_outer_left = {}
    stairs_south_top_outer_left = {}
    stairs_north_top_outer_left = {}
    stairs_west_bottom_outer_left = {}
    stairs_east_bottom_outer_left = {}
    stairs_south_bottom_outer_left = {}
    stairs_north_bottom_outer_left = {}
    stairs_west_top_straight = {}
    stairs_east_top_straight = {}
    stairs_west_bottom_straight = {}
    stairs_east_bottom_straight = {}
    stairs_north_top_straight = {}
    stairs_south_top_straight = {}
    stairs_north_bottom_straight = {}
    stairs_south_bottom_straight = {}
    stairs_south_top_inner_left = {}
    stairs_north_top_inner_right = {}
    stairs_west_top_inner_left = {}
    stairs_west_top_inner_right = {}
    stairs_south_bottom_inner_left = {}
    stairs_north_bottom_inner_right = {}
    stairs_west_bottom_inner_left = {}
    stairs_west_bottom_inner_right = {}

    processed_models = set()  
    
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            if dir == "minecraft":
                blockstate_dir = os.path.join(root, dir, version, "assets", dir, "blockstates")
            else:
                blockstate_dir = os.path.join(root, dir, "assets", dir, "blockstates")
            if os.path.exists(blockstate_dir):
                for file in os.listdir(blockstate_dir):
                    if file.endswith(".json"):
                        file_path = os.path.join(blockstate_dir, file)
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            if 'variants' in data:
                                variants = data['variants']
                                for variant_key, variant_value in variants.items():
                                    if variant_key != "":
                                        id = str(dir + ":" + file.replace(".json", "") + "[" + variant_key + "]")
                                        if variant_key =="type=bottom":
                                            get_color(variant_value,processed_models,slab_dict,id)
                                            continue
                                        elif variant_key =="type=top":
                                            get_color(variant_value,processed_models,slab_top_dict,id)
                                            continue
                                        elif variant_key =="facing=west,half=top,shape=outer_left":
                                            get_color(variant_value,processed_models,stairs_west_top_outer_left,id)
                                            continue
                                        elif variant_key =="facing=east,half=top,shape=outer_left":
                                            get_color(variant_value,processed_models,stairs_east_top_outer_left,id)
                                            continue
                                        elif variant_key =="facing=south,half=top,shape=outer_left":
                                            get_color(variant_value,processed_models,stairs_south_top_outer_left,id)
                                            continue
                                        elif variant_key =="facing=north,half=top,shape=outer_left":
                                            get_color(variant_value,processed_models,stairs_north_top_outer_left,id)
                                            continue
                                        elif variant_key =="facing=west,half=bottom,shape=outer_left":
                                            get_color(variant_value,processed_models,stairs_west_bottom_outer_left,id)
                                            continue
                                        elif variant_key =="facing=east,half=bottom,shape=outer_left":
                                            get_color(variant_value,processed_models,stairs_east_bottom_outer_left,id)
                                            continue
                                        elif variant_key =="facing=south,half=bottom,shape=outer_left":
                                            get_color(variant_value,processed_models,stairs_south_bottom_outer_left,id)
                                            continue
                                        elif variant_key =="facing=north,half=bottom,shape=outer_left":
                                            get_color(variant_value,processed_models,stairs_north_bottom_outer_left,id)
                                            continue
                                        elif variant_key =="facing=west,half=top,shape=straight":
                                            get_color(variant_value,processed_models,stairs_west_top_straight,id)
                                            continue
                                        elif variant_key =="facing=east,half=top,shape=straight":
                                            get_color(variant_value,processed_models,stairs_east_top_straight,id)
                                            continue
                                        elif variant_key =="facing=west,half=bottom,shape=straight":
                                            get_color(variant_value,processed_models,stairs_west_bottom_straight,id)
                                            continue
                                        elif variant_key =="facing=east,half=bottom,shape=straight":
                                            get_color(variant_value,processed_models,stairs_east_bottom_straight,id)
                                            continue
                                        elif variant_key =="facing=north,half=top,shape=straight":
                                            get_color(variant_value,processed_models,stairs_north_top_straight,id)
                                            continue
                                        elif variant_key =="facing=south,half=top,shape=straight":
                                            get_color(variant_value,processed_models,stairs_south_top_straight,id)
                                            continue
                                        elif variant_key =="facing=north,half=bottom,shape=straight":
                                            get_color(variant_value,processed_models,stairs_north_bottom_straight,id)
                                            continue
                                        elif variant_key =="facing=south,half=bottom,shape=straight":
                                            get_color(variant_value,processed_models,stairs_south_bottom_straight,id)
                                            continue
                                        elif variant_key =="facing=south,half=top,shape=inner_left":
                                            get_color(variant_value,processed_models,stairs_south_top_inner_left,id)
                                            continue
                                        elif variant_key =="facing=north,half=top,shape=inner_right":
                                            get_color(variant_value,processed_models,stairs_north_top_inner_right,id)
                                            continue
                                        elif variant_key =="facing=west,half=top,shape=inner_left":
                                            get_color(variant_value,processed_models,stairs_west_top_inner_left,id)
                                            continue
                                        elif variant_key =="facing=west,half=top,shape=inner_right":
                                            get_color(variant_value,processed_models,stairs_west_top_inner_right,id)
                                            continue
                                        elif variant_key =="facing=south,half=bottom,shape=inner_left":
                                            get_color(variant_value,processed_models,stairs_south_bottom_inner_left,id)
                                            continue
                                        elif variant_key =="facing=north,half=bottom,shape=inner_right":
                                            get_color(variant_value,processed_models,stairs_north_bottom_inner_right,id)
                                            continue
                                        elif variant_key =="facing=west,half=bottom,shape=inner_left":
                                            get_color(variant_value,processed_models,stairs_west_bottom_inner_left,id)
                                            continue
                                        elif variant_key =="facing=west,half=bottom,shape=inner_right":
                                            get_color(variant_value,processed_models,stairs_west_bottom_inner_right,id)
                                            continue

                                    else:
                                        id = str(dir + ":" + file.replace(".json", ""))

                                    if 'model' in variant_value:
                                        model = variant_value['model']

                                        if model in processed_models:
                                            continue
                                        processed_models.add(model)
                                        filepath = get_file_path(model, 'm')
                                        if filepath is None:
                                            continue
                                        dirname, filename = os.path.split(filepath)
                                        dirname = dirname + '\\'
                                        try:
                                            _, _, parent = get_all_data(dirname, filename)
                                            
                                            if parent == "block/cube":
                                                t, _, _ = get_all_data(dirname, filename)
                                                texture_counter = Counter(t.values())
                                                most_common_texture = texture_counter.most_common(1)[0][0]

                                                all_average_colors = []
                                                processed_textures = set()

                                                for value in t.values():
                                                    if value != most_common_texture:
                                                        continue

                                                    if value in processed_textures:
                                                        continue
                                                    processed_textures.add(value)

                                                    texture = get_file_path(value, 't')
                                                    average_color = calculate_average_color(texture)
                                                    all_average_colors.append(average_color)

                                                if all_average_colors:
                                                    overall_average_color = np.mean(all_average_colors, axis=0)
                                                    overall_average_color = np.round(overall_average_color, 2)
                                                    cube_dict[tuple(overall_average_color)] = id

                                        except Exception as e:
                                            pass
    # 将所有字典写入文件
    with open(os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin","colors","colors.py"), 'w') as models_file:
        dict_names = [
            "cube_dict",
            "slab_dict",
            "slab_top_dict",
            "stairs_west_top_outer_left",
            "stairs_east_top_outer_left",
            "stairs_south_top_outer_left",
            "stairs_north_top_outer_left",
            "stairs_west_bottom_outer_left",
            "stairs_east_bottom_outer_left",
            "stairs_south_bottom_outer_left",
            "stairs_north_bottom_outer_left",
            "stairs_west_top_straight",
            "stairs_east_top_straight",
            "stairs_west_bottom_straight",
            "stairs_east_bottom_straight",
            "stairs_north_top_straight",
            "stairs_south_top_straight",
            "stairs_north_bottom_straight",
            "stairs_south_bottom_straight",
            "stairs_south_top_inner_left",
            "stairs_north_top_inner_right",
            "stairs_west_top_inner_left",
            "stairs_west_top_inner_right",
            "stairs_south_bottom_inner_left",
            "stairs_north_bottom_inner_right",
            "stairs_west_bottom_inner_left",
            "stairs_west_bottom_inner_right",
        ]

        for dict_name in dict_names:
            models_file.write(f"{dict_name} = {{\n")
            write_model_dict(models_file, locals()[dict_name])
            models_file.write("}\n")

    print("finish")


classes=[ModInfo,Property,UnzipModOperator,UnzipResourcepacksOperator]


def register():
    threading.Thread(target=unzip_mods_files).start()
    threading.Thread(target=unzip_resourcepacks_files).start()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_properties = bpy.props.PointerProperty(type=Property)
    temp_dir = os.path.join(bpy.utils.script_path_user(), "addons", "BaiGave_Plugin", "temp")
    importlib.reload(config)
    #threading.Thread(target=read_blockstate_files, args=(temp_dir,config.config["version"])).start()
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
