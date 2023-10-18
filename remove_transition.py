import bpy 
import bpy_extras
import mathutils
import math
from mathutils import Vector
from bpy.types import Operator

wm = bpy.context.window_manager

class SPR_OT_Remove_Transition(Operator):
    bl_idname = "object.remove_transition"
    bl_label = "Make animation in place"
    _obj = None 
    _scene = None
    _props = None

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.animation_data is not None

    def execute(self, context):
        self._scene = context.scene
        self._props = self._scene.sprite2d_props
        self._obj = bpy.context.active_object
        # set animation to frame 1
        self._scene.frame_set(1)
        bone = self.find_root_bone()
        if bone is None :
            self.report({"WARNING"},"No root bone found")
        else :
            #self.report({"WARNING"},bone.name)
            z = self.find_z_global()
            print("keeping axis ",z)
            # remove all location curves for root bone so we pass -1 if we want to keep z we pass it
            self.remove_xy(bone.name,-1)
        return {'FINISHED'}
    
    def find_root_bone(self):
        bones = self._obj.data.bones
        if bones is None or len(bones) == 0 :
            return None
        for b in bones: 
            if b.parent is None: 
                return b
        return None


    # finds the ocal z direction in global coords and return index indicating axis
    def find_z_global(self):
        obj = self._obj
        coords = []
        mat = obj.matrix_world.normalized()
        z = [mat[0][2],mat[1][2],mat[2][2]]
        # find  local z global direction 0,1,2 means x,y,z 
        index = 0 
        for i in z : 
            if abs(i) == 1 :
                self.report({"INFO"},"Converted successfully")
                return index
            index +=1 
        return 2
        
       


    def remove_xy(self,bone_name,axis_to_keep):
        anim = self._obj.animation_data
        if anim is not None and anim.action is not None:
            temp = []
            for fcu in anim.action.fcurves:
                path =  fcu.data_path 
                # we want to remove curves related to bone location and only x and y where index 0 and 1
                if path is not None and path.find(bone_name) > 0 and  path.find('location')>0 and fcu.array_index != axis_to_keep:
                    temp.append(fcu)
            # now remove the x,y curves related to bone 
            for c in temp:
                anim.action.fcurves.remove(c)
        else:
            self.report({"WARNING"},"No animation was found")
