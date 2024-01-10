from ..blockstates import blockstates
from ..classification_files.block_type import air_blocks

def section(section, level, y, vertices, faces, texture_list, uv_list, direction, uv_rotation_list, vertices_dict):
    # 遍历多维数组
    for i in range(len(section)):         # 遍历第一维
        for j in range(len(section[i])):  # 遍历第二维
            for k in range(len(section[i][j])):  # 遍历第三维
                blockid = level.block_palette[section[i][j][k]]
                if str(blockid).startswith("universal_minecraft"):
                    blockid = level.translation_manager.get_version("java", (1, 20, 0)).block.from_universal(blockid)[0]
                    
                if blockid != "minecraft:air":
                    # 检查方块六个方向是否有空气
                    has_air = [False, False, False, False, False, False]  # 东西北南上下
                    if i > 0 and str(level.translation_manager.get_version("java", (1, 20, 0)).block.from_universal(level.block_palette[section[i-1][j][k]])[0]) in air_blocks:
                        has_air[0] = True  # 东方向
                    if i < len(section) - 1 and str(level.translation_manager.get_version("java", (1, 20, 0)).block.from_universal(level.block_palette[section[i+1][j][k]])[0]) in air_blocks:
                        has_air[1] = True  # 西方向
                    if j > 0 and str(level.translation_manager.get_version("java", (1, 20, 0)).block.from_universal(level.block_palette[section[i][j-1][k]])[0]) in air_blocks:
                        has_air[5] = True  # 北方向
                    if j < len(section[i]) - 1 and str(level.translation_manager.get_version("java", (1, 20, 0)).block.from_universal(level.block_palette[section[i][j+1][k]])[0]) in air_blocks:
                        has_air[4] = True  # 南方向
                    if k > 0 and str(level.translation_manager.get_version("java", (1, 20, 0)).block.from_universal(level.block_palette[section[i][j][k-1]])[0]) in air_blocks:
                        has_air[3] = True  # 上方向
                    if k < len(section[i][j]) - 1 and str(level.translation_manager.get_version("java", (1, 20, 0)).block.from_universal(level.block_palette[section[i][j][k+1]])[0]) in air_blocks:
                        has_air[2] = True  # 下方向

                    if any(has_air):
                        blockstates((i, k, (j + y*16)), str(blockid), has_air, vertices, faces, direction, texture_list, uv_list, uv_rotation_list, vertices_dict)
    return vertices, faces, texture_list, uv_list, direction, uv_rotation_list, vertices_dict
