import bpy
import subprocess
import sys

def install_dependencies():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "amulet-core"])
    except subprocess.CalledProcessError as e:
        print("安装Amulet库失败:", e)

# 执行自动安装函数
install_dependencies()
from .operators.operator import ImportSchem,Importjson,ImportWorld,SelectArea,GenerateWorld,MainPanel,RigPanel,BlockPanel,WorldPanel
from .operators.map import Map
from .operators.BaiGave_Rig import Settings,SPAWN_MODEL    


bl_info={
    "name":"BaiGave's Tool",
    "author":"BaiGave",
    "version":(1, 0),
    "blender":(3, 6, 0),
    "location":"View3d > Tool",
    "warning":"如果有任何问题请联系白给~我的bilbil账号:BaiGave",
    "category":"BaiGave's Tool"
}



classes=[Settings,SPAWN_MODEL,ImportSchem,Importjson,ImportWorld,Map,SelectArea,GenerateWorld,MainPanel,RigPanel,BlockPanel,WorldPanel]


def register():
    
    for cls in classes:
        bpy.utils.register_class(cls)
        
        bpy.types.Scene.BaiGave = bpy.props.PointerProperty(type = Settings)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
        #del bpy.types.Scene.BaiGave
    
if __name__ =="__main__":
    register()