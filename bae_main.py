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
from bpy.props import *
from .bae_globals import *


class BrresAnimationExporterProperties(bpy.types.PropertyGroup):

    node_type: EnumProperty(
        name="Node Type",
        default="CHR0",
        description="Type of node to export.",
        items=[('CHR0', "CHR0 Node", "Bone transformation"),
               ('CLR0', "CLR0 Node", "Colour animation"),
               ('SRT0', "SRT0 Node", "UV transformation")]
    )

    start_frame: IntProperty(
        name="Frame Start",
        description=("Only keyframes on this interval will be exported. "
                     "Keyframes will be 0-indexed from 'Frame Start'"),
        default=1
    )

    end_frame: IntProperty(
        name="Frame End",
        description=("Only keyframes on this interval will be exported. "
                     "Keyframes will be 0-indexed from 'Frame Start'"),
        default=60
    )
    node_name: StringProperty(
        name="Node Name",
        description="Name of node file",
        default="MyAnimationNode"
    )

    # CHR0 node settings
    i4 = ("i4", "Interpolated 4", "4 bytes per key frame, tangents stored as integers, select if unsure")
    i6 = ("i6", "Interpolated 6", "6 bytes per key frame, tangents stored as integers")
    i12 = ("i12", "Interpolated 12", "12 bytes per key frame, tangents stored as floats")
    l1 = ("l1", "Linear 1", "4 bytes per key frame per frame, tangents not stored")
    l4 = ("l4", "Linear 4", "4 bytes per key frame per frame, tangents not stored, values stored directly")

    advanced: BoolProperty(name="Show Advanced Options", default=False)

    scale: BoolProperty(name="Include Scale Data")
    scale_format: EnumProperty(
        name="Scale Data Format",
        default="i4",
        description="Choose",
        items=[i4, i6, i12]
    )

    scale_x: BoolProperty(name="Scale X")
    scale_y: BoolProperty(name="Scale Y")
    scale_z: BoolProperty(name="Scale Z")

    rotation: BoolProperty(name="Include Rotation Data")
    rotation_format: EnumProperty(
        name="Rotation Data Format",
        default="i4",
        description="Choose",
        items=[i4, i6, i12, l1, l4]
    )

    rotation_x: BoolProperty(name="Rotation X")
    rotation_y: BoolProperty(name="Rotation Y")
    rotation_z: BoolProperty(name="Rotation Z")

    convert_to_degrees: BoolProperty(
        name="Convert to degrees",
        default=True,
        description="Enable if rotation data is in radians"
    )

    translation: BoolProperty(name="Include Translation Data")

    scale_translation: FloatProperty(
        name="Translation Scale",
        description="Scale translation data by this value. Set to 100 if unsure",
        default=100
    )

    translation_format: EnumProperty(
        name="Translation Data Format",
        default="i4",
        description="Choose",
        items=[i4, i6, i12]
    )

    translation_x: BoolProperty(name="Translation X")
    translation_y: BoolProperty(name="Translation Y")
    translation_z: BoolProperty(name="Translation Z")

    xyz_to_xzy: BoolProperty(
        name="Convert XYZ to XZY",
        default=True,
        description="Keep True unless F-Curves animate a bone"
    )

    # CLR0 node settings
    red_source: EnumProperty(
        name="Red Channel",
        default='FCURVE',
        description="Source of data for this channel",
        items=[('FCURVE', "F-Curve", "Source data from a selected F-Curve"),
               ('CONSTANT', "Constant", "Source data from a constant value")]
    )

    red_constant: FloatProperty(
        name="Value",
        description="Constant value for the red channel",
        default=0.0,
        soft_min=0.0,
        soft_max=1.0,
        precision=3,
        subtype='FACTOR'
    )

    green_source: EnumProperty(
        name="Green Channel",
        default='FCURVE',
        description="Source of data for this channel",
        items=[('FCURVE', "F-Curve", "Source data from a selected F-Curve"),
               ('CONSTANT', "Constant", "Source data from a constant value")]
    )

    green_constant: FloatProperty(
        name="Value",
        description="Constant value for the green channel",
        default=0.0,
        soft_min=0.0,
        soft_max=1.0,
        precision=3,
        subtype='FACTOR'
    )

    blue_source: EnumProperty(
        name="Blue Channel",
        default='FCURVE',
        description="Source of data for this channel",
        items=[('FCURVE', "F-Curve", "Source data from a selected F-Curve"),
               ('CONSTANT', "Constant", "Source data from a constant value")]
    )

    blue_constant: FloatProperty(
        name="Value",
        description="Constant value for the blue channel",
        default=0.0,
        soft_min=0.0,
        soft_max=1.0,
        precision=3,
        subtype='FACTOR'
    )

    alpha_source: EnumProperty(
        name="Alpha Channel",
        default='FCURVE',
        description="Source of data for this channel",
        items=[('FCURVE', "F-Curve", "Source data from a selected F-Curve"),
               ('CONSTANT', "Constant", "Source data from a constant value")]
    )

    alpha_constant: FloatProperty(
        name="Value",
        description="Constant value for the alpha channel",
        default=0.0,
        soft_min=0.0,
        soft_max=1.0,
        precision=3,
        subtype='FACTOR'
    )

    mask: FloatVectorProperty(
        name="Mask",
        default=(0.0, 0.0, 0.0, 0.0),
        soft_min=0.0,
        soft_max=1.0,
        subtype='COLOR',
        size=4,
        description="Set the mask colour"
    )

    # SRT0 node settings
    srt_scale_x: BoolProperty(name="Scale X")
    srt_scale_y: BoolProperty(name="Scale Y")
    srt_rotation: BoolProperty(name="Rotation")
    srt_translation_x: BoolProperty(name="Translation X")
    srt_translation_y: BoolProperty(name="Translation Y")
