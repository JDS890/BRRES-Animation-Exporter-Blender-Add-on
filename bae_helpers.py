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
import math
import os
from .bae_globals import *


class ChrAnimData():

    def __init__(self):
        self.__format = 'none'
        self.__has = False
        self.__data_x = []
        self.__fixed_x = True
        self.__data_y = []
        self.__fixed_y = True
        self.__data_z = []
        self.__fixed_z = True
        self.__isotropic = True

    def __str__(self):
        data_list = [
            self.__data_x,
            self.__fixed_x,
            self.__data_y,
            self.__fixed_y,
            self.__data_z,
            self.__fixed_z
        ]

        def __format_data(axis):

            if data_list[axis * 2]:
                if self.__format in CHR0_LINEAR_FORMATS or data_list[axis*2 + 1]:
                    return ["%07.3f" % frame for frame in data_list[axis * 2]]
                else:
                    return ["(%04s, %07.3f, %07.3f)"
                            % tuple for tuple in data_list[axis * 2]]
            else:
                return []

        lines = [
            "Format: %s" % self.__format,
            "Has data: %s" % self.__has,
            "Is isotropic: %s\n" % self.__isotropic,

            "X axis has: %s" % bool(self.__data_x),
            "X axis constant: %s" % self.__fixed_x,
            *__format_data(0), "\n",

            "Y axis has: %s" % bool(self.__data_y),
            "Y axis constant: %s" % self.__fixed_y,
            *__format_data(1), "\n",

            "Z axis has: %s" % bool(self.__data_z),
            "Z axis constant: %s" % self.__fixed_z,
            *__format_data(2)
        ]

        return '\n'.join(lines)

    def updateData(self, axis: int, data: list):
        """
        'axis' should take values 0, 1 or 2 corresponding
        to the X, Y or Z axis, respectively.
        """
        if axis not in range(3):
            raise ValueError("'axis' must be in range(0, 3)")

        elif not type(data) == list:
            raise ValueError("'data' must be a list")

        else:
            if axis == 2:
                self.__data_z = data

            elif axis == 1:
                self.__data_y = data

            else:
                self.__data_x = data

    def updateFormat(self, format):
        self.__format = format

    def updateFlags(self):
        self.__isotropic = self.__data_x == self.__data_y and self.__data_y == self.__data_z

        self.__fixed_x = not self.__data_x or len(self.__data_x) == 1
        self.__fixed_y = not self.__data_y or len(self.__data_y) == 1
        self.__fixed_z = not self.__data_z or len(self.__data_z) == 1

        self.__has = bool(self.__data_x) or bool(self.__data_y) or bool(self.__data_z)

    def formatData(self, srt):

        settings = bpy.context.scene.brres_animation_exporter_properties
        xyz_to_xzy = settings.xyz_to_xzy
        scale = settings.scale_translation
        convert_to_degrees = settings.convert_to_degrees
        deg_per_rad = 180 / math.pi if convert_to_degrees else 1

        if xyz_to_xzy:

            data_y_temp = self.__data_y
            fixed_y_temp = self.__fixed_y

            self.__data_y = self.__data_z
            self.__fixed_y = self.__fixed_z

            self.__data_z = data_y_temp
            self.__fixed_z = fixed_y_temp

        data = [self.__data_x, self.__data_y, self.__data_z]

        for i in range(3):
            if data[i]:
                new_list = []
                sign = -1 if i == 2 and xyz_to_xzy else 1

                # scale
                if srt == 0:

                    if len(data[i]) == 1:

                        new_list.append(data[i][0])

                    else:

                        for tuple in data[i]:
                            new_list.append((

                                # frame
                                int(tuple[0]),

                                # value
                                tuple[1],

                                # tangent
                                tuple[2]
                            ))

                # rotation
                elif srt == 1:

                    if self.__format in CHR0_LINEAR_FORMATS or len(data[i]) == 1:

                        for value in data[i]:

                            new_list.append(value * deg_per_rad * sign)

                    else:

                        for tuple in data[i]:
                            new_list.append((

                                # frame
                                int(tuple[0]),

                                # value
                                tuple[1] * deg_per_rad * sign,

                                # tangent
                                tuple[2] * deg_per_rad * sign
                            ))

                # translation
                else:

                    if len(data[i]) == 1:

                        new_list.append(data[i][0] * scale * sign)

                    else:

                        for tuple in data[i]:
                            new_list.append((

                                # frame
                                int(tuple[0]),

                                # value
                                tuple[1] * scale * sign,

                                # tangent
                                tuple[2] * scale * sign
                            ))
                if i == 0:
                    self.__data_x = new_list
                elif i == 1:
                    self.__data_y = new_list
                else:
                    self.__data_z = new_list

        self.__update_format(srt)

    def __update_format(self, srt):

        if self.__has:

            const_x = get_fixed(self.__data_x, srt)
            const_y = get_fixed(self.__data_y, srt)
            const_z = get_fixed(self.__data_z, srt)

            if const_x and len(self.__data_x) != 1:
                self.__data_x = const_x
                self.__fixed_x = True

            if const_y and len(self.__data_y) != 1:
                self.__data_y = const_y
                self.__fixed_y = True

            if const_z and len(self.__data_z) != 1:
                self.__data_z = const_z
                self.__fixed_z = True

            if self.__fixed_x and self.__fixed_y and self.__fixed_z:

                self.__format = 'none'

                if (self.__data_x[0] == self.__data_y[0] and
                        self.__data_y[0] == self.__data_z[0]):

                    self.__isotropic = True

                    if self.__data_x[0] == (1 if srt == 1 else 0):

                        self.__has = False

            else:
                if self.__format == 'i4' or self.__format == 'i6':

                    largest_frame_count = 0
                    largest_frame_index = 0
                    largest_tangent = 0
                    smallest_tangent = 0

                    data_info = [self.__data_x, self.__fixed_x,
                                 self.__data_y, self.__fixed_y,
                                 self.__data_z, self.__fixed_z]

                    for i in range(3):
                        if not data_info[2*i + 1]:
                            if largest_frame_count < len(data_info[2 * i]):
                                largest_frame_count = len(data_info[2 * i])
                            if largest_frame_index < data_info[2 * i][-1][0]:
                                largest_frame_index = data_info[2 * i][-1][0]
                            min, max = getDataMaxima(data_info[2 * i], 2)
                            if min < smallest_tangent:
                                smallest_tangent = min
                            if largest_tangent < max:
                                largest_tangent = max

                    if PRINT_TO_CONSOLE:
                        print(("largest_frame_count: %s\n"
                               "largest_frame_index: %s\n"
                               "largest_tangent: %s\n"
                               "smallest_tangent: %s"
                               ) % (largest_frame_count,
                                    largest_frame_index,
                                    largest_tangent,
                                    smallest_tangent))

                    if (largest_frame_count > 65535 or
                        largest_frame_index > 2047 or
                        256 * smallest_tangent < -32768 or
                            256 * largest_tangent >= 32768):

                        if PRINT_TO_CONSOLE:
                            print("Increased format from %s to i12" % self.__format)
                        self.__format = 'i12'

                    elif self.__format == 'i4':
                        if (largest_frame_index > 255 or
                            32 * smallest_tangent < -2048 or
                                32 * largest_tangent >= 2048):

                            if PRINT_TO_CONSOLE:
                                print("Increased format from %s to i6" % self.__format)
                            self.__format = 'i6'

    def size(self) -> int:
        if self.__has:
            if self.__isotropic:
                return 4
            else:
                return 12
        else:
            return 0

    def has(self) -> bool:
        return self.__has

    def xFixed(self) -> bool:
        return self.__fixed_x

    def yFixed(self) -> bool:
        return self.__fixed_y

    def zFixed(self) -> bool:
        return self.__fixed_z

    def isotropic(self) -> bool:
        return self.__isotropic

    def format(self) -> str:
        return self.__format

    def xData(self) -> list:
        return self.__data_x

    def yData(self) -> list:
        return self.__data_y

    def zData(self) -> list:
        return self.__data_z


