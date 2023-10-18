import bpy 
from bpy.props import IntProperty
from bpy.types import Panel


class SPR_PT_Panel(Panel):
    bl_label = "Sprite 2D"
    b1_category = "Sprite"
    bl_idname = "OBJECT_PT_SPRITE2D"
    bl_space_type ="VIEW_3D"
    bl_region_type = "UI"
    width : IntProperty(name="width",default = 128,min = 0) 

    def draw(self,context):
        scene = context.scene
        props = scene.sprite2d_props
        layout = self.layout
        layout.label(text="Make sure to select ")
        layout.label(text="an armature with animation ")
        layout.separator()
        row = layout.row()
        col = row.column()
        #col = row.column(heading="Camera properties")
        col.operator("object.remove_transition")
        col.prop(props,"camera_angle")
        col.prop(props,"resolution")
        col.prop(props,"camera_scale")
        col.operator("object.setup_camera")
        layout.separator()
        row2 = layout.row()
        col2 = row2.column()
        #col2 = row2.column(heading="Export options")
        col2.prop(props,"render_angles")
        col2.prop(scene,"frame_start")
        col2.prop(scene,"frame_end")
        col2.prop(scene,"frame_step")
        col2.separator()
        col2.prop(scene.render,"filepath")
        col2.separator()
        col2.prop(props,"create_sheet",text = "Generate sprite sheets")        
        col2.separator()
        row3 = layout.row()
        col3 = row3.column()
        col3.prop(props,"row_count",text = "row_count")
        row3.enabled = props.create_sheet
        row4 = layout.row()
        col4 = row4.column()
        col4.operator("object.export_sprite",text = "Export")
        row5 = layout.row()
        row5.operator("object.generate_sheet",text = "Regenerate spritesheet")
        row5.enabled = props.create_sheet
        
        
        
    
        
