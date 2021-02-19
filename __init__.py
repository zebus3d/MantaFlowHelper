import bpy
from datetime import datetime
import re


bl_info = {
    "name": "MantaFlowHelper",
    "author": "Jorge Hernandez Melendez",
    "version": (0, 1),
    "blender": (2, 90, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "category": "Physics",
    }

from bpy.types import (Panel, Operator)


class MFH_PT_ui(Panel):
    bl_label = "Mantaflow Helper"
    bl_category = "MFH"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.use_property_split = True
        layout.use_property_decorate = False
        flow = layout.grid_flow(align=True)
        col = flow.column()
        col.operator("mfh.prepare", text="Prepare all manta objects")
        col.operator("mfh.rcache", text="Reset Cache")


class MHH_prepare(Operator):
    bl_idname = "mfh.prepare"
    bl_label = "Prepare all manta objects"
    bl_description = "Prepare all objects for work correctly with MantaFlow"

    def execute(self, context):
        current_selection = bpy.context.selected_objects
        current_active = bpy.context.view_layer.objects.active

        current_mode = bpy.context.mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')

        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                if any(mod for mod in ob.modifiers if mod.type == 'FLUID'):
                    bpy.context.view_layer.objects.active = ob
                    ob.select_set(True)
                    noreturn = bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                    noreturn = bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        if len(current_selection) > 0:
            for ob in current_selection:
                ob.select_set(True)
        else:
            bpy.ops.object.select_all(action='DESELECT')

        bpy.context.view_layer.objects.active = current_active
        bpy.ops.object.mode_set(mode=current_mode)

        return {'FINISHED'}

class MHH_reset_cache(Operator):
    bl_idname = "mfh.rcache"
    bl_label = "Reset Cache"
    bl_description = "Reset Cache"

    def execute(self, context):
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                for mod in ob.modifiers:
                    if mod.type == 'FLUID':
                        if mod.fluid_type == "DOMAIN":
                            bpy.ops.screen.frame_jump(0)
                            now = datetime.now()
                            time = '_MFH_' + str(now.hour) + '_' + str(now.minute) + '_' + str(now.second) + '_' +  str(now.microsecond)
                            print(mod.domain_settings.cache_directory + time)
                            if 'MFH' in mod.domain_settings.cache_directory:
                                m = re.match(r'^(.*)(_MFH_.*)$', mod.domain_settings.cache_directory)
                                if m:
                                    mod.domain_settings.cache_directory = mod.domain_settings.cache_directory.replace(m.group(2), time)
                            else:
                                mod.domain_settings.cache_directory = mod.domain_settings.cache_directory + time

        return {'FINISHED'}

all_classes = [
    MFH_PT_ui,
    MHH_prepare,
    MHH_reset_cache,
]

def register():
    from bpy.utils import register_class

    if len(all_classes) > 1:
        for cls in all_classes:
            register_class(cls)
    else:
        register_class(all_classes[0])


def unregister():
    from bpy.utils import unregister_class

    if len(all_classes) > 1:
        for cls in reversed(all_classes):
            unregister_class(cls)
    else:
        unregister_class(all_classes[0])


if __name__ == "__main__":
    register()