def get_fixed(data: list, srt: int) -> list:
    """
    Return a list constaining a constant if the given list is null, empty,
    contains only one element, or containes one unique element. Otherwise,
    return an empty list indicating the given list is not constant.
    """
    if not data:
        return [0] if srt else [1]
    elif len(data) == 1:
        return [data[0]]
    elif type(data[0]) == tuple:
        for tuple_data in data:
            if tuple_data[1] != data[0][1]:
                return []
        return [data[0][1]]
    else:
        for value in data:
            if value != data[0]:
                return []
        return [data[0]]


def combineSRT(s: ChrAnimData, r: ChrAnimData, t: ChrAnimData) -> bytearray:

    def get_header_values(data: list, bit_length: int) -> (int, int):
        """
        Used for I4, I6 and L1 interpolation formats. These formats store the
        value of each keyframe as an integer* using 'bit_length' bits. The
        actual value is obtained by step_header * step_frame + base_header,
        where step_header and base_header are stored in the header and
        step_frame is the value stored in each frame.
        Returns (step_header, base_header).
        Note: step_header and base_header are calculated such that the range of
        values in the list are normalised to the range of an unsigned integer
        represented in bit_length bits.
        *step_frame is actually a float for the L1 format.
        Assumes list contains at least two elements.
        """

        min, max = getDataMaxima(data, 1)

        step_header = (max - min) / (2**bit_length - 1)
        base_header = min
        return step_header, base_header

    def get_frame_value(step_header: float, base_header: float,
                        value: float) -> float:

        if step_header:
            return (value - base_header) / step_header
        else:
            return 0

    node = bytearray(4)

    # type code
    node += struct.pack('>I', (
        s.isotropic() << 0x04
        | r.isotropic() << 0x05
        | t.isotropic() << 0x06
        | s.xFixed() << 0x0D
        | s.yFixed() << 0x0E
        | s.zFixed() << 0x0F
        | r.xFixed() << 0x10
        | r.yFixed() << 0x11
        | r.zFixed() << 0x12
        | t.xFixed() << 0x13
        | t.yFixed() << 0x14
        | t.zFixed() << 0x15
        | s.has() << 0x16
        | r.has() << 0x17
        | t.has() << 0x18
        | CHR0_FORMAT_INDEXES[s.format()] << 0x19
        | CHR0_FORMAT_INDEXES[r.format()] << 0x1B
        | CHR0_FORMAT_INDEXES[t.format()] << 0x1E
    ))

    offset = 4
    node += bytearray(s.size() + r.size() + t.size())

    srt = -1
    for chr_anim_data in [s, r, t]:
        srt += 1
        if chr_anim_data.has():

            axes_info = [
                chr_anim_data.xFixed(), chr_anim_data.xData(),
                chr_anim_data.yFixed(), chr_anim_data.yData(),
                chr_anim_data.zFixed(), chr_anim_data.zData()
            ]

            for xyz in range(0, 1 if chr_anim_data.isotropic() else 3):

                offset += 4

                # if axis does not need a frame data structure
                if axes_info[2 * xyz]:

                    fixed_value = axes_info[2*xyz + 1][0]
                    node[offset: offset + 4] = struct.pack('>f', fixed_value)

                # if axis needs a frame data structure
                else:
                    node[offset: offset + 4] = struct.pack('>I', len(node))

                    if PRINT_TO_CONSOLE:
                        print("Format for SRT(%s): %s" % (srt, chr_anim_data.format()))

                    # Interpolated 4
                    if chr_anim_data.format() == 'i4':

                        frame_scale = 1.0  # often 0x3C381703
                        step, base = get_header_values(axes_info[2*xyz + 1], 12)

                        # header
                        node += struct.pack('>HHfff',
                                            len(axes_info[2*xyz + 1]),  # frame count
                                            0x0000,  # unknown
                                            frame_scale,
                                            step,
                                            base
                                            )

                        # keyframes
                        for frame, value, tangent in axes_info[2*xyz + 1]:

                            value = get_frame_value(step, base, value)
                            value = 4095 if value == 4096 else int(value)

                            node += (
                                to_bits(frame, 8) << 24  # frame of keyframe
                                | to_bits(value, 12) << 12
                                | to_bits(int(tangent * 32), 12, signed=True)
                            ).to_bytes(4, byteorder='big')

                    # Interpolated 6
                    elif chr_anim_data.format() == 'i6':

                        frame_scale = 1.0  # often 0x3C381703
                        step, base = get_header_values(
                            axes_info[2*xyz + 1], 16)

                        # header
                        node += struct.pack('>HHfff',
                                            len(axes_info[2*xyz + 1]),  # frame count
                                            0x0000,  # unknown
                                            frame_scale,
                                            step,
                                            base
                                            )

                        # keyframes
                        for frame, value, tangent in axes_info[2*xyz + 1]:

                            value = get_frame_value(step, base, value)
                            value = 65535 if value == 65536 else int(value)

                            node += (
                                to_bits(frame * 32, 16) << 32  # frame of keyframe
                                | to_bits(value, 16) << 16
                                | to_bits(int(tangent * 256), 16, signed=True)
                            ).to_bytes(6, byteorder='big')

                    # Interpolated 12
                    elif chr_anim_data.format() == 'i12':

                        frame_scale = 1.0  # often 0x3C381703

                        # header
                        node += struct.pack('>HHf',
                                            len(axes_info[2*xyz + 1]),  # frame count
                                            0x0000,  # unknown
                                            frame_scale
                                            )

                        # keyframes
                        for tuple in axes_info[2*xyz + 1]:
                            node += struct.pack('>fff', *tuple)

                    # Linear 1
                    elif chr_anim_data.format() == 'l1':

                        step, base = get_header_values(
                            axes_info[2*xyz + 1], 16)

                        # header
                        node += struct.pack('>ff', step, base)

                        # keyframes
                        for value in axes_info[2*xyz + 1]:
                            value = get_frame_value(step, base, value)
                            node += struct.pack('>f', value)

                    # Linear 4
                    else:

                        # keyframes
                        for value in axes_info[2*xyz + 1]:
                            node += struct.pack('>f', value)

    return node


