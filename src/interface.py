import bpy

class XCC_PT_ControllerPanel(bpy.types.Panel):
    """Panel for Xbox Camera Control polling"""
    bl_label = "Xbox Camera Control"
    bl_idname = "XCC_PT_ControllerPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "5Th-Dimension"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        cam = context.scene.camera

        row = layout.row()
        label = "Stop Polling" if wm.xcc_poll_enabled else "Start Polling"
        row.operator("xcc.toggle_polling", text=label, depress=wm.xcc_poll_enabled)
        layout.prop(context.window_manager, "xcc_move_speed", text="Camera Speed")
        if cam and cam.type == 'CAMERA':
            layout.prop(cam.data, "lens", text="Focal Length")
        else:
            layout.label(text="No active camera.")
        layout.prop(context.window_manager, "xcc_debug_buttons", text="Debug Controller Buttons")

classes = (XCC_PT_ControllerPanel,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
