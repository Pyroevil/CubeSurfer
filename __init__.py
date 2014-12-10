#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

bl_info = {
    "name": "Iso Surfer script",
    "author": "Jean-Francois Gallant(PyroEvil)",
    "version": (0, 0, 1),
    "blender": (2, 7, 1),
    "location": "Properties > Mesh Tab",
    "description": ("Iso Surfer script"),
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "http://pyroevil.com/",
    "tracker_url": "http://pyroevil.com/" ,
    "category": "Object"}
    
import bpy
from math import ceil,floor
from bpy.types import Operator,Panel, UIList
from bpy.props import FloatVectorProperty,IntProperty,StringProperty,FloatProperty,BoolProperty, CollectionProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
import bmesh
import sys
from isosurfer import mciso
import time
import ctypes

tmframe = 'init'

def add_isosurf(self, context):

    mesh = bpy.data.meshes.new(name="IsoSurface")
    obj = bpy.data.objects.new("IsoSurface",mesh)
    bpy.context.scene.objects.link(obj)
    obj['IsoSurfer'] = True
    obj.IsoSurf_res = True


class OBJECT_OT_add_isosurf(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_isosurf"
    bl_label = "Add IsoSurface Object"
    bl_options = {'REGISTER', 'UNDO'}

    scale = FloatVectorProperty(
            name="scale",
            default=(1.0, 1.0, 1.0),
            subtype='TRANSLATION',
            description="scaling",
            )

    def execute(self, context):

        add_isosurf(self, context)

        return {'FINISHED'}


# Registration

def add_isosurf_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_isosurf.bl_idname,
        text="IsoSurface",
        icon='OUTLINER_DATA_META')


# This allows you to right click on a button and link to the manual
def add_isosurf_manual_map():
    url_manual_prefix = "http://pyroevil.com"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_object", "Modeling/Objects"),
        )
    return url_manual_prefix, url_manual_mapping    

        

        
def isosurf(context):
    global tmframe
    scn = bpy.context.scene
    

    
    stime = time.clock()
    global a
    
    SurfList = []
    i = 0
    for object in bpy.context.scene.objects:
        if 'IsoSurfer' in object:
            obsurf = object
            mesurf = object.data
            res = object.IsoSurf_res
            SurfList.append([(obsurf,mesurf,res)])
            for item in object.IsoSurf:
                if item.active == True:
                    if item.obj != '':
                        if item.psys != '':
                            SurfList[i].append((item.obj,item.psys,item.sizem))
            i += 1
                            
    for surfobj in SurfList:
        print("start calculation of isosurface")
        #print(surfobj)
        obsurf,mesurf,res = surfobj[0]
        #print(obsurf,mesurf)
        #print(surfobj[1][0])
        ploc = []
        psize = []
        stime = time.clock()
        xmin = 10000000000
        xmax = -10000000000
        ymin = 10000000000
        ymax = -10000000000
        zmin = 10000000000
        zmax = -10000000000
        for obj,psys,sizem in surfobj[1:]:
            print(obj,psys,res,sizem)
            psys = bpy.data.objects[obj].particle_systems[psys].particles
            print(psys)
            psysize = len(psys)
            for par in range(psysize):
                if psys[par].alive_state == 'ALIVE':
                    size = psys[par].size * sizem
                    if psys[par].location.x - size < xmin:
                        xmin = psys[par].location.x - size
                    if psys[par].location.x + size > xmax:
                        xmax = psys[par].location.x + size
                    if psys[par].location.y - size < ymin:
                        ymin = psys[par].location.y - size
                    if psys[par].location.y + size > ymax:
                        ymax = psys[par].location.y + size
                    if psys[par].location.z - size < zmin:
                        zmin = psys[par].location.z - size
                    if psys[par].location.z + size > zmax:
                        zmax = psys[par].location.z + size
                    ploc.append(psys[par].location)
                    psize.append(size)
                    
        if len(psize) > 0:
            lx = xmax - xmin
            ly = ymax - ymin
            lz = zmax - zmin

            xres = (ceil(lx/res) - floor(lx/res)) * res
            xmax += xres
            xres = int(lx / res)
            yres = (ceil(ly/res) - floor(ly/res)) * res
            ymax += yres
            yres = int(ly / res)
            zres = (ceil(lz/res) - floor(lz/res)) * res
            zmax += zres
            zres = int(lz / res)

            print('res:',res,'xmin:',xmin,'xmax:',xmax,' lx:',lx,' xres:',xres)
            print('res:',res,'ymin:',ymin,'ymax:',ymax,' ly:',ly,' yres:',yres)
            print('res:',res,'zmin:',zmin,'zmax:',zmax,' lz:',lz,' zres:',zres)

            p0 = xmin,ymin,zmin
            p1 = xmax,ymax,zmax
            #res=200
            resolution=(xres,yres,zres)
            isolevel=0.0
            print('  pack particles:',time.clock() - stime,'sec')
            a = mciso.isosurface(p0,p1,resolution,isolevel,ploc,psize)

            print('  mciso:',time.clock() - stime,'sec')
            stime = time.clock()
            
            #if "myMesh" in bpy.data.meshes:
                #mesurf = bpy.data.meshes['myMesh']
            #else:
                #mesurf = bpy.data.meshes.new('myMesh')

            #if "myObject" in bpy.data.objects:
                #obsurf = bpy.data.objects['myObject']
            #else:
                #obsurf = bpy.data.objects.new('myObject', mesurf)
                #bpy.context.scene.objects.link(obsurf)


            #obsurf.show_name = True

            bm = bmesh.new()

            bm.from_mesh(mesurf)
            bm.clear()
            for i in range(int(len(a)/9)):

                vertex1 = bm.verts.new( (a[i*9], a[i*9+1], a[i*9+2]) )
                vertex2 = bm.verts.new( (a[i*9+3], a[i*9+4], a[i*9+5]) )
                vertex3 = bm.verts.new( (a[i*9+6], a[i*9+7], a[i*9+8]) )

                bm.faces.new( (vertex1, vertex2, vertex3) ).smooth = True
                
            bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=res/20)

            bm.to_mesh(mesurf)
            scn.update()
            bm.free()
            print('  Bmesh:',time.clock() - stime,'sec')

            #bpy.context.scene.objects.unlink(obsurf)
            #bpy.data.objects.remove(obsurf)
            #bpy.data.meshes.remove(mesurf)


