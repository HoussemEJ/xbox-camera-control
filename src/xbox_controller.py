import ctypes

# This module is intended for Windows; non-Windows platforms will have no controller support.

try:
    xinput = ctypes.windll.xinput1_4
except Exception:
    try:
        xinput = ctypes.windll.xinput1_3.dll
    except Exception:
        xinput = None

ERROR_SUCCESS = 0

BUTTONS = {
    0x1000: "A",
    0x2000: "B",
    0x4000: "X",
    0x8000: "Y",
    0x0001: "DPAD_UP",
    0x0002: "DPAD_DOWN",
    0x0004: "DPAD_LEFT",
    0x0008: "DPAD_RIGHT",
    0x0010: "MENU",
    0x0020: "VIEW",
    0x0100: "LB",
    0x0200: "RB",
}

class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ("wButtons", ctypes.c_ushort),
        ("bLeftTrigger", ctypes.c_ubyte),
        ("bRightTrigger", ctypes.c_ubyte),
        ("sThumbLX", ctypes.c_short),
        ("sThumbLY", ctypes.c_short),
        ("sThumbRX", ctypes.c_short),
        ("sThumbRY", ctypes.c_short),
    ]

class XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ("dwPacketNumber", ctypes.c_ulong),
        ("Gamepad", XINPUT_GAMEPAD),
    ]

def get_controller_state(controller_id=0):
    """
    Retrieve the current state of the Xbox controller.
    """
    if not xinput:
        return None
    state = XINPUT_STATE()
    result = xinput.XInputGetState(controller_id, ctypes.byref(state))
    if result == ERROR_SUCCESS:
        return state.Gamepad
    return None

def decode_buttons(wButtons):
    """
    Convert the raw wButtons bitmask into a list of pressed button names.
    """
    return [name for mask, name in BUTTONS.items() if wButtons & mask]

def read_controller_values(controller_id=0):
    """
    Read all available controller data including digital buttons, triggers, 
    and analog thumbstick axes.

    Returns:
        dict: A dictionary containing all controller values or None if no controller is detected.
    """
    gamepad = get_controller_state(controller_id)
    if not gamepad:
        return None
    return {
        "buttons": decode_buttons(gamepad.wButtons),
        "wButtons": gamepad.wButtons,
        "left_trigger": gamepad.bLeftTrigger,
        "right_trigger": gamepad.bRightTrigger,
        "thumbLX": gamepad.sThumbLX,
        "thumbLY": gamepad.sThumbLY,
        "thumbRX": gamepad.sThumbRX,
        "thumbRY": gamepad.sThumbRY,
    }
