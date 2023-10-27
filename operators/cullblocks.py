from .classification import air_blocks
from .blockstates import blockstates

def CullBlocks(coord, d,vertices,faces,direction,texture_list,uv_list,uv_rotation_list,vertices_dict):
    # 如果坐标在字典中，获取对应的方块 ID
    if coord in d:
        block_id = d[coord]
        # 定义一个元组，存储六个方向的偏移量，按照 上下北南东西 的顺序排序
        offsets = ((0, -1, 0),  # 东
                   (0, 1, 0),  # 西
                   (-1, 0, 0),  # 北
                   (1, 0, 0),  # 南
                   (0, 0, -1),  # 下
                   (0, 0, 1))  # 上
        # 使用列表推导式生成相邻坐标
        adjacent_coords = [(coord[0] + offset[0], coord[1] + offset[1], coord[2] + offset[2]) for offset in offsets]
        # 使用 any 函数判断是否有空气方块
        has_air = [adj_coord not in d or d[adj_coord].split('[')[0] in air_blocks for adj_coord in adjacent_coords]
        # 将 has_air 中的值按照 东西北南上下 的顺序排列
        has_air = [has_air[2], has_air[3], has_air[0], has_air[1], has_air[5], has_air[4]]
        
        # 如果有空气方块，输出方块
        if any(has_air):
            return blockstates((coord[0],coord[1],coord[2]), block_id, has_air,vertices,faces,direction,texture_list,uv_list,uv_rotation_list,vertices_dict)
        # 如果没有空气方块，返回
        else:
            return vertices,faces,direction,texture_list,uv_list,uv_rotation_list