class OBJECT_UL_IsoSurf(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(0.1)
        split.label(str(index))
        split.prop(item, "name", text="", emboss=False, translate=False, icon='OUTLINER_OB_META')
        split.prop(item,"active",text = "")


class UIListPanelExample(Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "IsoSurfer Panel"
    bl_idname = "OBJECT_PT_ui_list_example"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        obj = context.object
        if 'IsoSurfer' in obj:
            layout = self.layout
            box = layout.box()
            row = box.row()
            row.prop(obj,"IsoSurf_res",text = "Voxel size:")
            row = box.row()
            row.template_list("OBJECT_UL_IsoSurf", "", obj, "IsoSurf", obj, "IsoSurf_index")
            col = row.column(align=True)
            col.operator("op.isosurfer_item_add", icon="ZOOMIN", text="").add = True
            col.operator("op.isosurfer_item_add", icon="ZOOMOUT", text="").add = False    
            if obj.IsoSurf and obj.IsoSurf_index < len(obj.IsoSurf):
                row = box.row()
                row.prop(obj.IsoSurf[obj.IsoSurf_index],"active",text = "Active:")
                row = box.row()
                row.label('Object: ')
                row.prop_search(obj.IsoSurf[obj.IsoSurf_index], "obj",context.scene, "objects", text="")
                if obj.IsoSurf[obj.IsoSurf_index].obj != '':
                    if bpy.data.objects[obj.IsoSurf[obj.IsoSurf_index].obj].type != 'MESH':
                        obj.IsoSurf[obj.IsoSurf_index].obj = ''
                    else:
                        row = box.row()
                        row.label('Particles: ')
                        row.prop_search(obj.IsoSurf[obj.IsoSurf_index], "psys",bpy.data.objects[obj.IsoSurf[obj.IsoSurf_index].obj], "particle_systems", text="")
                        if obj.IsoSurf[obj.IsoSurf_index].psys != '':
                            row = box.row()
                            row.prop(obj.IsoSurf[obj.IsoSurf_index],"sizem",text = "Particles Size Multiplier:")
                            row = box.row()
                            #row.prop(obj.IsoSurf[obj.IsoSurf_index],"res",text = "Voxel size:")
                        
            row = box.row()
            box = box.box()
            box.active = False
            box.alert = False
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text = "THANKS TO ALL DONATORS !")
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text = "If you want donate to support my work")
            row = box.row()
            row.alignment = 'CENTER'
            row.operator("wm.url_open", text=" click here to Donate ", icon='URL').url = "www.pyroevil.com/donate/"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text = "or visit: ")
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text = "www.pyroevil.com/donate/")

                
class OBJECT_OT_isosurfer_add(bpy.types.Operator):
    bl_label = "Add/Remove items from IsoSurf obj"
    bl_idname = "op.isosurfer_item_add"
    add = bpy.props.BoolProperty(default = True)

    def invoke(self, context, event):
        add = self.add
        ob = context.object
        if ob != None:
            item = ob.IsoSurf
            if add:
                item.add()
                l = len(item)
                item[-1].name = ("IsoSurf." +str(l))
                item[-1].active = True
                item[-1].sizem = 1.0
                #item[-1].res = 0.25
                item[-1].id = l
            else:
                index = ob.IsoSurf_index
                item.remove(index)

        return {'FINISHED'}                 
                

class IsoSurf(bpy.types.PropertyGroup):
    # name = StringProperty()
    active = BoolProperty()
    id = IntProperty()
    obj = StringProperty()
    psys = StringProperty()
    #res = FloatProperty()
    sizem = FloatProperty()
    weight = FloatProperty()    


def register():
    bpy.utils.register_class(OBJECT_OT_add_isosurf)
    bpy.utils.register_manual_map(add_isosurf_manual_map)
    bpy.types.INFO_MT_mesh_add.append(add_isosurf_button)
    bpy.utils.register_module(__name__)
    bpy.types.Object.IsoSurf = CollectionProperty(type=IsoSurf)
    bpy.types.Object.IsoSurf_index = IntProperty()
    bpy.types.Object.IsoSurf_res = FloatProperty()
    pass


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_isosurf)
    bpy.utils.unregister_manual_map(add_isosurf_manual_map)
    bpy.types.INFO_MT_mesh_add.remove(add_isosurf_button)
    bpy.utils.unregister_module(__name__)
    del bpy.types.Object.IsoSurf
    pass


if isosurf not in bpy.app.handlers.frame_change_post:
    print('create isosurfer handlers...')
    bpy.app.handlers.persistent(isosurf)
    bpy.app.handlers.frame_change_post.append(isosurf)
    print('isosurfer handler created successfully!')

  




