import bpy

from .operators.operator import ImportSchem,ImportSchemPlants,ImportSchemLeaves,ImportSchemLiquid,ImportSchemDeepStone,ImportSchemDirtGrass,ImportSchemOthers,ImportSchemSandGravel,ImportSchemSnow,Importjson,ImportWorld,SelectArea,GenerateWorld,VIEW3D_read_dir,MyFileList,PRINT_SELECTED_ITEM
from .operators.map import Map
from .ui import MainPanel,RigPanel,BlockPanel,WorldPanel,ResourcepacksPanel
from .operators.surface_optimization import MapOptimize
from .operators.sway_animation import SwayAnimationOperator
from .operators.BaiGave_Rig import SPAWN_MODEL,Settings
from .operators.Property import Property


bl_info={
    "name":"BaiGave's Tool",
    "author":"BaiGave",
    "version":(1, 0),
    "blender":(4, 0, 0),
    "location":"View3d > Tool",
    "warning":"如果有任何问题请联系白给~我的bilbil账号:BaiGave",
    "category":"BaiGave's Tool"
}



classes=[Settings,Property,SPAWN_MODEL,ImportSchem,ImportSchemPlants,ImportSchemLeaves,ImportSchemLiquid,ImportSchemSnow,ImportSchemDeepStone,
         ImportSchemDirtGrass,ImportSchemOthers,ImportSchemSandGravel,Importjson,ImportWorld,Map,MapOptimize,SwayAnimationOperator,SelectArea,
         GenerateWorld,MainPanel,RigPanel,BlockPanel,WorldPanel,ResourcepacksPanel,VIEW3D_read_dir,MyFileList,PRINT_SELECTED_ITEM]


def register():
    
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.BaiGave = bpy.props.PointerProperty(type = Settings)
    bpy.types.Scene.my_properties = bpy.props.PointerProperty(type=Property)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.BaiGave
    
if __name__ =="__main__":
    register()