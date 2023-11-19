import bpy

#信息栏
def ShowMessageBox(message = "", title = "信息", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def button_callback(self, context, message):
    ShowMessageBox(message)