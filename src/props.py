import bpy
from . import utils

PROFILE_ITEMS = [
    ("FISHEYE", "Fisheye Madness", 10),
    ("ARCHITECT", "Architect's Dream", 18),
    ("STREET", "Street Classic", 24),
    ("CINEMA", "Everyday Cinema", 35),
    ("PORTRAIT", "Portrait Standard", 50),
    ("CLOSEUP", "Soft Close-Up", 85),
    ("TELESCOPE", "Telescope Feel", 135),
]

def on_xcc_poll_toggle(self, context):
    """
    Called when the xcc_poll_enabled property is toggled.
    When set to True, starts the polling operator if it isn’t running.
    """
    if context.window_manager.xcc_poll_enabled:
        if not utils.is_polling_running():
            bpy.ops.xcc.controller_poll('INVOKE_DEFAULT')

def register():
    bpy.types.WindowManager.xcc_poll_enabled = bpy.props.BoolProperty(
         name="Enable Controller Polling",
         description="Start Xbox controller polling",
         default=False,
         update=on_xcc_poll_toggle
    )
    bpy.types.WindowManager.xcc_debug_buttons = bpy.props.BoolProperty(
         name="Debug Controller Buttons",
         description="Display detailed controller state info",
         default=False
    )
    bpy.types.Object.xcc_camera_profile = bpy.props.StringProperty(
        name="Camera Profile",
        description="Active profile ID for this camera",
        default="PORTRAIT"
    )
    bpy.types.WindowManager.xcc_move_speed = bpy.props.IntProperty(
        name="Camera Speed",
        description="Adjust the speed of camera movement (units per tick)",
        default=10,
        min=1,
        max=100
    )
    bpy.types.WindowManager.xcc_focal_length = bpy.props.IntProperty(
        name="Focal Length",
        description="Manually adjust focal length of the active camera",
        default=50,
        min=1,
        max=5000,
        update=utils.on_focal_length_slider_change
    )

def unregister():
    del bpy.types.WindowManager.xcc_poll_enabled
    del bpy.types.WindowManager.xcc_debug_buttons
    del bpy.types.Object.xcc_camera_profile
    del bpy.types.WindowManager.xcc_move_speed
    del bpy.types.WindowManager.xcc_focal_length

