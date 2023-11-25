from ..dependencies import nbtlib
def create_level(World_Name,SpawnX,SpawnY,SpawnZ,hardcore,Difficulty,allowCommands,LastPlayed,DayTime,Seed):    
# 创建一个名为"Data"的标记，并添加一些基本的数据到其中
    data = nbtlib.Compound()
    data['version'] = nbtlib.Int(19133)
    data['GameType'] = nbtlib.Int(1)
    data['SpawnX'] = nbtlib.Int(SpawnX)
    data['SpawnY'] = nbtlib.Int(SpawnY)
    data['SpawnZ'] = nbtlib.Int(SpawnZ)
    data['MapHeight'] = nbtlib.Int(320)
    data['hardcore'] = nbtlib.Byte(hardcore)
    data['Difficulty'] = nbtlib.Byte(Difficulty)
    data['allowCommands'] = nbtlib.Byte(allowCommands)
    data['LevelName'] = nbtlib.String(World_Name)
    data['LastPlayed'] = nbtlib.Long(LastPlayed)
    data['DayTime'] = nbtlib.Long(DayTime)
    data['DataVersion'] = nbtlib.Int(3105)
    data['BorderCenterX'] = nbtlib.Double(0)
    data['BorderCenterZ'] = nbtlib.Double(0)
    data['BorderSize'] = nbtlib.Double(60000000)
    data['BorderSizeLerpTarget'] = nbtlib.Double(60000000)
    data['BorderSizeLerpTime'] = nbtlib.Long(0)
    data['BorderWarningBlocks'] = nbtlib.Double(5)
    data['BorderWarningTime'] = nbtlib.Double(15)
    data['BorderDamagePerBlock'] = nbtlib.Double(0.200000002980232)
    data['BorderSafeZone'] = nbtlib.Double(5)
    

    # 创建一个名为"Player"的标记，并添加玩家数据到其中
    GameRules = nbtlib.Compound()
    # 是否在聊天窗口中通知玩家进度的完成情况
    GameRules['announceAdvancements'] = nbtlib.String("True")

    # 方块爆炸后是否掉落物品和经验
    GameRules['blockExplosionDropDecay'] = nbtlib.String("True")

    # 命令方块是否输出执行结果
    GameRules['commandBlockOutput'] = nbtlib.String("True")

    # 是否禁用飞行翼的移动检测
    GameRules['disableElytraMovementCheck'] = nbtlib.String("True")

    # 可以在单个命令块中执行的命令条数限制 #不起作用
    GameRules['commandModificationBlockLimit'] = nbtlib.String(200)

    # 是否禁用袭击事件
    GameRules['disableRaids'] = nbtlib.String("True")

    # 是否启用白天黑夜交替
    GameRules['doDaylightCycle'] = nbtlib.String("True")

    # 实体死亡时是否掉落物品
    GameRules['doEntityDrops'] = nbtlib.String("True")

    # 是否使火焰逐渐蔓延并对周围方块造成伤害
    GameRules['doFireTick'] = nbtlib.String("True")

    # 是否立即重生而不等待复活画面
    GameRules['doImmediateRespawn'] = nbtlib.String("True")

    # 是否启用失眠效果（只在夜晚出现）
    GameRules['doInsomnia'] = nbtlib.String("True")

    # 是否限制玩家的合成配方
    GameRules['doLimitedCrafting'] = nbtlib.String("True")

    # 怪物死亡时是否掉落物品
    GameRules['doMobLoot'] = nbtlib.String("True")

    # 是否生成怪物
    GameRules['doMobSpawning'] = nbtlib.String("True")

    # 是否生成巡逻队
    GameRules['doPatrolSpawning'] = nbtlib.String("True")

    # 方块破坏时是否掉落物品
    GameRules['doTileDrops'] = nbtlib.String("True")

    # 是否生成村民商人
    GameRules['doTraderSpawning'] = nbtlib.String("True")

    # 是否使藤蔓逐渐蔓延
    GameRules['doVinesSpread'] = nbtlib.String("True")

    # 是否生成守卫者
    GameRules['doWardenSpawning'] = nbtlib.String("True")

    # 是否启用天气系统
    GameRules['doWeatherCycle'] = nbtlib.String("True")

    # 是否启用溺水伤害
    GameRules['drowningDamage'] = nbtlib.String("True")

    # 是否启用坠落伤害
    GameRules['fallDamage'] = nbtlib.String("True")

    # 是否启用火焰伤害
    GameRules['fireDamage'] = nbtlib.String("True")

    # 是否允许死亡的玩家回到他们死亡的地方
    GameRules['forgiveDeadPlayers'] = nbtlib.String("True")

    # 是否启用冰冻伤害
    GameRules['freezeDamage'] = nbtlib.String("True")

    # 是否在全局广播声音事件
    GameRules['globalSoundEvents'] = nbtlib.String("True")

    # 死亡时是否保留背包物品
    GameRules['keepInventory'] = nbtlib.String("True")

    # 是否启用岩浆源方块转换
    GameRules['lavaSourceConversion'] = nbtlib.String("True")

    # 是否记录管理员执行的命令
    GameRules['logAdminCommands'] = nbtlib.String("True")

    # 命令执行的最大长度
    GameRules['maxCommandChainLength'] = nbtlib.String(65536)

    # 实体拥挤时的最大数量
    GameRules['maxEntityCramming'] = nbtlib.String(12)

    # 怪物死亡时是否掉落物品和经验
    GameRules['mobExplosionDropDecay'] = nbtlib.String("True")

    # 怪物是否可以破坏方块
    GameRules['mobGriefing'] = nbtlib.String("True")

    # 是否启用自然生命恢复
    GameRules['naturalRegeneration'] = nbtlib.String("True")

    # 需要睡眠的玩家所占的百分比
    GameRules['playersSleepingPercentage'] = nbtlib.String(0)

    # 方块随机刻计时器的速度
    GameRules['randomTickSpeed'] = nbtlib.String(0)

    # 是否对玩家隐藏调试信息
    GameRules['reducedDebugInfo'] = nbtlib.String("False")

    # 命令执行后是否向玩家显示执行结果
    GameRules['sendCommandFeedback'] = nbtlib.String("True")

    # 是否在聊天窗口中显示玩家死亡消息
    GameRules['showDeathMessages'] = nbtlib.String("True")

    # 降雪时积雪高度
    GameRules['snowAccumulationHeight'] = nbtlib.String(1)

    # 生成点周围的半径
    GameRules['spawnRadius'] = nbtlib.String(10)

    # 观察者是否可以生成新的区块
    GameRules['spectatorsGenerateChunks'] = nbtlib.String("True")

    # 炸药爆炸后是否掉落物品和经验
    GameRules['tntExplosionDropDecay'] = nbtlib.String("True")

    # 是否启用全局愤怒机制
    GameRules['universalAnger'] = nbtlib.String("True")

    # 是否启用水源方块转换
    GameRules['waterSourceConversion'] = nbtlib.String("True")


    # 创建一个名为"Version"的标记
    abilities = nbtlib.Compound()
    abilities['flying'] = nbtlib.Byte(0)
    abilities['flySpeed'] = nbtlib.Float(1.1)
    abilities['instabuild'] = nbtlib.Byte(1)
    abilities['invulnerable'] = nbtlib.Byte(1)
    abilities['mayBuild'] = nbtlib.Byte(1)
    abilities['mayfly'] = nbtlib.Byte(1)
    abilities['walkSpeed'] = nbtlib.Float(1.1)


    # 创建一个名为"Player"的标记，并添加玩家数据到其中
    player = nbtlib.Compound()
    player['Health'] = nbtlib.Short(20)
    player['SpawnX'] = nbtlib.Int(SpawnX)
    player['SpawnY'] = nbtlib.Int(SpawnY)
    player['SpawnZ'] = nbtlib.Int(SpawnZ)
    player['SpawnFoced'] = nbtlib.Byte(1)
    player['foodLevel'] = nbtlib.Int(20)
    player['XpLevel'] = nbtlib.Int(1110)
    player['XpTotal'] = nbtlib.Int(0)
    player['XpSeed'] = nbtlib.Long(0)
    player['Score'] = nbtlib.Int(0)
    player['Inventory'] = nbtlib.List[nbtlib.Compound]()
    player['abilities'] =abilities
    # 添加玩家的坐标信息
    player['Pos'] = nbtlib.List[nbtlib.Double]([nbtlib.Double(SpawnX), nbtlib.Double(SpawnY), nbtlib.Double(SpawnZ)])

    # 创建一个名为"Version"的标记
    Version = nbtlib.Compound()
    Version['Id'] = nbtlib.Int(3105)
    Version['Name'] = nbtlib.String("blender")
    Version['Snapshot'] = nbtlib.Byte(0)

    # 创建一个名为"WorldGenSettings"的标记
    WorldGenSettings = nbtlib.Compound()
    WorldGenSettings['generate_features'] = nbtlib.Byte(0)
    WorldGenSettings['bonus_chest'] = nbtlib.Byte(0)
    WorldGenSettings['seed'] = nbtlib.Long(Seed)
    
    # 创建一个名为"overworld_biome_source"的标记
    overworld_biome_source = nbtlib.Compound()
    overworld_biome_source['preset'] = nbtlib.String("minecraft:overworld")
    overworld_biome_source['type'] = nbtlib.String("minecraft:multi_noise")

    # 创建一个名为"overworld_generator"的标记
    overworld_generator = nbtlib.Compound()
    overworld_generator['biome_source'] = overworld_biome_source
    overworld_generator['seed'] = nbtlib.Long(Seed)
    overworld_generator['settings'] = nbtlib.String("minecraft:large_biomes")
    overworld_generator['type'] = nbtlib.String("minecraft:noise")

    # 创建一个名为"overworld"的标记
    overworld = nbtlib.Compound()
    overworld['generator'] = overworld_generator
    overworld['type'] = nbtlib.String("minecraft:overworld")

    
    # 创建一个名为"the_end_biome_source"的标记
    the_end_biome_source = nbtlib.Compound()
    the_end_biome_source['seed'] = nbtlib.Long(Seed)
    the_end_biome_source['type'] = nbtlib.String("minecraft:the_end")

    # 创建一个名为"the_end_generator"的标记
    the_end_generator = nbtlib.Compound()
    the_end_generator['biome_source'] = the_end_biome_source
    the_end_generator['seed'] = nbtlib.Long(Seed)
    the_end_generator['settings'] = nbtlib.String("minecraft:end")
    the_end_generator['type'] = nbtlib.String("minecraft:noise")

    # 创建一个名为"the_end"的标记
    the_end = nbtlib.Compound()
    the_end['generator'] = the_end_generator
    the_end['type'] = nbtlib.String("minecraft:the_end")

    
    # 创建一个名为"the_nether_biome_source"的标记
    the_nether_biome_source = nbtlib.Compound()
    the_nether_biome_source['preset'] = nbtlib.String("minecraft:nether")
    the_nether_biome_source['type'] = nbtlib.String("minecraft:multi_noise")

    # 创建一个名为"the_nether_generator"的标记
    the_nether_generator = nbtlib.Compound()
    the_nether_generator['biome_source'] = the_nether_biome_source
    the_nether_generator['seed'] = nbtlib.Long(Seed)
    the_nether_generator['settings'] = nbtlib.String("minecraft:nether")
    the_nether_generator['type'] = nbtlib.String("minecraft:noise")
    
    # 创建一个名为"the_nether"的标记
    the_nether = nbtlib.Compound()
    the_nether['generator'] = the_nether_generator
    the_nether['type'] = nbtlib.String("minecraft:the_nether")


    # 创建一个名为"dimensions"的标记
    dimensions = nbtlib.Compound()
    dimensions['minecraft:overworld'] = overworld
    dimensions['minecraft:the_end'] = the_end
    dimensions['minecraft:the_nether'] = the_nether

    WorldGenSettings['dimensions'] =dimensions 
    
    # 将"Player"标记添加到"Data"中
    data['Player'] = player
    data['Version'] = Version
    data['WorldGenSettings'] = WorldGenSettings
    data['GameRules'] = GameRules
    d=nbtlib.Compound({'Data': data})
    # 创建一个名为"level.dat"的标记，并将"Data"标记添加到其中
    level_dat = nbtlib.Compound({'': d})
    return level_dat