def get_srt_node(data_all: list) -> bytearray:

    get_srt = {0: 0, 1: 0, 2: 1, 3: 2, 4: 2}

    for i in range(5):
        constant = get_fixed(data_all[i], get_srt[i])
        if constant:
            data_all[i] = constant

    scale_x_fixed = len(data_all[0]) == 1
    scale_y_fixed = len(data_all[1]) == 1
    rotation_fixed = len(data_all[2]) == 1
    translation_x_fixed = len(data_all[3]) == 1
    translation_y_fixed = len(data_all[4]) == 1

    scale_isotropic = data_all[0] == data_all[1]
    scale_has = not (scale_x_fixed and data_all[0][0] == 1
                     and scale_isotropic)
    rotation_has = bool(data_all[2][0])
    translation_has = bool(data_all[3][0]) or bool(data_all[4][0])

    if rotation_has:
        if rotation_fixed:
            data_all[2][0] = math.degrees(data_all[2][0])
        else:
            new_rot_data = []
            for frame, value, tangent in data_all[2]:
                new_rot_data.append((frame, math.degrees(value), math.degrees(tangent)))
            data_all[2] = new_rot_data

    node = bytearray()

    node += struct.pack('>I', (
        1
        | (not scale_has) << 0x01
        | (not rotation_has) << 0x02
        | (not translation_has) << 0x03
        | scale_isotropic << 0x04
        | scale_x_fixed << 0x05
        | scale_y_fixed << 0x06
        | rotation_fixed << 0x07
        | translation_x_fixed << 0x08
        | translation_y_fixed << 0x09
    ))

    node += bytearray(4*(scale_has + (not scale_isotropic) + rotation_has
                           + 2 * translation_has))

    offset = 0

    def append_data(data: list, node: bytearray, srt: int):

        sign = -1 if srt else 1

        if len(data) == 1:
            node[offset: offset + 4] = struct.pack('>f', data[0] * sign)
        else:
            node[offset: offset + 4] = struct.pack('>I', len(node) - offset)
            node += struct.pack('>HHf',
                                len(data),  # frame count
                                0x0000,  # unknown
                                1)  # frame scale

            for frame, value, tangent in data:
                node += struct.pack('>3f',
                                    frame,  # frame index
                                    value * sign,  # value
                                    tangent * sign  # tangent
                                    )

    if scale_has:
        offset += 4
        append_data(data_all[0], node, 0)
        if not scale_isotropic:
            offset += 4
            append_data(data_all[1], node, 0)

    if rotation_has:
        offset += 4
        append_data(data_all[2], node, 1)

    if translation_has:
        offset += 4
        append_data(data_all[3], node, 2)
        offset += 4
        append_data(data_all[4], node, 2)

    return node


