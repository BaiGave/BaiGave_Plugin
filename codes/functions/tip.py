import bpy

def ShowMessageBox(message="", title="信息", icon='INFO', link_text=None, link_operator=None):
    def draw(self, context):
        layout = self.layout
        layout.label(text=message)

        if link_text and link_operator:
            row = layout.row()
            row.scale_y = 2.0
            row.operator(link_operator.bl_idname, text=link_text)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def button_callback(self, context, message, title="信息", link_text=None, link_operator=None):
    ShowMessageBox(message, title, link_text=link_text, link_operator=link_operator)

