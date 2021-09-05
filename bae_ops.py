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
import struct
from .bae_helpers import *
from .bae_globals import *


class BRRESANIMATIONEXPORTER_OT_All(bpy.types.Operator):
    bl_idname = "brresanimationexporter.all"
    bl_description = "Converts selected F-Curves to a BRRES animation node"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.brres_animation_exporter_properties
        FCurves = bpy.context.selected_editable_fcurves
        i_fcurve = -1
        hints = []
        errors = []
        start = settings.start_frame
        end = settings.end_frame
        count = end - start + 1

        # Create CHR0 node
        if settings.node_type == 'CHR0':

            panel_options = (
                settings.scale,
                settings.scale_format,
                settings.scale_x,
                settings.scale_y,
                settings.scale_z,
                settings.rotation,
                settings.rotation_format,
                settings.rotation_x,
                settings.rotation_y,
                settings.rotation_z,
                settings.translation,
                settings.translation_format,
                settings.translation_x,
                settings.translation_y,
                settings.translation_z
            )

            srt = ("Scale", "Rotation", "Translation")
            axes = ("X", "Y", "Z")

            anim_data_list = [ChrAnimData(), ChrAnimData(), ChrAnimData()]

            # increment through srt
            for i in range(3):

                # if user enabled transformation
                if panel_options[i * 5]:

                    # increment through axes
                    for j in range(3):

                        # if user enabled axis
                        if panel_options[i * 5 + j + 2]:
                            i_fcurve += 1
                            format = panel_options[i * 5 + 1]

                            if not allFramesAreIntegers(FCurves[i_fcurve].keyframe_points):
                                errors.append(("Error: At least one keyframe "
                                               "point in the F-Curve used for %s %s is not an "
                                               "integer") % (srt[i], axes[j]))
                                break

                            keyframe_info = analyseKeyframeList(
                                FCurves[i_fcurve],
                                start,
                                end,
                                format in CHR0_LINEAR_FORMATS)

                            if PRINT_TO_CONSOLE:
                                print(("F-Curve at index %s:\n"
                                       " - Index of left keyframe point: %s\n"
                                       " - Index of right keyframe point: %s\n"
                                       " - Number of keyframe points on interval: "
                                       "%s\n") % (i_fcurve, *keyframe_info))

                            if not keyframe_info[2]:
                                errors.append((
                                    "Error: F-Curve used for %s %s is None or "
                                    "contains 0 keyframes within the specified "
                                    "interval.") % (srt[i], axes[j]))

                            # if F-Curve has 1 keyframe point
                            elif keyframe_info[2] == 1:
                                value = FCurves[i_fcurve].keyframe_points[keyframe_info[0]].co[1]
                                anim_data_list[i].updateData(j, [value])

                            else:
                                anim_data_list[i].updateFormat(format)

                                if format in CHR0_LINEAR_FORMATS:
                                    keyframes = []
                                    for i_keyframe in range(keyframe_info[0], keyframe_info[1]+1):
                                        keyframes.append(
                                            FCurves[i_fcurve].keyframe_points[i_keyframe].co[1])
                                    anim_data_list[i].updateData(j, keyframes)

                                # get list of tuples for i4, i6, i12 formats
                                else:
                                    keyframes = extractKeyframes(
                                        keyframe_info[0],
                                        keyframe_info[1],
                                        FCurves[i_fcurve].keyframe_points,
                                        start,
                                        end)

                                    anim_data_list[i].updateData(j, keyframes)

                    anim_data_list[i].updateFlags()

                    if PRINT_TO_CONSOLE:
                        print("\n%s data (before format):\n%s" % (srt[i], anim_data_list[i]))

                    anim_data_list[i].formatData(i)

                    if PRINT_TO_CONSOLE:
                        print("\n%s data (after format):\n%s" % (srt[i], anim_data_list[i]))

            if errors:

                self.report({'ERROR'}, '\n'.join(errors))

            else:
                node = combineSRT(*anim_data_list)

                # add bone name to node
                bone_name = settings.node_name  # get bone name
                bone_name = remove_non_ascii(bone_name)
                node += len(bone_name).to_bytes(4, 'big')
                node[:4] = len(node).to_bytes(4, 'big')
                node += bone_name.encode('ascii')
                node += bytearray((4 - len(node) % 4) % 4)

        # Create CLR0 node
        elif settings.node_type == 'CLR0':

            sources = (
                settings.red_source,
                settings.green_source,
                settings.blue_source,
                settings.alpha_source
            )
            constants = (
                settings.red_constant,
                settings.green_constant,
                settings.blue_constant,
                settings.alpha_constant
            )
            channels = ('red', 'green', 'blue', 'alpha')
            data_all = []

            for rgba in range(4):

                if sources[rgba] == 'FCURVE':
                    i_fcurve += 1

                    if not allFramesAreIntegers(FCurves[i_fcurve].keyframe_points):
                        errors.append(("Error: F-Curve selected for %s channel "
                                       "has at least one keyframe point that is not an integer"
                                       ) % channels[rgba])
                        break

                    keyframe_info = analyseKeyframeList(
                        FCurves[i_fcurve],
                        start,
                        end,
                        True)

                    if not keyframe_info[2]:
                        data_all.append(0)
                        errors.append(("Error: F-Curve selected for %s channel"
                                       " is None or empty.") % channels[rgba])

                    elif keyframe_info[2] == 1:
                        data_all.append([FCurves[i_fcurve].keyframe_points[0].co[1]])
                        hints.append(("Hint: F-Curve selected for %s channel is"
                                      " constant.") % channels[rgba])

                    else:
                        data = []
                        for i_keyframe in range(keyframe_info[0], keyframe_info[1] + 1):
                            data.append(scaleColourValue(
                                FCurves[i_fcurve].keyframe_points[i_keyframe].co[1]))

                        data_all.append(data)
                else:
                    data_all.append([scaleColourValue(constants[rgba])])

            if errors:
                self.report({'ERROR'}, '\n'.join(errors))

            else:
                node = bytearray(12 + count * 4)

                # mask, unknown, count
                node[:12] = struct.pack('>BBBBII',
                                        *(scaleColourValue(settings.mask[i]) for i in range(4)),
                                        0x08,
                                        count
                                        )

                # colours
                for rgba in range(4):
                    if len(data_all[rgba]) == 1:
                        constant = bytearray(data_all[rgba])
                        for row in range(12, 12 + count * 4, 4):
                            node[row + rgba] = constant[0]
                    else:
                        rgba_data = bytearray(data_all[rgba])
                        for i in range(count):
                            node[12 + 4 * i + rgba] = rgba_data[i]

        # Create SRT0 node
        else:
            names = [
                "Scale X",
                "Scale Y",
                "Rotation",
                "Translation X",
                "Translation Y"]

            sources = [
                settings.srt_scale_x,
                settings.srt_scale_y,
                settings.srt_rotation,
                settings.srt_translation_x,
                settings.srt_translation_y]

            data_all = []

            for i in range(5):
                if sources[i]:
                    i_fcurve += 1

                    if not allFramesAreIntegers(FCurves[i_fcurve].keyframe_points):
                        errors.append((
                            "Error: At least one keyframe point in the F-Curve used"
                            " for %s is not an integer") % names[i])
                        break

                    keyframe_info = analyseKeyframeList(
                        FCurves[i_fcurve], start, end, False)

                    if PRINT_TO_CONSOLE:
                        print(("F-Curve at index %s:\n"
                               " - Index of left keyframe point: %s\n"
                               " - Index of right keyframe point: %s\n"
                               " - Number of keyframe points on interval: "
                               "%s\n") % (i_fcurve, *keyframe_info))

                    if not keyframe_info[2]:
                        errors.append(("Error: F-Curve used for %s is None or "
                                       "contains 0 keyframes within the specified interval.")
                                      % names[i])

                    # if F-Curve has 1 keyframe point
                    elif keyframe_info[2] == 1:
                        data_all.append([FCurves[i_fcurve].keyframe_points[keyframe_info[0]].co[1]])

                    else:
                        data_all.append(extractKeyframes(
                            keyframe_info[0],
                            keyframe_info[1],
                            FCurves[i_fcurve].keyframe_points,
                            start,
                            end))

                else:
                    data_all.append([1 if i in range(2) else 0])

            node = get_srt_node(data_all)

        # Write node to file
        if not errors:
            filename = getUniqueFilename(getFilename(), include_tail=True)

            with open(filename, 'wb') as file:
                file.write(node)

            self.report({'INFO'},
                        "Successfully exported %s node to %s%s" % (
                settings.node_type,
                filename,
                ". Check console for hints" if hints else ""
            )
            )

        if hints:
            print("\nHints:\n%s" % ("\n".join(hints)))

        return {'FINISHED'}
