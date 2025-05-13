import bpy
from . import xbox_controller
from . import utils
import mathutils

class XCC_OT_ControllerPoll(bpy.types.Operator):
    """Poll Xbox Controller Input, trigger camera/render operations,
    and display detailed debug info if enabled."""
    bl_idname = "xcc.controller_poll"
    bl_label = "Xbox Controller Polling"

    _timer = None
    last_state = None
    reported_no_controller = False

    def modal(self, context, event):
        if event.type == 'TIMER':
            if not context.window_manager.xcc_poll_enabled:
                self.cancel(context)
                self.report({'INFO'}, "Xbox Controller Polling Stopped")
                return {'CANCELLED'}

            state = xbox_controller.read_controller_values()
            if state is None:
                if not self.reported_no_controller:
                    self.report({'WARNING'}, "No controller detected")
                    self.reported_no_controller = True
                self.last_state = None
            else:
                self.reported_no_controller = False

                current_buttons = set(state['buttons'])
                previous_buttons = set(self.last_state['buttons']) if self.last_state else set()
                new_presses = current_buttons - previous_buttons

                # --- A Button: view_camera (like numpad 0) ---
                if "A" in new_presses:
                    cam = utils.ensure_camera(context)
                    if cam:
                        bpy.ops.view3d.view_camera('INVOKE_DEFAULT')
                    else:
                        self.report({'WARNING'}, "No camera available for 'View Camera' (A button)")

                # --- X Button: camera_to_view (like Ctrl+Alt+Numpad 0) ---
                if "X" in new_presses:
                 cam = utils.ensure_camera(context)
                 if cam and not utils.is_viewing_through_camera(context):
                     bpy.ops.view3d.camera_to_view('INVOKE_DEFAULT')
                 elif not cam:
                     self.report({'WARNING'}, "No camera available for 'Camera to View' (X button)")

                # --- B Button: camera_to_view_selected ---
                if "B" in new_presses:
                    cam = utils.ensure_camera(context)
                    if cam:
                        bpy.ops.view3d.camera_to_view_selected('INVOKE_DEFAULT')
                    else:
                        self.report({'WARNING'}, "No camera available for 'Camera to View Selected' (B button)")

                # --- Y Button: Render (like F12) ---
                if "Y" in new_presses:
                    cam = utils.ensure_camera(context)
                    if cam:
                        bpy.ops.render.render('INVOKE_DEFAULT')
                    else:
                        self.report({'WARNING'}, "No camera available for rendering (Y button)")

                # --- DPAD_LEFT: Cycle to previous camera ---
                if "DPAD_LEFT" in new_presses:
                    new_cam = utils.cycle_camera(context, direction=-1)
                    if new_cam:
                        self.report({'INFO'}, f"Switched to camera: {new_cam.name}")
                    else:
                        self.report({'WARNING'}, "No cameras available to cycle through (DPAD_LEFT)")
                
                # --- DPAD_RIGHT: Cycle to next camera ---
                if "DPAD_RIGHT" in new_presses:
                    new_cam = utils.cycle_camera(context, direction=1)
                    if new_cam:
                        self.report({'INFO'}, f"Switched to camera: {new_cam.name}")
                    else:
                        self.report({'WARNING'}, "No cameras available to cycle through (DPAD_RIGHT)")
                
                # --- DPAD_UP: Move to previous profile ---
                if "DPAD_UP" in new_presses:
                    name, mm = utils.change_profile(context, direction=-1)
                    self.report({'INFO'}, f"Switched to profile: {name} ({mm} mm)")

                # --- DPAD_DOWN: Move to next profile ---
                if "DPAD_DOWN" in new_presses:
                    name, mm = utils.change_profile(context, direction=1)
                    self.report({'INFO'}, f"Switched to profile: {name} ({mm} mm)")

                cam = utils.ensure_camera(context)
                if cam:
                    move_speed = context.window_manager.xcc_move_speed * 0.1

                    lt = state['left_trigger']
                    rt = state['right_trigger']

                    if lt > 0:
                        cam.location.z -= move_speed * (lt / 255.0) * 0.5

                    if rt > 0:
                        cam.location.z += move_speed * (rt / 255.0) * 0.5

                    if "RB" in state["buttons"]:
                        cam.rotation_euler.rotate_axis("Y", -move_speed * 0.01)

                    if "LB" in state["buttons"]:
                        cam.rotation_euler.rotate_axis("Y", move_speed * 0.01)

                    lx = utils.apply_deadzone(state["thumbRX"])
                    ly = utils.apply_deadzone(state["thumbRY"])

                    # Rotate around local Z (left/right)
                    if lx != 0:
                        cam.rotation_euler.rotate_axis("Z", -lx / 32768 * move_speed * 0.005)

                    # Rotate around local X (up/down)
                    if ly != 0:
                        cam.rotation_euler.rotate_axis("X", -ly / 32768 * move_speed * 0.005)

                    rx = utils.apply_deadzone(state["thumbLX"])
                    ry = utils.apply_deadzone(state["thumbLY"])
                    
                    local_offset = mathutils.Vector((
                        rx / 32768 * move_speed * 0.2,
                        0,
                        -ry / 32768 * move_speed * 0.2
                    ))
                    # Transform the local offset to global space using the camera's rotation
                    global_offset = cam.matrix_world.to_quaternion() @ local_offset
                    cam.location += global_offset

                if context.window_manager.xcc_debug_buttons:
                    debug_msg = (
                        f"Buttons: {state['buttons']}\n"
                        f"LT: {state['left_trigger']}, RT: {state['right_trigger']}\n"
                        f"ThumbLX: {state['thumbLX']}, ThumbLY: {state['thumbLY']}\n"
                        f"ThumbRX: {state['thumbRX']}, ThumbRY: {state['thumbRY']}"
                    )
                    utils.set_debug_text(debug_msg)
                else:
                    utils.set_debug_text("")
                
                for area in context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()

                self.last_state = state.copy()
        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(time_step=0.02, window=context.window)
        wm.modal_handler_add(self)
        self.last_state = None
        self.reported_no_controller = False
        utils.set_polling_running(True)
        utils.enable_debug_draw()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        if self._timer is not None:
            wm.event_timer_remove(self._timer)
        utils.set_polling_running(False)
        utils.disable_debug_draw()

class XCC_OT_TogglePolling(bpy.types.Operator):
    """Toggle Xbox Controller Polling"""
    bl_idname = "xcc.toggle_polling"
    bl_label = "Toggle Polling"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        wm = context.window_manager
        wm.xcc_poll_enabled = not wm.xcc_poll_enabled
        return {'FINISHED'}

classes = (XCC_OT_ControllerPoll, XCC_OT_TogglePolling)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
