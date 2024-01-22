from amulet_nbt import TAG_Compound, TAG_Int, TAG_Byte, TAG_String, TAG_Long, TAG_Double, TAG_Float, TAG_Short, TAG_List


def create_level(World_Name, SpawnX, SpawnY, SpawnZ, hardcore, Difficulty, allowCommands, LastPlayed, DayTime, Seed, GameType, OverworldGenerator_Type,
                announceAdvancements="True", blockExplosionDropDecay="True", commandBlockOutput="True",
                disableElytraMovementCheck="True", commandModificationBlockLimit="32768", disableRaids="True",
                doDaylightCycle="True", doEntityDrops="True", doFireTick="True", doImmediateRespawn="True",
                doInsomnia="True", doLimitedCrafting="True", doMobLoot="True", doMobSpawning="True",
                doPatrolSpawning="True", doTileDrops="True", doTraderSpawning="True", doVinesSpread="True",
                doWardenSpawning="True", doWeatherCycle="True", drowningDamage="True", fallDamage="True",
                fireDamage="True", forgiveDeadPlayers="True", freezeDamage="True", globalSoundEvents="True",
                keepInventory="True", lavaSourceConversion="True", logAdminCommands="True",
                maxCommandChainLength="65536", maxEntityCramming="12", mobExplosionDropDecay="True",
                mobGriefing="True", naturalRegeneration="True", playersSleepingPercentage="0",
                randomTickSpeed="0", reducedDebugInfo="False", sendCommandFeedback="True",
                showDeathMessages="True", snowAccumulationHeight="1", spawnRadius="10",
                spectatorsGenerateChunks="True", tntExplosionDropDecay="True", universalAnger="True",
                waterSourceConversion="True"):    
    data = TAG_Compound()
    data['version'] = TAG_Int(19133)
    data['GameType'] = TAG_Int(GameType)
    data['SpawnX'] = TAG_Int(SpawnX)
    data['SpawnY'] = TAG_Int(SpawnY)
    data['SpawnZ'] = TAG_Int(SpawnZ)
    data['hardcore'] = TAG_Byte(hardcore)
    data['Difficulty'] = TAG_Byte(Difficulty)
    data['allowCommands'] = TAG_Byte(allowCommands)
    data['LevelName'] = TAG_String(World_Name)
    data['LastPlayed'] = TAG_Long(LastPlayed)
    data['DayTime'] = TAG_Long(DayTime)
    data['Time'] = TAG_Long(1083)
    data['DataVersion'] = TAG_Int(3105)
    data['BorderCenterX'] = TAG_Double(0)
    data['BorderCenterZ'] = TAG_Double(0)
    data['BorderSize'] = TAG_Double(60000000)
    data['BorderSizeLerpTarget'] = TAG_Double(60000000)
    data['BorderSizeLerpTime'] = TAG_Long(0)
    data['BorderWarningBlocks'] = TAG_Double(5)
    data['BorderWarningTime'] = TAG_Double(15)
    data['BorderDamagePerBlock'] = TAG_Double(0.200000002980232)
    data['BorderSafeZone'] = TAG_Double(5)

    # 创建一个名为"GameRules"的标记，并添加规则数据到其中
    GameRules = TAG_Compound()
    GameRules['announceAdvancements'] = TAG_String(announceAdvancements)
    GameRules['blockExplosionDropDecay'] = TAG_String(blockExplosionDropDecay)
    GameRules['commandBlockOutput'] = TAG_String(commandBlockOutput)
    GameRules['disableElytraMovementCheck'] = TAG_String(disableElytraMovementCheck)
    GameRules['commandModificationBlockLimit'] = TAG_String(commandModificationBlockLimit)
    GameRules['disableRaids'] = TAG_String(disableRaids)
    GameRules['doDaylightCycle'] = TAG_String(doDaylightCycle)
    GameRules['doEntityDrops'] = TAG_String(doEntityDrops)
    GameRules['doFireTick'] = TAG_String(doFireTick)
    GameRules['doImmediateRespawn'] = TAG_String(doImmediateRespawn)
    GameRules['doInsomnia'] = TAG_String(doInsomnia)
    GameRules['doLimitedCrafting'] = TAG_String(doLimitedCrafting)
    GameRules['doMobLoot'] = TAG_String(doMobLoot)
    GameRules['doMobSpawning'] = TAG_String(doMobSpawning)
    GameRules['doPatrolSpawning'] = TAG_String(doPatrolSpawning)
    GameRules['doTileDrops'] = TAG_String(doTileDrops)
    GameRules['doTraderSpawning'] = TAG_String(doTraderSpawning)
    GameRules['doVinesSpread'] = TAG_String(doVinesSpread)
    GameRules['doWardenSpawning'] = TAG_String(doWardenSpawning)
    GameRules['doWeatherCycle'] = TAG_String(doWeatherCycle)
    GameRules['drowningDamage'] = TAG_String(drowningDamage)
    GameRules['fallDamage'] = TAG_String(fallDamage)
    GameRules['fireDamage'] = TAG_String(fireDamage)
    GameRules['forgiveDeadPlayers'] = TAG_String(forgiveDeadPlayers)
    GameRules['freezeDamage'] = TAG_String(freezeDamage)
    GameRules['globalSoundEvents'] = TAG_String(globalSoundEvents)
    GameRules['keepInventory'] = TAG_String(keepInventory)
    GameRules['lavaSourceConversion'] = TAG_String(lavaSourceConversion)
    GameRules['logAdminCommands'] = TAG_String(logAdminCommands)
    GameRules['maxCommandChainLength'] = TAG_String(maxCommandChainLength)
    GameRules['maxEntityCramming'] = TAG_String(maxEntityCramming)
    GameRules['mobExplosionDropDecay'] = TAG_String(mobExplosionDropDecay)
    GameRules['mobGriefing'] = TAG_String(mobGriefing)
    GameRules['naturalRegeneration'] = TAG_String(naturalRegeneration)
    GameRules['playersSleepingPercentage'] = TAG_String(playersSleepingPercentage)
    GameRules['randomTickSpeed'] = TAG_String(randomTickSpeed)
    GameRules['reducedDebugInfo'] = TAG_String(reducedDebugInfo)
    GameRules['sendCommandFeedback'] = TAG_String(sendCommandFeedback)
    GameRules['showDeathMessages'] = TAG_String(showDeathMessages)
    GameRules['snowAccumulationHeight'] = TAG_String(snowAccumulationHeight)
    GameRules['spawnRadius'] = TAG_String(spawnRadius)
    GameRules['spectatorsGenerateChunks'] = TAG_String(spectatorsGenerateChunks)
    GameRules['tntExplosionDropDecay'] = TAG_String(tntExplosionDropDecay)
    GameRules['universalAnger'] = TAG_String(universalAnger)
    GameRules['waterSourceConversion'] = TAG_String(waterSourceConversion)

    # 创建一个名为"Version"的标记
    abilities = TAG_Compound()
    abilities['flying'] = TAG_Byte(0)
    abilities['flySpeed'] = TAG_Float(1.1)
    abilities['instabuild'] = TAG_Byte(1)
    abilities['invulnerable'] = TAG_Byte(1)
    abilities['mayBuild'] = TAG_Byte(1)
    abilities['mayfly'] = TAG_Byte(1)
    abilities['walkSpeed'] = TAG_Float(1.1)

    # 创建一个名为"Player"的标记，并添加玩家数据到其中
    player = TAG_Compound()
    player['Health'] = TAG_Short(20)
    player['SpawnX'] = TAG_Int(SpawnX)
    player['SpawnY'] = TAG_Int(SpawnY)
    player['SpawnZ'] = TAG_Int(SpawnZ)
    player['SpawnFoced'] = TAG_Byte(1)
    player['foodLevel'] = TAG_Int(20)
    player['XpLevel'] = TAG_Int(0)
    player['XpTotal'] = TAG_Int(0)
    player['XpSeed'] = TAG_Long(0)
    player['Score'] = TAG_Int(0)
    player['Inventory'] = TAG_List()
    player['abilities'] = abilities
    player['Pos'] = TAG_List([TAG_Double(SpawnX), TAG_Double(SpawnY), TAG_Double(SpawnZ)])

    # 创建一个名为"Version"的标记
    Version = TAG_Compound()
    Version['Id'] = TAG_Int(3105)
    Version['Name'] = TAG_String("blender")
    Version['Snapshot'] = TAG_Byte(0)

    # 创建一个名为"WorldGenSettings"的标记
    WorldGenSettings = TAG_Compound()
    #是否生成结构？
    WorldGenSettings['generate_features'] = TAG_Byte(0)
    WorldGenSettings['bonus_chest'] = TAG_Byte(0)
    WorldGenSettings['seed'] = TAG_Long(Seed)

    # 创建一个名为"overworld_biome_source"的标记
    overworld_biome_source = TAG_Compound()
    overworld_biome_source['preset'] = TAG_String("minecraft:overworld")
    overworld_biome_source['type'] = TAG_String("minecraft:multi_noise")

    # 创建一个名为"overworld_generator"的标记
    overworld_generator = TAG_Compound()
    
    overworld_generator['type'] = TAG_String(OverworldGenerator_Type)
    print(OverworldGenerator_Type)
    if OverworldGenerator_Type =="noise":
        overworld_generator['settings'] = TAG_String("minecraft:large_biomes")
        overworld_generator['biome_source'] = overworld_biome_source
        overworld_generator['seed'] = TAG_Long(Seed)
    elif OverworldGenerator_Type =="flat":
        settings = TAG_Compound()
        settings['layers']=TAG_List()
        overworld_generator['settings'] = settings
    elif OverworldGenerator_Type=="debug":
        pass

    # 创建一个名为"overworld"的标记
    overworld = TAG_Compound()
    overworld['generator'] = overworld_generator
    overworld['type'] = TAG_String("minecraft:overworld")

    # 创建一个名为"the_end_biome_source"的标记
    the_end_biome_source = TAG_Compound()
    the_end_biome_source['seed'] = TAG_Long(Seed)
    the_end_biome_source['type'] = TAG_String("minecraft:the_end")

    # 创建一个名为"the_end_generator"的标记
    the_end_generator = TAG_Compound()
    the_end_generator['biome_source'] = the_end_biome_source
    the_end_generator['seed'] = TAG_Long(Seed)
    the_end_generator['settings'] = TAG_String("minecraft:end")
    the_end_generator['type'] = TAG_String("minecraft:noise")

    # 创建一个名为"the_end"的标记
    the_end = TAG_Compound()
    the_end['generator'] = the_end_generator
    the_end['type'] = TAG_String("minecraft:the_end")

    # 创建一个名为"the_nether_biome_source"的标记
    the_nether_biome_source = TAG_Compound()
    the_nether_biome_source['preset'] = TAG_String("minecraft:nether")
    the_nether_biome_source['type'] = TAG_String("minecraft:multi_noise")

    # 创建一个名为"the_nether_generator"的标记
    the_nether_generator = TAG_Compound()
    the_nether_generator['biome_source'] = the_nether_biome_source
    the_nether_generator['seed'] = TAG_Long(Seed)
    the_nether_generator['settings'] = TAG_String("minecraft:nether")
    the_nether_generator['type'] = TAG_String("minecraft:noise")

    # 创建一个名为"the_nether"的标记
    the_nether = TAG_Compound()
    the_nether['generator'] = the_nether_generator
    the_nether['type'] = TAG_String("minecraft:the_nether")

    # 创建一个名为"dimensions"的标记
    dimensions = TAG_Compound()
    dimensions['minecraft:overworld'] = overworld
    dimensions['minecraft:the_end'] = the_end
    dimensions['minecraft:the_nether'] = the_nether

    WorldGenSettings['dimensions'] = dimensions

    # 将"Player"标记添加到"Data"中
    data['Player'] = player
    data['Version'] = Version
    data['WorldGenSettings'] = WorldGenSettings
    data['GameRules'] = GameRules
    level_dat = TAG_Compound({'Data': data})

    return level_dat
