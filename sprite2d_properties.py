import bpy 
from bpy.props import (FloatProperty,BoolProperty,IntProperty)
from math import radians

class Sprite_2D_Properites(bpy.types.PropertyGroup):
    def update_camera_angle(self,context):
        camera = context.scene.camera
        camera.rotation_euler[0] =radians(90 -self.camera_angle)
    
    def update_resolution(self,context):
        context.scene.render.resolution_x = self.resolution
        context.scene.render.resolution_y = self.resolution

    def update_scale(self,context):
        context.scene.camera.data.ortho_scale = self.camera_scale
    

    resolution : IntProperty(name="Resolution(px)",soft_min =8, min = 0, step = 2,default = 128,
    description="the texture width and height in pixel",update = update_resolution)
    camera_angle : IntProperty(name="Camera angle",min = 0, max = 90 , default = 45,update= update_camera_angle)
    render_angles : IntProperty(name="Render angles",min = 1, max = 128 , default = 8)
    row_count : IntProperty(name="Row count",min = 1, max = 128 , default = 2)
    camera_scale : FloatProperty(name="Camera Scale",min = 0 , default = 1.2, update = update_scale)
    create_sheet: BoolProperty(name="Generate spritesheet",default = False)