def getUniqueFilename(name: str, prepend_blend_filename=True,
                      include_tail=False) -> str:
    """
    If the blend file has not been saved, the function returns a cleaned version
    of the passed string. Otherwise, if a file with the passed name already
    exists in the directory of the blend file, make the name unique. By default,
    the name of the blend file is prepended to the passed name.
    """
    if bpy.data.is_saved:
        # Clean name and prepend blend filename.
        if prepend_blend_filename:
            root_and_ext = os.path.splitext(bpy.data.filepath)
            name_without_ext = os.path.basename(root_and_ext[0])
            head = bpy.path.clean_name(name_without_ext + name)
        else:
            head = bpy.path.clean_name(name)

        # Make 'head' a unique filename if not already.
        tail = os.path.split(bpy.data.filepath)[0]
        if os.path.exists(os.path.join(tail, head)):
            i = 1
            while os.path.exists(os.path.join(tail, ('%s(%s)' % (head, i)))):
                i += 1
            head = '%s(%s)' % (head, i)
            return os.path.join(tail, head) if include_tail else head
        else:
            return os.path.join(tail, head) if include_tail else head
    else:
        return bpy.path.clean_name(suffix)


def getFilename() -> str:
    """
    Returns a name for the file containing meaningful information, including the
    user's name for the node, the type of node and duration of the animation in
    frames.
    """
    settings = bpy.context.scene.brres_animation_exporter_properties
    frame_diff = settings.end_frame - settings.start_frame
    return '_%sNode_%sf_%s' % (settings.node_type,
                               (frame_diff + 1 if frame_diff > -1 else 0), settings.node_name)


