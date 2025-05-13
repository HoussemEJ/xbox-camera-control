import bpy
from blf import position, size, color, draw
from . import props

# Global flag for tracking if the polling operator is running.
polling_running = False

def set_polling_running(val):
    global polling_running
    polling_running = val

def is_polling_running():
    return polling_running

def ensure_controller_polling(context):
    """
    Start the polling operator if it's not already running.
    """
    if not polling_running:
        bpy.ops.xcc.controller_poll('INVOKE_DEFAULT')

def ensure_camera(context):
    """
    Ensure that there is an active camera in the scene.
    If none is active but cameras exist in the scene, set the first (sorted by name) as the default.
    Returns the active camera or None if no camera is found.
    """
    scene = context.scene
    if scene.camera and scene.camera.type == 'CAMERA':
        return scene.camera
    cameras = [obj for obj in scene.objects if obj.type == 'CAMERA']
    if cameras:
        cameras.sort(key=lambda cam: cam.name)
        scene.camera = cameras[0]
        return scene.camera
    return None

def cycle_camera(context, direction):
    """
    Cycle the current scene's camera.
    
    Args:
        context: Blender context.
        direction (int): Use -1 to move to the previous camera and 1 to move to the next.
        
    Returns:
        The new active camera, or None if there are no cameras.
    """
    scene = context.scene
    cameras = [obj for obj in scene.objects if obj.type == 'CAMERA']
    if not cameras:
        return None
    cameras.sort(key=lambda cam: cam.name)
    try:
        current_index = cameras.index(scene.camera)
    except ValueError:
        current_index = 0
    new_index = (current_index + direction) % len(cameras)
    scene.camera = cameras[new_index]
    return scene.camera

def is_viewing_through_camera(context):
    for area in context.window.screen.areas:
        if area.type == 'VIEW_3D':
            region_3d = area.spaces.active.region_3d
            return region_3d.view_perspective == 'CAMERA'
    return False

def change_profile(context, direction):
    cam = ensure_camera(context)
    if not cam or cam.type != 'CAMERA':
        return "No camera", 0

    profile_items = props.PROFILE_ITEMS
    profile_ids = [item[0] for item in profile_items]

    current = cam.xcc_camera_profile if hasattr(cam, "xcc_camera_profile") else "PORTRAIT"

    try:
        index = profile_ids.index(current)
    except ValueError:
        index = 0

    new_index = (index + direction) % len(profile_ids)
    new_profile = profile_items[new_index]
    profile_id, profile_name, focal_length = new_profile

    cam.xcc_camera_profile = profile_id
    cam.data.lens = focal_length

    return profile_name, focal_length

def on_focal_length_slider_change(self, context):
    cam = ensure_camera(context)
    if cam and cam.type == 'CAMERA':
        cam.data.lens = context.window_manager.xcc_focal_length

_draw_handler = None
_debug_text = ""

def set_debug_text(text):
    global _debug_text
    _debug_text = text

def _draw_callback():
    if not _debug_text:
        return

    font_id = 0
    size(font_id, 14)

    x = 20
    y = 30
    line_height = 20

    lines = _debug_text.splitlines()
    for i, line in enumerate(reversed(lines)):
        position(font_id, x, y + i * line_height, 0)
        color(font_id, 1.0, 1.0, 1.0, 0.9)
        draw(font_id, line)



def enable_debug_draw():
    global _draw_handler
    if _draw_handler is None:
        _draw_handler = bpy.types.SpaceView3D.draw_handler_add(
            _draw_callback, (), 'WINDOW', 'POST_PIXEL'
        )

def disable_debug_draw():
    global _draw_handler
    if _draw_handler:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handler, 'WINDOW')
        _draw_handler = None

def apply_deadzone(value, threshold=5000):
    return value if abs(value) > threshold else 0