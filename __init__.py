# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Sprite2D",
    "author" : "kameloov",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (1, 0, 0),
    "location" : "View3D",
    "warning" : "",
    "category" : "Sprite"
}

import bpy

from . panel import SPR_PT_Panel
from . export_sprite import SPR_OT_Export
from . setup_camera import SPR_OT_Setup
from . sprite2d_properties import Sprite_2D_Properites
from . remove_transition import SPR_OT_Remove_Transition
from . generate_sheet import SPR_OT_Sheet

def register():
    bpy.utils.register_class(SPR_PT_Panel)
    bpy.utils.register_class(SPR_OT_Export)
    bpy.utils.register_class(SPR_OT_Setup)
    bpy.utils.register_class(Sprite_2D_Properites)
    bpy.utils.register_class(SPR_OT_Remove_Transition)
    bpy.utils.register_class(SPR_OT_Sheet)
    bpy.types.Scene.sprite2d_props = bpy.props.PointerProperty(type=Sprite_2D_Properites)


def unregister():
    bpy.utils.unregister_class(SPR_PT_Panel)
    bpy.utils.unregister_class(SPR_OT_Export)
    bpy.utils.unregister_class(SPR_OT_Setup)
    bpy.utils.unregister_class(SPR_OT_Remove_Transition)
    bpy.utils.unregister_class(SPR_OT_Sheet)
    bpy.utils.unregister_class(Sprite_2D_Properites)
    del bpy.types.Scene.sprite2d_props