def remove_non_ascii(s: str, sub=""):
    return "".join(c if ord(c) < 128 else sub for c in s)


def analyseKeyframeList(FCurve: bpy.types.FCurve, user_left: int,
                        user_right: int, to_be_sampled: bool) -> (int, int, int):
    """
    Analyses the keyframe list in the given FCurve. If to_be_sampled is True,
    keyframes are added to each frame on the interval specified by the user. For
    each endpoint, the keyframe closest to the interval (but outside it or on
    its boundary) is found. If no such keyframe exists, a keyframe is added on
    the boundary of that side of the interval. These two keyframes are selected
    and the curve is sampled. Returns a tuple containing the indexes of the
    endpoint keyframes. If to_be_sampled is False, instead finds and returns the
    index of the leftmost and rightmost keyframes on the given interval. The
    tuple (0, 0, 0) is returned if the F-Curve is None, empty, or if
    to_be_sampled is False and there are no keyframes on the given interval. If
    to_be_sampled is False, the tuple (#, #, 1) is returned if and only if there
    is exactly one keyframe on the given interval.
    """

    if FCurve is None:
        return 0, 0, 0

    elif FCurve.is_empty:
        return 0, 0, 0

    else:
        data_left, data_right = FCurve.range()

        if to_be_sampled:
            if len(FCurve.keyframe_points) == 1:
                return 0, 0, 1
            else:
                if user_left < data_left:
                    # Create new keyframe on left boundary
                    FCurve.keyframe_points.insert(user_left, FCurve.keyframe_points[0].co[1])
                    data_left = user_left
                    FCurve.update()
                    index_start = 0

                elif data_left < user_left:
                    # Get index of keyframe closer to left boundary
                    index_start = optimiseKeyframeIndex(FCurve, user_left, data_left)

                else:
                    index_start = 0

                if data_right < user_right:
                    # Create new keyframe on right boundary
                    FCurve.keyframe_points.insert(user_right, FCurve.keyframe_points[-1].co[1])
                    data_right = user_right
                    FCurve.update()
                    index_end = len(FCurve.keyframe_points)-1

                elif user_right < data_right:
                    # Get index of keyframe closer to right boundary
                    index_end = optimiseKeyframeIndex(FCurve, user_right, data_right)

                else:
                    index_end = len(FCurve.keyframe_points)-1

                bpy.ops.graph.select_all(action='DESELECT')
                FCurve.keyframe_points[index_start].select_control_point = True
                FCurve.keyframe_points[index_end].select_control_point = True
                bpy.ops.graph.sample()  # Create keyframes on each frame between two selected keyframes
                FCurve.update()  # Ensures keyframe list is chronological

                new_index_start = index_start + \
                    (user_left - int(FCurve.keyframe_points[index_start].co[0]))
                new_index_end = new_index_start + (user_right - user_left)

                return new_index_start, new_index_end, user_right - user_left + 1

        else:  # to_be_sampled = False
            size = len(FCurve.keyframe_points)
            new_left_index = getKeyframeIndex(FCurve.keyframe_points, user_left, 0, size-1)
            if FCurve.keyframe_points[new_left_index].co[0] < user_left:
                new_left_index += 1
            new_right_index = getKeyframeIndex(FCurve.keyframe_points, user_right, 0, size-1)
            if user_right < FCurve.keyframe_points[new_right_index].co[0]:
                new_right_index -= 1

            if new_right_index < new_left_index:
                # Indicates no keyframes in range
                return 0, 0, 0  # Evaluates as False

            elif new_left_index == new_right_index:
                # Indicates exactly one keyframe in range. Returns index of single keyframe.
                return new_left_index, new_left_index, 1  # Evaluates as False

            else:
                # Indicates at least two keyframes in range.
                # Returns index of single keyframe.
                return new_left_index, new_right_index, new_right_index-new_left_index + 1


