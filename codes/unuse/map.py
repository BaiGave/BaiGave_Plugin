import bpy
import time
import amulet
import math
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from .color_dict import color_dict
from .map_functions import scene, create_images, process_chunk, update_images

processed_chunks = []

class Map(bpy.types.Operator):
    """生成地图(性能有问题)"""
    bl_idname = "baigave.spawn_map"
    bl_label = "生成地图"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def __init__(self):
        self.start_time = 0
        self.executor = None
        self.futures = []
        self.completed_images = 0

    def execute(self, context):
        # 获取当前时间
        self.start_time = time.time()
        self.executor = ThreadPoolExecutor()
        global level 
        # 加载地图数据
        self.level = amulet.load_level(self.filepath)
        level = self.level
        self.player_location = self.level.get_player(list(self.level.all_player_ids())[0]).location
        self.player_chunk_location = (int(self.player_location[0] / 16), int(self.player_location[2] / 16))
        self.chunk_coords = self.get_circular_chunk_coords(self.player_chunk_location, self.level)
        self.scale = 1
        self.min_x = min(self.chunk_coords, key=lambda c: c[0])[0]
        self.max_x = max(self.chunk_coords, key=lambda c: c[0])[0]
        self.min_z = min(self.chunk_coords, key=lambda c: c[1])[1]
        self.max_z = max(self.chunk_coords, key=lambda c: c[1])[1]
        self.chunk_size = 16 // self.scale
        self.image_size = self.chunk_size * 32 // self.scale
        self.num_images_x = math.ceil((self.max_x - self.min_x + 1) / 32)
        self.num_images_z = math.ceil((self.max_z - self.min_z + 1) / 32)

        # 创建图像和像素数据列表
        self.images = [bpy.data.images.new(f"r.{x}.{z}", width=self.image_size, height=self.image_size)
                       for z in range(self.num_images_z) for x in range(self.num_images_x)]
        self.pixel_data_list = [np.zeros((self.image_size, self.image_size, 4), dtype=np.float32)
                                for _ in range(self.num_images_z * self.num_images_x)]

        #scene()
        create_images(self.images, self.pixel_data_list)

        # 启动多线程任务
        for chunk_coord in self.chunk_coords:
            future = self.executor.submit(self.process_chunk_threaded, chunk_coord)
            self.futures.append(future)

        return {'RUNNING_MODAL'}

    def get_circular_chunk_coords(self, center_coord, level):
        chunk_coords = list(level.all_chunk_coords("minecraft:overworld"))
        chunk_coords.sort(key=lambda coord: math.sqrt((coord[0] + center_coord[0]) ** 2 + (coord[1] + center_coord[1]) ** 2))
        return chunk_coords

    def process_chunk_threaded(self, chunk_coord):
        chunk = process_chunk(chunk_coord, self.chunk_size, self.scale, self.min_x, self.min_z, self.image_size,
                              self.num_images_x, self.num_images_z, self.level, self.pixel_data_list, color_dict)
        if chunk is not None:
            processed_chunks.append(chunk)
            self.completed_images += 1
            if self.completed_images % 5 == 0:
                update_images(self.images, self.pixel_data_list)
                bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)

    def modal(self, context, event):
        if event.type == 'ESC':
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # 更新图像
            update_images(self.images, self.pixel_data_list)

            # 检查是否所有任务完成
            if all(future.done() for future in self.futures):
                self.level.close()
                self.executor.shutdown(wait=False)

                # 获取当前时间
                end_time = time.time()

                # 计算代码块执行时间
                execution_time = end_time - self.start_time

                # 打印执行时间
                print("代码块执行时间：", execution_time, "秒")

                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def cancel(self, context):
        self.level.close()
        self.executor.shutdown(wait=False)
        return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
classes=[Map]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
