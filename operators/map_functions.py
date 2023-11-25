import bpy
import itertools


def process_chunk(chunk_coord, chunk_size, scale, min_x, min_z, image_size, num_images_x, num_images_z, level, pixel_data_list, color_dict):
    x, z = chunk_coord
    x_start = x * chunk_size
    z_start = z * chunk_size
    chunk = level.get_chunk(x, z, "minecraft:overworld")
    if chunk.misc['height_mapC'].get('WORLD_SURFACE', None) is not None:
        pixel_coords = itertools.product(
            range(x_start, x_start + chunk_size, scale),
            range(z_start, z_start + chunk_size, scale)
        )

        for pixel_x, pixel_z in pixel_coords:
            temp_z = abs(pixel_z % chunk_size)
            temp_x = abs(pixel_x % chunk_size)
            y = chunk.misc['height_mapC'].get('WORLD_SURFACE', None)[temp_z][temp_x] - 1
            block = chunk.get_block(temp_x, y, temp_z)
            if str(block).startswith("universal_minecraft"):
                block = level.translation_manager.get_version("java", (1, 20, 0)).block.from_universal(block)[0]

            block = str(block).split('[')[0]
            color = color_dict.get(block, (1, 1, 1))
            pixel_x = (pixel_x - min_x * chunk_size) // scale
            pixel_z = (pixel_z - min_z * chunk_size) // scale

            pixel_data_index = pixel_z // image_size * num_images_x + pixel_x // image_size
            pixel_data = pixel_data_list[pixel_data_index]
            pixel = pixel_data[pixel_z % image_size, pixel_x % image_size]

            pixel[0] = color[0] / 255.0
            pixel[1] = color[1] / 255.0
            pixel[2] = color[2] / 255.0
            pixel[3] = 1.0
        return chunk


def create_material(image_name):
    material_name = f"{image_name}_mat"
    mat = bpy.data.materials.new(material_name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes_to_delete = [node for node in nodes if node.type in ['BSDF_PRINCIPLED', 'OUTPUT_MATERIAL']]
    for node in nodes_to_delete:
        nodes.remove(node)

    tex_node = nodes.new('ShaderNodeTexImage')
    tex_node.image = bpy.data.images.get(image_name)
    tex_node.interpolation = 'Closest'
    bsdf_node = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_node.location = (200, 200)

    output_node = nodes.new('ShaderNodeOutputMaterial')
    output_node.location = (1000, 200)
    links.new(tex_node.outputs['Color'], bsdf_node.inputs['Base Color'])
    links.new(tex_node.outputs['Alpha'], bsdf_node.inputs['Alpha'])
    links.new(bsdf_node.outputs['BSDF'], output_node.inputs[0])
    return mat


def create_plane(image):
    material = create_material(image.name)
    size = 1.024
    coords = image.name.split(".")
    x, z = float(coords[1]) * size, float(coords[2]) * size
    bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, align='WORLD', location=(x - size / 2, z - size / 2, 0))

    plane = bpy.context.active_object
    plane.name = f"plane_{image.name}"
    plane.data.materials.append(material)


def scene():
    map = bpy.data.scenes.new("地图")
    bpy.context.window.scene = map
    world = bpy.data.worlds.new("地图")
    world.use_nodes = True
    bpy.context.space_data.shading.color_type = 'TEXTURE'
    bpy.context.space_data.overlay.show_stats = True
    world.node_tree.nodes["背景"].inputs[1].default_value = 5
    map.world = world


def create_images(images, pixel_data_list):
    for image, pixel_data in zip(images, pixel_data_list):
        image.pixels.foreach_set(pixel_data.ravel())
        create_plane(image)


def update_images(images, pixel_data_list):
    for image, pixel_data in zip(images, pixel_data_list):
        image.pixels.foreach_set(pixel_data.ravel())
        image.update()


def finalize_images(images, pixel_data_list):
    for image, pixel_data in zip(images, pixel_data_list):
        image.pixels.foreach_set(pixel_data.ravel())
        image.update()