def optimiseKeyframeIndex(FCurve: bpy.types.FCurve, user_frame: int,
                          data_frame: int) -> int:
    """
    Takes user_frame as the left or right boundary, data_frame as some frame
    that falls outside the region defined by the two boundaries. If a keyframe
    on a frame closer or on the boundary (but not inside it) exists, return its
    index within the list, else return the index of the keyframe at data_frame.
    Knowing the keyframes closest to the boundaries will optimise the
    'Sample Keyframes' operation later.
    """
    new_index = getKeyframeIndex(FCurve.keyframe_points, user_frame,
                                 0, len(FCurve.keyframe_points)-1)
    if data_frame < user_frame:
        if user_frame < FCurve.keyframe_points[new_index].co[0]:
            # There will always be at least data_frame to the left of new_index, so new_index-1>=0
            new_index -= 1
    else:  # user_frame > data_frame
        if FCurve.keyframe_points[new_index].co[0] < user_frame:
            # There will always be at least data_frame to the right of new_index, so new_index+1<=len(list)-1
            new_index += 1
    return new_index


def getKeyframeIndex(keyframe_points: bpy.types.FCurveKeyframePoints,
                     frame: int, min: int, max: int) -> int:
    """
    Calls getKeyframeIndexRec and clamps the returned integer to a valid index.
    """
    i = getKeyframeIndexRec(keyframe_points, frame, min, max)
    if i < min:
        return min
    elif i > max:
        return max
    else:
        return i


def getKeyframeIndexRec(keyframe_points: bpy.types.FCurveKeyframePoints,
                        frame: int, min: int, max: int) -> int:
    """
    Recursive binary search for a keyframe point with the given frame. If the
    given list contains a keyframe point with the given frame, returns the index
    of the keyframe point in the list. Otherwise, returns the index of the
    keyframe point left or right of where the absent keyframe point would be.
    """
    mid = (max + min)//2
    value = int(keyframe_points[mid].co[0])
    if min > max or value == frame:
        return mid
    elif value > frame:
        return getKeyframeIndex(keyframe_points, frame, min, mid-1)
    else:
        return getKeyframeIndex(keyframe_points, frame, mid+1, max)


