import bpy 
import bpy_extras
import mathutils
import math
from mathutils import Vector
from bpy.types import Operator

wm = bpy.context.window_manager

class SPR_OT_Setup(Operator):
    bl_idname = "object.setup_camera"
    bl_label = "Setup Camera"
    _cam  = None
    _obj = None 
    _center = Vector((0,0,0))
    _centers = []
    _max_length = 0 
    _peak_key = 0
    _scene = None
    _props = None

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None #and obj.animation_data is not None

    def execute(self, context):
        self._scene = context.scene
        self._props = self._scene.sprite2d_props
        self._props.resolution = self._props.resolution
        self._scene.render.film_transparent = True
        self._obj = bpy.context.active_object
        bpy.data.scenes['Scene'].render.use_lock_interface = True
        #set origin to center of geometry 
        print("old location ", self._obj.location)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        print("new location ", self._obj.location)
        # add a camera if there is no camera in the scene
        if (context.scene.camera is None):
            # make sure to keep reference to selected object as the camera will become selected when added
            old_obj =bpy.context.active_object
            #bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
            bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0), rotation=(0, 0, 0))
            bpy.context.view_layer.objects.active = old_obj
        self._cam =  self._scene.camera
        # upate camera angle 
        self._props.camera_angle = self._props.camera_angle
        self._obj = bpy.context.active_object
        self.set_frame_range(self._obj)
        keys = self.get_keyframes(self._obj) 
        self._max_length = 0
        print("checking keys ")
        if keys and len(keys) > 0 :
            wm.progress_begin(0,len(keys))

        i = 0 
        centers_sum = Vector((0,0,0))
        max_bounds = []
        self._scene.frame_set(1)
        min_point = Vector((100000000,100000000,100000000))
        max_point = Vector((-100000000,-100000000,-100000000))
        for k in keys:
            i += 1
            wm.progress_update(i)
            self._scene.frame_set(k)
            vectors = self.get__bounding_limits(self._obj)
            min_point = self.min_values(min_point,vectors[0])
            max_point = self.max_values(max_point,vectors[1])
            length = (min_point-max_point).length
            vec = 0.5 *(vectors[0]+vectors[1])
            self._centers.append(vec)
            centers_sum += vec
            #print("length is ",length)
            if length>self._max_length:
                #self._center = 0.5 *(vectors[0]+vectors[6])
                self._max_length= length
                self._peak_key = k
        if keys and len(keys)>0:
            self._center = 0.5*(min_point+max_point)
            #self._center = centers_sum / len(self._centers)
            print("center",self._center)
            print("old center",centers_sum / len(self._centers))
            #self.add_planes(min_point,max_point)
            wm.progress_end()
        else: 
            self._center = self.get_static_mesh_center()
        self.prepare_camera()
        bpy.data.scenes['Scene'].render.use_lock_interface = False
        return {'FINISHED'}
    

    def add_planes(self,minV,maxV):
        #bottom limits
        bpy.ops.mesh.primitive_cube_add(size =0.1, location=(minV.x, minV.y,minV.z))
        bpy.ops.mesh.primitive_cube_add(size =0.1, location=(maxV.x, minV.y,minV.z))
        bpy.ops.mesh.primitive_cube_add(size =0.1, location=(maxV.x, maxV.y,minV.z))
        bpy.ops.mesh.primitive_cube_add(size =0.1, location=(minV.x, maxV.y,minV.z))
        #top limits
        bpy.ops.mesh.primitive_cube_add(size =0.1, location=(minV.x, minV.y,maxV.z))
        bpy.ops.mesh.primitive_cube_add(size =0.1, location=(maxV.x, minV.y,maxV.z))
        bpy.ops.mesh.primitive_cube_add(size =0.1, location=(maxV.x, maxV.y,maxV.z))
        bpy.ops.mesh.primitive_cube_add(size =0.1, location=(minV.x, maxV.y,maxV.z))

    def get_static_mesh_center(self):
        vectors = self.get__bounding_limits(self._obj)
        length = (vectors[0]-vectors[1]).length
        if length>self._max_length:
            self._max_length= length
            self._peak_key = 1
        return  0.5 *(vectors[0]+vectors[1])

    def prepare_camera(self):
        cam_direction = self._cam.matrix_world.to_quaternion() @ Vector((0.0, 0.0, -1.0))
        cam_direction = cam_direction.normalized()
        straf_z = math.sin(math.radians(self._props.camera_angle))
        straf_y = math.cos(math.radians(self._props.camera_angle))
        #print("object pos ",self._obj.location)
        #print("center pos ",self._center)
        self._cam.location = self._obj.location + (-self._max_length*cam_direction)#+ Vector((0.0,0.0,straf_z))
   
        print("camera pos ",self._cam.location)
        self._cam.data.type='ORTHO'
       # print("max_length: ",self._max_length)        
        self._cam.data.ortho_scale = self._max_length
        # update roperty in props 
        self._scene.sprite2d_props.camera_scale = self._max_length
        self._scene.frame_set(self._peak_key)
        self.set_camera_view()
        self._cam.select_set(False)
        self._obj.select_set(True)


    def set_camera_view(self):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].region_3d.view_perspective = 'CAMERA'
                break

    def set_frame_range(self,obj):
        anim = obj.animation_data
        if obj.type =='MESH' and obj.parent  and  obj.parent.type =='ARMATURE':
            anim = obj.parent.animation_data
        self._scene.frame_start = 1
        self._scene.frame_end =1
        if anim is not None and anim.action is not None:
            ran =  anim.action.frame_range
            self._scene.frame_start = int(ran[0])
            self._scene.frame_end =int(ran[1])
      

    def get_keyframes(self,obj):
        keyframes = []
        anim = obj.animation_data
        if obj.type =='MESH' and obj.parent and  obj.parent.type =='ARMATURE':
            anim = obj.parent.animation_data
        if anim is not None and anim.action is not None:
            print(anim.action.frame_range)
            for fcu in anim.action.fcurves:
                for keyframe in fcu.keyframe_points:
                    x, y = keyframe.co
                    if x not in keyframes:
                        keyframes.append((math.ceil(x)))
        else:
            print("animation is none")

        return keyframes
    
    def get_bounding_coords(self,object):
        coords =[]
        box = object.bound_box
        for v in box :
            vec = mathutils.Vector(v)
            v_global = object.matrix_world @ vec
            coords.append(v_global)
 #       print(coords[0])
  #      print("======================")
        return coords

    def get__bounding_limits(self,object):
        minX = 10000000
        minY = 10000000
        minZ = 10000000
        maxX = -10000000
        maxY = -10000000
        maxZ = -10000000
        # if the selected object is a mesh we just return min and max vector from its bounding box
        if object.type == 'MESH' :
            minV = object.matrix_world @ mathutils.Vector(object.bound_box[0])
            #max vector is stored at index 6
            maxV = object.matrix_world @ mathutils.Vector(object.bound_box[6])
            return [minV,maxV]
        # if we reach here this means that the slected item is not a mesh and probably an armature
        # we get limits from the bounding boxes of the armature children
        for obj in bpy.data.objects: 
            if obj.parent == object and obj.type =='MESH': 
                # min vector is sotred at index 0 
                minV = obj.matrix_world @ mathutils.Vector(obj.bound_box[0])
                #max vector is stored at index 6
                maxV = obj.matrix_world @ mathutils.Vector(obj.bound_box[6])
                #min
                minX = min(minX,minV.x,maxV.x)
                minY = min(minY,minV.y,maxV.y)
                minZ = min(minZ,minV.z,maxV.z)
                #max
                maxX = max(maxX,minV.x,maxV.x)
                maxY = max(maxY,minV.y,maxV.y)
                maxZ = max(maxZ,minV.z,maxV.z)
        return [mathutils.Vector((minX,minY,minZ)),mathutils.Vector((maxX,maxY,maxZ))] 


    def min_values(self,v1:Vector,v2:Vector):
        min = v1
        if v2.x<v1.x : min.x = v2.x
        if v2.y<v1.y : min.y = v2.y
        if v2.z<v1.z : min.z = v2.z
        return min

    def max_values(self,v1:Vector,v2:Vector):
        max = v1
        if v2.x>v1.x : max.x = v2.x
        if v2.y>v1.y : max.y = v2.y
        if v2.z>v1.z : max.z = v2.z
        return max