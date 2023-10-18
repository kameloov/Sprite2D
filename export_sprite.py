import bpy
from bpy.types import Operator
from bpy.props import IntProperty
from bpy.props import StringProperty
from math import nan, radians

class SPR_OT_Export(Operator):
    bl_idname = "object.export_sprite"
    bl_label = "export 2d sprite"
    b1_discription ="export 3d model with animation into 2d sprite"

    _props = None
    _angle_delta = 0
    _timer = None
    _index = 0
    _stop = False
    _max =2
    _rendring  = False
    _rest_frame = False
    resolution : IntProperty(name="resolution",default=128,min = 16)
    text : StringProperty(name="x",default="hello")
    _obj = None

    path = ""
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None #and obj.animation_data is not None

    def finished(self,dummy,x = None):
        print("render complete")
        print(self)
        self._index += 1
        self._rendring = False
        self._rest_frame = True
  
    def cancelled(self, dummy,x = None):
        self._stop = True
        
    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'} or self._stop or self._index >= self._max:
            self.cancel(context)
            if self._index==self._max and self._props.create_sheet:
                bpy.ops.object.generate_sheet()
            return {'CANCELLED'}
        if event.type == 'TIMER':
            if not self._rendring :
                if self._rest_frame:
                    print("rest frame")
                    bpy.context.scene.frame_set(1)
                    bpy.ops.transform.rotate(value =self._angle_delta, orient_axis='Z', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
                    context.scene.render.filepath = self.path +str(self._index)+"/"
                    self._rest_frame = False
                else :
                    print(context.scene.render.filepath)
                    bpy.ops.render.render('INVOKE_DEFAULT',write_still=True,animation=True)
                    self._rendring = True

        return {'PASS_THROUGH'}

    def execute(self, context):
        print("=========================")
        bpy.data.scenes['Scene'].render.use_lock_interface = True
        self._props = context.scene.sprite2d_props
        #select armature if mesh is selected 
        if context.active_object.type == 'MESH' and context.active_object.parent_type == 'ARMATURE':
            bpy.context.view_layer.objects.active =  context.active_object.parent
        self._obj =context.active_object
        self._max = self._props.render_angles
        self._angle_delta = radians(360/self._max)
        wm = context.window_manager
        self._rendring = False
        self._rest_frame = True
        self._index = 0
        self_stop = False
        if not self.path:
            self.path = context.scene.render.filepath
        # Remove  rener complete handler if already exists and re add it 
        if  not self.finished.__name__ in [hand.__name__ for hand in bpy.app.handlers.render_complete]:
            bpy.app.handlers.render_complete.append(self.finished)
        # remove render cancelled handler and re add it 
        if not self.cancelled.__name__ in [hand.__name__ for hand in bpy.app.handlers.render_cancel]:
            bpy.app.handlers.render_cancel.append(self.cancelled)
        
        self._timer = wm.event_timer_add(1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

#    def add_empty_parent(self):
#       empty = bpy.data.objects.new("Empty", None)  # Create new empty object
#        self._obj.users_collection[0].objects.link(empty)  # Link empty to the current object's collection
#        empty.empty_display_type = 'PLAIN_AXES'
#        empty.location = self._obj.location
#        self._obj.parent = empty
#        self._obj.location = (0, 0, 0)
#        bpy.context.view_layer.objects.active = empty
        

    def cancel(self, context):
        # reset path to default
        bpy.data.scenes['Scene'].render.use_lock_interface = False
        context.scene.render.filepath = self.path
        print("cancelling")
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        bpy.app.handlers.render_complete.remove(self.finished)
        bpy.app.handlers.render_cancel.remove(self.cancelled)
        print("cancelled")

