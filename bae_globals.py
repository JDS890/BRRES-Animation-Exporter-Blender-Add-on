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

# Different types of formats used to store sets of keyframes in Nintendo CHR0
# animation files. Interpolated formats store tangent information, whereas
# linear formats do not.
CHR0_INTERPOLATED_FORMATS = ["i4", "i6", "i12"]
CHR0_LINEAR_FORMATS = ["l1", "l4"]

# Blender supports keyframes with vertical tangents, BRRES CHR0 and STR0 files
# do not. Hence, a large value is used to approximate vertical gradients.
# Note: >= 64 upgrades file to i6
#       >= 128 upgrades file to i12
VERTICAL_TANGENT_GRADIENT = 1000

# Keyframes with left and right tangents that differ by more than this value
# will be stored as two distinct points in CHR0 and STR0 nodes.
DISTINCT_TANGENTS_THRESHOLD = 0.00001

# Dictionary of CHR0 curve formats and their representative index stored in the
# file.
CHR0_FORMAT_INDEXES = {
    'none': 0,
    'i4':   1,
    'i6':   2,
    'i12':  3,
    'l1':   4,
    'l4':   6
}

# Whether debugging information is printed to Blender's console.
PRINT_TO_CONSOLE = False
