import bpy
import time
import shutil
import os
from .functions.tip import ShowMessageBox
from .unuse.level import create_level


class OpenFileManagerOperator(bpy.types.Operator):
    bl_idname = "baigave.open_saves_folder"
    bl_label = "打开文件管理器"

    def execute(self, context):
        # 构建路径
        folderpath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"saves")

        # 打开文件管理器并导航到指定路径
        bpy.ops.wm.path_open(filepath=folderpath)

        return {'FINISHED'}
class CreateWorld(bpy.types.Operator):
    """创建世界"""
    bl_idname = "baigave.create_world"
    bl_label = "创建存档"

    # 定义操作的执行函数
    def execute(self, context):
        World_Name = context.scene.world_name
        SpawnX = context.scene.spawn_x
        SpawnY = context.scene.spawn_y
        SpawnZ = context.scene.spawn_z
        hardcore = context.scene.hardcore
        Difficulty = context.scene.difficulty
        gametype = context.scene.gametype
        allowCommands = context.scene.allow_commands
        HeightLimit =context.scene.breaking_the_height_limit
        Overworld_Generator_Type=context.scene.overworld_generator_type
        LastPlayed = int(round(time.time() * 1000))
        DayTime = context.scene.day_time
        Seed = context.scene.seed

        #成就
        announce_advancements = bpy.context.scene.announce_advancements
        block_explosion_drop_decay = bpy.context.scene.block_explosion_drop_decay
        command_block_output = bpy.context.scene.command_block_output
        disable_elytra_movement_check = bpy.context.scene.disable_elytra_movement_check
        command_modification_block_limit = bpy.context.scene.command_modification_block_limit
        disable_raids = bpy.context.scene.disable_raids
        do_daylight_cycle = bpy.context.scene.do_daylight_cycle
        do_entity_drops = bpy.context.scene.do_entity_drops
        do_fire_tick = bpy.context.scene.do_fire_tick
        do_immediate_respawn = bpy.context.scene.do_immediate_respawn
        do_insomnia = bpy.context.scene.do_insomnia
        do_limited_crafting = bpy.context.scene.do_limited_crafting
        do_mob_loot = bpy.context.scene.do_mob_loot
        do_mob_spawning = bpy.context.scene.do_mob_spawning
        do_patrol_spawning = bpy.context.scene.do_patrol_spawning
        do_tile_drops = bpy.context.scene.do_tile_drops
        do_trader_spawning = bpy.context.scene.do_trader_spawning
        do_vines_spread = bpy.context.scene.do_vines_spread
        do_warden_spawning = bpy.context.scene.do_warden_spawning
        do_weather_cycle = bpy.context.scene.do_weather_cycle
        drowning_damage = bpy.context.scene.drowning_damage
        fall_damage = bpy.context.scene.fall_damage
        fire_damage = bpy.context.scene.fire_damage
        forgive_dead_players = bpy.context.scene.forgive_dead_players
        freeze_damage = bpy.context.scene.freeze_damage
        global_sound_events = bpy.context.scene.global_sound_events
        keep_inventory = bpy.context.scene.keep_inventory
        lava_source_conversion = bpy.context.scene.lava_source_conversion
        log_admin_commands = bpy.context.scene.log_admin_commands
        max_entity_cramming = bpy.context.scene.max_entity_cramming
        mob_explosion_drop_decay = bpy.context.scene.mob_explosion_drop_decay
        mob_griefing = bpy.context.scene.mob_griefing
        natural_regeneration = bpy.context.scene.natural_regeneration
        players_sleeping_percentage = bpy.context.scene.players_sleeping_percentage
        random_tick_speed = bpy.context.scene.random_tick_speed
        reduced_debug_info = bpy.context.scene.reduced_debug_info
        send_command_feedback = bpy.context.scene.send_command_feedback
        show_death_messages = bpy.context.scene.show_death_messages
        snow_accumulation_height = bpy.context.scene.snow_accumulation_height
        spawn_radius = bpy.context.scene.spawn_radius
        spectators_generate_chunks = bpy.context.scene.spectators_generate_chunks
        tnt_explosion_drop_decay = bpy.context.scene.tnt_explosion_drop_decay
        universal_anger = bpy.context.scene.universal_anger
        water_source_conversion = bpy.context.scene.water_source_conversion
        max_entity_cramming = bpy.context.scene.max_entity_cramming
        snow_accumulation_height = bpy.context.scene.snow_accumulation_height
        spawn_radius = bpy.context.scene.spawn_radius
        players_sleeping_percentage = bpy.context.scene.players_sleeping_percentage
        random_tick_speed = bpy.context.scene.random_tick_speed
        max_command_chain_length =bpy.context.scene.max_command_chain_length
        command_modification_block_limit = bpy.context.scene.command_modification_block_limit

        #玩家能力：
        flying = bpy.context.scene.flying
        flySpeed = bpy.context.scene.flySpeed
        instabuild = bpy.context.scene.instabuild
        invulnerable = bpy.context.scene.invulnerable
        mayBuild = bpy.context.scene.mayBuild
        mayfly = bpy.context.scene.mayfly
        walkSpeed = bpy.context.scene.walkSpeed

        luck = bpy.context.scene.luck
        max_health = bpy.context.scene.max_health
        knockback_resistance = bpy.context.scene.knockback_resistance
        movement_speed = bpy.context.scene.movement_speed
        armor = bpy.context.scene.armor
        armor_toughness = bpy.context.scene.armor_toughness
        attack_damage = bpy.context.scene.attack_damage
        attack_speed = bpy.context.scene.attack_speed


        folderpath =os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"saves",World_Name)

        # 创建存档文件夹
        if not os.path.exists(folderpath):
            os.makedirs(folderpath)
        level_dat = create_level(
    World_Name, SpawnX, SpawnY, SpawnZ, hardcore, Difficulty, allowCommands, LastPlayed, DayTime, Seed, gametype, Overworld_Generator_Type,
    announce_advancements, block_explosion_drop_decay, command_block_output, disable_elytra_movement_check, command_modification_block_limit,
    disable_raids, do_daylight_cycle, do_entity_drops, do_fire_tick, do_immediate_respawn, do_insomnia, do_limited_crafting, do_mob_loot,
    do_mob_spawning, do_patrol_spawning, do_tile_drops, do_trader_spawning, do_vines_spread, do_warden_spawning, do_weather_cycle, drowning_damage,
    fall_damage, fire_damage, forgive_dead_players, freeze_damage, global_sound_events, keep_inventory, lava_source_conversion, log_admin_commands,
    max_command_chain_length,max_entity_cramming, mob_explosion_drop_decay, mob_griefing, natural_regeneration, players_sleeping_percentage,
    random_tick_speed, reduced_debug_info, send_command_feedback, show_death_messages, snow_accumulation_height, spawn_radius, spectators_generate_chunks,
    tnt_explosion_drop_decay, universal_anger, water_source_conversion,HeightLimit,flying, flySpeed, instabuild, invulnerable, mayBuild, mayfly, walkSpeed,
    luck,max_health,knockback_resistance,movement_speed,armor,armor_toughness,attack_damage,attack_speed

)
        # 将NBT数据写入文件
        filepath =os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"saves",World_Name,"level.dat")
        level_dat.save_to(filepath)
        if HeightLimit == "1":
            source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"datapacks", "datapacks.zip")
            destination_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),"saves", World_Name, "datapacks")
            # 创建目标文件夹（如果不存在）
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)
            
            # 复制文件
            shutil.copy(source_path, destination_path)
        ShowMessageBox("世界创建成功！","白给的插件",link_text="点击这里前往导出文件夹", link_operator=OpenFileManagerOperator)
        
        return {'FINISHED'}


    
classes=[OpenFileManagerOperator,CreateWorld]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)