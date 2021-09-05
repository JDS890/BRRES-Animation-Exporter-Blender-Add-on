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

if "bpy" in locals():
    import importlib
    importlib.reload(bae_main)
    importlib.reload(bae_panels)
    importlib.reload(bae_ops)
    importlib.reload(bae_globals)
    importlib.reload(bae_helpers)

import bpy
from . import bae_main
from . import bae_panels
from . import bae_ops
from . import bae_globals
from . import bae_helpers

bl_info = {
    "name": "BRRES Animation Exporter",
    "author": "JDS",
    "version": (1, 0, 0),
    "blender": (2, 92, 0),
    "location": "Graph editor > N panel > BRRES Animation Exporter",
    "description": "Export F-Curves as CHR0, CLR0 or STR0 node",
    "warning": "Experimental",
    "wiki_url": "https://github.com/JDS890/BRRES-Animation-Exporter-Blender-Add-on/blob/main/README.md",
    "tracker_url": "https://github.com/JDS890/BRRES-Animation-Exporter-Blender-Add-on",
    "category": "Export"
}

classes = (
    bae_main.BrresAnimationExporterProperties,
    bae_panels.BRRESANIMATIONEXPORTER_PT_All,
    bae_ops.BRRESANIMATIONEXPORTER_OT_All
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register properties
    bpy.types.Scene.brres_animation_exporter_properties = bpy.props.PointerProperty(
        type=bae_main.BrresAnimationExporterProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Unregister properties
    del bpy.types.Scene.brres_animation_exporter_properties
