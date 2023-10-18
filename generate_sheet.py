import bpy 
import os
import numpy as np
from bpy.types import Operator
from bpy.props import (StringProperty)

wm = bpy.context.window_manager

class SPR_OT_Sheet(Operator):
    bl_idname = "object.generate_sheet"
    bl_label = "generate spritesheet"
    folder : StringProperty(name="Folder", default = "")
    _props = None

    def execute(self, context):
        self._props = context.scene.sprite2d_props
        scene = context.scene
        row_count = self._props.row_count
        length = self._props.resolution
        wm.progress_begin(0,self._props.render_angles)
        for i in range(self._props.render_angles):
            root_folder = context.scene.render.filepath + "%d/"%i
            files = self.get_file_paths(root_folder,scene.frame_start,scene.frame_end,scene.frame_step)
            wm.progress_update(i)
            self.generate_sprite_sheet(files,row_count,length)
        wm.progress_end()
        return {'FINISHED'}     

    def generate_sprite_sheet(self,files,row_count,length):
        print("rendering files",files)
        images = [np.array(bpy.data.images.load(p, check_existing=False).pixels) for p in files]
        print(len(images))
        # if the image blocks count is odd add an empty transparent image block to complete the final image
        items_per_row = len(images) // row_count
        if len(images) % row_count != 0 : 
            items_per_row += 1
        items_to_add = (items_per_row * row_count) - len(images)
        for _ in range(items_to_add): 
            images.append(self.create_empty_sprite(length))
        print(len(images))
        images_rows = [np.array_split(img,length) for img in images]
        final_pixels = []
        sprite_rows = np.array_split(images_rows,row_count)
        final_rows = [self.merge_sprite_in_row(row) for row in sprite_rows]
        final_rows.reverse()
        final_pixels = self.merge_rows(final_rows).flatten()
        directory = os.path.dirname(files[0])+"/"
        output_image = bpy.data.images.new( 'sprite.png', alpha=True, width=length*len(sprite_rows[0]), height=length* len(sprite_rows))
        output_image.alpha_mode = 'STRAIGHT'          
        output_image.pixels = final_pixels
        output_image.filepath_raw = directory +'sprite.png'
        output_image.file_format = bpy.context.scene.render.image_settings.file_format
        output_image.save()

    # get the file names for a render based on start frame, end frame, and frame step 
    def get_file_paths(self,root_path,start,end,step):
        return [root_path+'%04d.png'% i for i in range(start,end+1,step)]

    def merge_sprite_in_row(self,sprites):
        tup = tuple(item for item in sprites)
        return np.hstack(tup)


    def merge_rows(self,rows):
        tup = tuple(row for row in rows)
        return np.vstack(tup)

    def create_empty_sprite(self,size):
        return  [1,1,1,0] * size * size
    