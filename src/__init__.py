bl_info = {
    "name": "Xbox Camera Control",
    "author": "Houssemeddine Jebali",
    "version": (1, 0, 0),
    "blender": (4, 4, 0),
    "location": "3D View > N-Panel",
    "description": "Use your Xbox controller to move scene camera, adjust focal length, add new cameras and switch between them",
    "category": "3D View",
}

from . import operators, interface, props

def register():
    props.register()
    operators.register()
    interface.register()

def unregister():
    interface.unregister()
    operators.unregister()
    props.unregister()

if __name__ == "__main__":
    register()