def scaleColourValue(value: float) -> int:
    value *= 256.0
    if value >= 255.5:
        return 255
    elif value <= 0:
        return 0
    else:
        return math.floor(value)


def allFramesAreIntegers(keyframe_points: bpy.types.FCurveKeyframePoints) -> bool:
    """
    Returns whether all keyframe points in the given list have integer frames.
    """
    if keyframe_points:
        i = 0
        while i < len(keyframe_points) and keyframe_points[i].co[0].is_integer():
            i += 1
        return i == len(keyframe_points)

    else:
        return True


def getDataMaxima(data: list, fvt: int) -> (int, int):
    """
    fvt is an integer in range(3) corresponding to the frame, value, tangent
    in a tuple.
    """
    if type(data[0]) == tuple:

        if fvt not in range(3):
            raise ValueError("fvt not in range(3)")

        minimum = data[0][fvt]
        maximum = data[0][fvt]

        for i in range(1, len(data)):
            if data[i][fvt] > maximum:
                maximum = data[i][fvt]
            elif data[i][fvt] < minimum:
                minimum = data[i][fvt]

    else:
        minimum = min(data)
        maximum = max(data)

    return minimum, maximum


def getTangent(x1: float, y1: float, x2: float, y2: float) -> float:

    if x2 - x1 == 0:
        if y2 - y1 >= 0:
            return VERTICAL_TANGENT_GRADIENT
        else:
            return -VERTICAL_TANGENT_GRADIENT
    else:
        return (y2 - y1) / (x2 - x1)


def to_bits(integer: int, length: int, signed=False) -> int:
    """
    Overflow error raised if integer cannot be represented with 'length' bits.
    Assumes length is a positive integer.
    Returned integer is always positive.
    """
    if signed:
        edge = 2**(length - 1)
        if integer in range(-edge, edge):
            if integer < 0:
                return (edge << 1) + integer
            else:
                return integer
        else:
            raise OverflowError("%s not in range(%s, %s)" % (integer, -edge, edge))
    else:
        if integer in range(0, 2**length):
            return integer
        else:
            raise OverflowError("%s not in range(0, %s)" % (integer, 2**length))


