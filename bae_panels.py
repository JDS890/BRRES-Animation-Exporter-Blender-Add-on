#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****

# <pep8 compliant>

import bpy
from .bae_helpers import (
    getUniqueFilename,
    getFilename,
    scaleColourValue
)


class BRRESANIMATIONEXPORTER_PT_All(bpy.types.Panel):

    bl_idname = "BRRESANIMATIONEXPORTER_PT_All"
    bl_label = "Export selected F-Curves as CHR0, CLR0 or STR0 node"
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'
    bl_category = "BRRES Animation Exporter"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.brres_animation_exporter_properties
        enable_button = True
        FCurves = bpy.context.selected_editable_fcurves
        given_fcurves = len(FCurves) if FCurves else 0

        layout.prop(settings, "node_type")

        # Draw meta data settings
        box_meta = layout.box()
        box_meta.label(text="Timeline Interval to Export From")
        box_meta.prop(settings, "start_frame")
        box_meta.prop(settings, "end_frame")
        frame_diff = settings.end_frame - settings.start_frame
        if frame_diff < 0:
            box_meta.label(text="Invalid range", icon='ERROR')
            enable_button = False
        else:
            box_meta.label(text="Number of Frames: %s" % (frame_diff + 1))

        if bpy.data.is_saved:
            box_meta.prop(settings, "node_name")
            box_meta.label(text="Path: %s" % getUniqueFilename(getFilename(),
                                                               include_tail=True))
        else:
            box_meta.label(text="Save Blend Before Export", icon='ERROR')
            enable_button = False

        if bpy.context.scene.render.fps != 60:
            box_meta.label(text=("Hint: Frame Rate set to %s fps. Change to 60"
                                 " fps to match BRRES animation speed.")
                           % bpy.context.scene.render.fps, icon='PLAY')

        # Draw CHR0 node settings
        if settings.node_type == 'CHR0':
            box_chr0 = layout.box()

            box_advanced = box_chr0.box()
            box_advanced.prop(settings, "advanced")

            box_scale = box_chr0.box()
            box_scale.prop(settings, "scale")
            if settings.scale:
                if settings.advanced:
                    box_scale.prop(settings, "scale_format")
                box_scale.prop(settings, "scale_x")
                box_scale.prop(settings, "scale_y")
                box_scale.prop(settings, "scale_z")

            box_rotation = box_chr0.box()
            box_rotation.prop(settings, "rotation")
            if settings.rotation:
                if settings.advanced:
                    box_rotation.prop(settings, "rotation_format")
                    box_rotation.prop(settings, "convert_to_degrees")
                box_rotation.prop(settings, "rotation_x")
                box_rotation.prop(settings, "rotation_y")
                box_rotation.prop(settings, "rotation_z")

            box_translation = box_chr0.box()
            box_translation.prop(settings, "translation")
            if settings.translation:
                if settings.advanced:
                    box_translation.prop(settings, "translation_format")
                    box_translation.prop(settings, "scale_translation")
                box_translation.prop(settings, "translation_x")
                box_translation.prop(settings, "translation_y")
                box_translation.prop(settings, "translation_z")

            if settings.advanced:
                box_xyz_to_xzy = box_chr0.box()
                box_xyz_to_xzy.prop(settings, "xyz_to_xzy")

            included_data_list = [
                settings.scale,
                settings.scale_x,
                settings.scale_y,
                settings.scale_z,
                settings.rotation,
                settings.rotation_x,
                settings.rotation_y,
                settings.rotation_z,
                settings.translation,
                settings.translation_x,
                settings.translation_y,
                settings.translation_z
            ]

            required_fcurves = 0
            for i in range(3):
                if included_data_list[i * 4]:
                    for j in range(1, 4):
                        if included_data_list[i * 4 + j]:
                            required_fcurves += 1

            if required_fcurves:
                frame_diff = required_fcurves - given_fcurves
                if frame_diff > 0:
                    box_chr0.label(
                        text="Hint: Select, unhide, or unlock %s more F-Curve%s"
                        % (frame_diff, ('s' if frame_diff > 1 else '')),
                        icon='ERROR')
                    enable_button = False
                elif frame_diff < 0:
                    box_chr0.label(text="Hint: Deselect %s F-Curve%s" %
                                   (-frame_diff, ('s' if -frame_diff > 1 else '')), icon='ERROR')
                    enable_button = False
            else:
                box_chr0.label(text="Hint: Must make use of at least 1 F-Curve",
                               icon='ERROR')
                enable_button = False

        # Draw CLR0 node settings
        elif settings.node_type == 'CLR0':
            box_clr0 = layout.box()
            box_clr0.label(text="Select Sources")

            box_clr0.prop(settings, "red_source")
            if settings.red_source == 'CONSTANT':
                red_constant_split = box_clr0.split(factor=0.24)
                red_constant_split.label(text='0x{:02X}'.format(
                    scaleColourValue(settings.red_constant)))
                red_constant_split.prop(settings, "red_constant")

            box_clr0.prop(settings, "green_source")
            if settings.green_source == 'CONSTANT':
                green_constant_split = box_clr0.split(factor=0.24)
                green_constant_split.label(text='0x{:02X}'.format(
                    scaleColourValue(settings.green_constant)))
                green_constant_split.prop(settings, "green_constant")

            box_clr0.prop(settings, "blue_source")
            if settings.blue_source == 'CONSTANT':
                blue_constant_split = box_clr0.split(factor=0.24)
                blue_constant_split.label(text='0x{:02X}'.format(
                    scaleColourValue(settings.blue_constant)))
                blue_constant_split.prop(settings, "blue_constant")

            box_clr0.prop(settings, "alpha_source")
            if settings.alpha_source == 'CONSTANT':
                alpha_constant_split = box_clr0.split(factor=0.24)
                alpha_constant_split.label(text='0x{:02X}'.format(
                    scaleColourValue(settings.alpha_constant)))
                alpha_constant_split.prop(settings, "alpha_constant")

            box_clr0.prop(settings, "mask")

            sources = [
                settings.red_source,
                settings.green_source,
                settings.blue_source,
                settings.alpha_source
            ]

            required_fcurves = sources.count('FCURVE')

            if required_fcurves:
                missing_fcurves = required_fcurves - given_fcurves
                if missing_fcurves > 0:
                    box_clr0.label(
                        text="Hint: Select, unhide, or unlock %s more F-Curve%s"
                        % (missing_fcurves, ("s" if missing_fcurves > 1 else "")),
                        icon='ERROR')
                    enable_button = False
                elif missing_fcurves < 0:
                    box_clr0.label(text="Hint: Deselect %s F-Curve%s" %
                                   (-missing_fcurves, ("s" if -missing_fcurves > 1 else "")),
                                   icon='ERROR')
                    enable_button = False
            else:
                box_clr0.label(text="Hint: All Channels Constant", icon='ERROR')
                enable_button = False

            if bpy.context.scene.view_settings.view_transform != 'Standard':
                box_clr0.label(text=("Hint: Change 'View Transform' to 'Standard'"
                                     " to display colours more accurately."), icon='COLOR')

        # Draw SRT0 node settings
        else:
            box_srt0 = layout.box()
            box_srt0.prop(settings, "srt_scale_x")
            box_srt0.prop(settings, "srt_scale_y")
            box_srt0.prop(settings, "srt_rotation")
            box_srt0.prop(settings, "srt_translation_x")
            box_srt0.prop(settings, "srt_translation_y")

            sources = [
                settings.srt_scale_x,
                settings.srt_scale_y,
                settings.srt_rotation,
                settings.srt_translation_x,
                settings.srt_translation_y]

            required_fcurves = 0
            for source in sources:
                if source:
                    required_fcurves += 1

            if required_fcurves:
                frame_diff = required_fcurves - given_fcurves
                if frame_diff > 0:
                    box_srt0.label(
                        text="Hint: Select, unhide, or unlock %s more F-Curve%s"
                        % (frame_diff, ("s" if frame_diff > 1 else "")),
                        icon='ERROR')
                    enable_button = False
                elif frame_diff < 0:
                    box_srt0.label(text="Hint: Deselect %s F-Curve%s" %
                                   (-frame_diff, ("s" if -frame_diff > 1 else "")),
                                   icon='ERROR')
                    enable_button = False
            else:
                box_srt0.label(text="Hint: Must make use of at least 1 F-Curve",
                               icon='ERROR')
                enable_button = False

        # Draw export button (calls BRRESANIMATIONEXPORTER_OT_All operator)
        export_btn_row = layout.row()
        export_btn_row.operator("brresanimationexporter.all",
                                text="Export as %s node" % settings.node_type)
        export_btn_row.enabled = enable_button
