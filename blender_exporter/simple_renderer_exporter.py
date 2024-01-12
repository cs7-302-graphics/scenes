if "bpy" in locals():
    import importlib
    if "bl_utils" in locals():
        importlib.reload(bl_utils)
    if "importer" in locals():
        importlib.reload(importer)
    if "exporter" in locals():
        importlib.reload(exporter)

import bpy
import math
import os
import json
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper, axis_conversion
from mathutils import Vector

bl_info = {
    'name': 'Simple Renderer Exporter',
    'author': 'Ishaan Shah',
    'version': (0, 1),
    'blender': (3, 6, 0),
    'category': 'Import-Export',
    'location': 'File mene',
    'description': 'Scene exporter for "Simple Render"',
}

class ExportSimpleRenderer(bpy.types.Operator, ExportHelper):
    """Export scene for 'Simple Renderer"""
    bl_idname = "export_scene.simple_renderer"
    bl_label = "Simpler Renderer Export"

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        # Conversion matrix to shift the "Up" Vector. This can be useful when exporting single objects to an existing mitsuba scene.
        axis_mat = axis_conversion(
	            to_forward='X',
	            to_up='Z',
	        ).to_4x4()

        # Extract camera config
        camera = bpy.context.scene.camera
        if camera is None:
            self.report({'ERROR'}, "No camera found in scene, please add one and try again.")
            return {'CANCELLED'}

        mat = axis_conversion(to_forward='X', to_up='Z').to_4x4()

        cam_matrix = camera.matrix_world
        origin = mat @ cam_matrix @ Vector((0, 0, 0, 1))
        to = origin + mat @ cam_matrix @ Vector((0, 0, -1, 0))
        up = mat @ cam_matrix @ Vector((0, 1, 0, 0))

        render_settings = bpy.context.scene.render
        fov_x = 2 * math.atan((camera.data.sensor_width / 2.0) / camera.data.lens) * 180 / math.pi
        fov_y = (render_settings.resolution_y / render_settings.resolution_x) * fov_x

        config_name = os.path.basename(self.filepath)
        obj_name = config_name.replace(".json", ".obj")
        config = {
            "camera": {
                "fieldOfView": fov_y,
                "from": [origin.x, origin.y, origin.z],
                "to": [to.x, to.y, to.z],
                "up": [up.x, up.y, up.z]
            },
            "output": {
                "resolution": [bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y]
            },
            "surface": [
                obj_name
            ]
        }

        with open(self.filepath, "w") as f:
            json.dump(config, f, indent=4)

        bpy.ops.wm.obj_export(filepath=self.filepath.replace(config_name, obj_name), up_axis='Z', forward_axis='X', export_triangulated_mesh=True)

        self.report({'INFO'}, "Scene exported successfully!")

        return {'FINISHED'}

def menu_export_func(self, context):
    self.layout.operator(ExportSimpleRenderer.bl_idname, text="Simpler Renderer (.json)")

classes = (
   ExportSimpleRenderer,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_export_func)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_export_func)
    
# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()