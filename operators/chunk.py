from .section import section

def chunk(chunk, level):
    vertices = []
    faces = []
    direction = []
    texture_list = []
    uv_list = []
    uv_rotation_list = []
    vertices_dict = {}
    
    for s in chunk.blocks.sections:
        section(chunk.blocks.get_section(s), level, s, vertices, faces, texture_list, uv_list, direction, uv_rotation_list, vertices_dict)
    
    return vertices, faces, texture_list, uv_list, direction, uv_rotation_list
