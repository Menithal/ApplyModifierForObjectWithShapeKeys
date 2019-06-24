# ------------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Przemysław Bągard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ------------------------------------------------------------------------------

# Date: 24 Jun 2019
# Blender script
# Description: Apply modifier and remove from the stack for object with shape keys
# (Pushing 'Apply' button in 'Object modifiers' tab result in an error 'Modifier cannot be applied to a mesh with shape keys').

import math
import bpy
from bpy.props import *
bl_info = {
    "name":         "Apply modifier for object with shape keys",
    "author":       "Przemysław Bągard",
    "blender":      (2, 80, 0),
    "version":      (0, 2, 4),
    "location":     "Context menu",
    "description":  "Apply modifier and remove from the stack for object with shape keys (Pushing 'Apply' button in 'Object modifiers' tab result in an error 'Modifier cannot be applied to a mesh with shape keys').",
    "category":     "Object Tools > Multi Shape Keys"
}


# Algorithm:
# - Duplicate active object as many times as the number of shape keys
# - For each copy remove all shape keys except one
# - Removing last shape does not change geometry data of object
# - Apply modifier for each copy
# - Join objects as shapes and restore shape keys names
# - Delete all duplicated object except one
# - Delete old object
# - Restore name of object and object data


def applyModifierForObjectWithShapeKeys(context, modifierName):
    list_names = []
    list = []
    list_shapes = []
    if context.object.data.shape_keys:
        list_shapes = [o for o in context.object.data.shape_keys.key_blocks]

    if(list_shapes == []):
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifierName)
        return context.view_layer.objects.active

    list.append(context.view_layer.objects.active)
    for i in range(1, len(list_shapes)):
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False, "mode": 'TRANSLATION'}, TRANSFORM_OT_translate={
                                      "value": (0, 0, 0), "release_confirm": False})
        list.append(context.view_layer.objects.active)

    for i, o in enumerate(list):
        context.view_layer.objects.active = o
        list_names.append(o.data.shape_keys.key_blocks[i].name)
        for j in range(i+1, len(list))[::-1]:
            context.object.active_shape_key_index = j
            bpy.ops.object.shape_key_remove()
        for j in range(0, i):
            context.object.active_shape_key_index = 0
            bpy.ops.object.shape_key_remove()
        # last deleted shape doesn't change object shape
        context.object.active_shape_key_index = 0
        bpy.ops.object.shape_key_remove()
        # time to apply modifiers
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifierName)

    bpy.ops.object.select_all(action='DESELECT')
    context.view_layer.objects.active = list[0]
    list[0].select_set(True)
    bpy.ops.object.shape_key_add(from_mix=False)
    context.view_layer.objects.active.data.shape_keys.key_blocks[0].name = list_names[0]
    for i in range(1, len(list)):
        list[i].select_set(True)
        bpy.ops.object.join_shapes()
        list[i].select_set(False)
        context.view_layer.objects.active.data.shape_keys.key_blocks[i].name = list_names[i]

    bpy.ops.object.select_all(action='DESELECT')
    for o in list[1:]:
        o.select_set(True)

    bpy.ops.object.delete(use_global=False)
    context.view_layer.objects.active = list[0]
    context.view_layer.objects.active.select_set(True)
    return context.view_layer.objects.active


class ApplyModifierForObjectWithShapeKeysOperator(bpy.types.Operator):
    bl_idname = "object.apply_modifier_for_object_with_shape_keys"
    bl_label = "Apply modifier for object with shape keys"

    def item_list(self, context):
        return [(modifier.name, modifier.name, modifier.name) for modifier in bpy.context.active_object.modifiers]

    my_enum: EnumProperty(name="Modifier name",
                           items=item_list)

    def execute(self, context):
        ob = context.view_layer.objects.active
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = ob
        context.view_layer.objects.active.select_set(True)
        applyModifierForObjectWithShapeKeys(context, self.my_enum)

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class MESH_PT_ApplyModifierDialogPanel(bpy.types.Panel):
    bl_label = "Multi Shape Keys"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        self.layout.operator(
            "object.apply_modifier_for_object_with_shape_keys")


def menu_func(self, context):
    self.layout.operator("object.apply_modifier_for_object_with_shape_keys",
                         text="Apply modifier for object with shape keys")


register, unregister = bpy.utils.register_classes_factory(
    (ApplyModifierForObjectWithShapeKeysOperator, MESH_PT_ApplyModifierDialogPanel))

if __name__ == "__main__":
    register()