def extractKeyframes(
    index_start: int,
    index_end: int,
    keyframe_points: bpy.types.FCurveKeyframePoints,
    frame_start: int,
    frame_end: int
) -> list:
    """
    Converts keyframe points on the user-defined F-Curve interval to a list of
    tuples. The number of keyframe points is not necessarily the number of
    tuples in the returned list. Each tuple contains (frame, value, tangent).
    keyframe_points: list of F-Curve keyframe points
    index_start, index_end: mark subset of keyframe_points to analyse
    frame_start, frame_end: first and last frame of user-defined interval
    Features:
    - A maximum of two tuples will have the same frame
    - Frames are 0-indexed from frame_start
    - Tangents are calculated using keyframe and keyframe handle coordinates
    - Represents keyframe points with 'CONSTANT', 'LINEAR' and 'BEZIER'
      interpolation.
    - For keyframe_points that have 'CONSTANT' or 'LINEAR' interpolation and are
      not on endpoints of the user-defined interval but are the first or last
      keyframe point of the interval:
          - a tuple will be added to represent a keyframe point with frame =
            frame_start or frame_end and calculated values for value and tangent
          - this is done in an effort to best represent the F-Curve displayed
            to the user,
          - this is not attempted for similar keyframe points with 'BEZIER'
            interpolation
    - "Easing Type" is represented
    - A first or last keyframe point will be represented by two tuples if and
      only if it is not on a boundary of the user-defined interval and it
      has 'BEZIER' interpolation and the left and right handles are not
      straight, which prevents adding redundant tuples
    Notes:
    - "Left Handle Type" and "Right Handle Type" are always ignored
    - Vertical handles (handles with Frame = Keyframe), which are supported in,
      Blender, and would otherwise produce undefined tangents, are represented
      by tangents with a large, hardcoded value.
    """

    keyframes = []

    keyframe_start = keyframe_points[index_start]
    if (keyframe_start.co[0] == frame_start or not index_start
            or keyframe_points[index_start - 1].interpolation == 'BEZIER'):
        keyframe_at_next = False

    elif keyframe_points[index_start - 1].interpolation == 'LINEAR':
        x1, y1 = keyframe_points[index_start - 1].co
        x2, y2 = keyframe_points[index_start].co
        tangent = getTangent(x1, y1, x2, y2)

        # find the value of the curve at frame_start
        value = keyframe_points[index_start - 1].co[1] + tangent*(frame_start - x1)

        keyframes.append((0, value, tangent))
        keyframes.append((x2 - frame_start, y1, tangent))

        keyframe_at_next = True

    else:
        x1, y1 = keyframe_points[index_start - 1].co
        keyframes.append((0, y1, 0))
        keyframes.append((keyframe_points[index_start].co[0] - frame_start, y1, 0))
        keyframe_at_next = True

    for i in range(index_start, index_end+1):
        frame_graph_editor = keyframe_points[i].co[0]
        frame = frame_graph_editor - frame_start
        value = keyframe_points[i].co[1]

        interpolation = keyframe_points[i].interpolation

        # if linear, keyframe_at_next will be True,
        # so adding a keyframe at frame_end is redundant
        if interpolation == 'LINEAR' and frame_graph_editor != frame_end:

            # if last keyframe on interval
            if i == index_end:

                # if last keyframe in list
                if i == len(keyframe_points) - 1:

                    # final keyframe is constant
                    keyframes.append((frame, value, 0))
                    keyframes.append((frame_end - frame_start, value, 0))

                # if last keyframe on interval, but not last on list
                else:
                    x1, y1 = keyframe_points[i].co
                    x2, y2 = keyframe_points[i + 1].co
                    tangent = getTangent(x1, y1, x2, y2)
                    keyframes.append((frame, value, tangent))

                    # find the value of the curve at frame_end
                    value = value + tangent*(frame_end - x1)

                    keyframes.append((frame_end - frame_start, value, tangent))

            # if not last keyframe on interval
            else:
                # add two keyframes to create a linear segment of the curve
                x1, y1 = keyframe_points[i].co
                x2, y2 = keyframe_points[i + 1].co
                tangent = getTangent(x1, y1, x2, y2)
                keyframes.append((frame, value, tangent))
                keyframes.append((x2 - frame_start, y2, tangent))
                keyframe_at_next = True

        # if linear, keyframe_at_next will be True,
        # so adding a keyframe at frame_end is redundant
        elif interpolation == 'CONSTANT' and frame_graph_editor != frame_end:

            keyframes.append((frame, value, 0))

            # if last keyframe on interval
            if i == index_end:

                # doesn't matter if keyframe last in list in this case
                keyframes.append((frame_end - frame_start, value, 0))

            # if not last keyframe on interval
            else:
                x2 = keyframe_points[i + 1].co[0]
                keyframes.append((x2 - frame_start, value, 0))
                keyframe_at_next = True

        elif interpolation == 'BEZIER':

            x1, y1 = keyframe_points[i].handle_left
            x2, y2 = keyframe_points[i].co
            left_tangent = getTangent(x1, y1, x2, y2)

            # if keyframe is at right boundary of interval
            if frame_graph_editor == frame_end:

                if not keyframe_at_next:
                    keyframes.append((frame, value, left_tangent))

            else:
                x3, y3 = keyframe_points[i].handle_right
                right_tangent = getTangent(x2, y2, x3, y3)

                # add keyframe for left tangent if different to right tangent
                if not keyframe_at_next and frame and abs(right_tangent - left_tangent) > DISTINCT_TANGENTS_THRESHOLD:
                    keyframes.append((frame, value, left_tangent))

                keyframes.append((frame, value, right_tangent))

                # if not last keyframe on interval and next keyframe not Bezier
                if i < index_end and keyframe_points[i + 1].interpolation != 'BEZIER':

                    x1, y1 = keyframe_points[i + 1].handle_left
                    x2, y2 = keyframe_points[i + 1].co
                    next_left_tangent = getTangent(x1, y1, x2, y2)
                    keyframes.append((x2 - frame_start, y2, next_left_tangent))
                    keyframe_at_next = True

                else:
                    keyframe_at_next = False

    return keyframes
