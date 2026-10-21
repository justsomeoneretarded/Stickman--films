"""Optional Cycles cost probe, not a production backend. blender -b -t 1 -P scripts/blender_cost_probe.py -- work/blender-probe"""
import bpy, math, time, json, sys
from pathlib import Path
out=Path(sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "work/blender-probe").resolve();out.mkdir(parents=True,exist_ok=True)
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=False
scene.render.threads_mode='FIXED';scene.render.threads=1
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.world.color=(.4,.4,.4)

def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);return m
ink=mat('ink',(.07,.13,.18));mint=mat('mint',(.32,.60,.50));paper=mat('paper',(.93,.88,.75));floor=mat('floor',(.62,.66,.53))
def sphere(name,p,r,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=r,location=p);o=bpy.context.object;o.name=name;o.data.materials.append(m)
def rod(a,b,r,m):
 mid=(Vector(a)+Vector(b))/2;v=Vector(b)-Vector(a)
 bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=v.length,location=mid);o=bpy.context.object;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(m)
rod((0,0,1.2),(0,0,2),.10,mint);sphere('head',(0,0,2.35),.30,paper)
for s in [-1,1]:
 rod((0,0,1.2),(.25*s,0,.65),.055,ink);rod((.25*s,0,.65),(.3*s,0,.1),.055,ink)
 rod((0,0,1.9),(.35*s,0,1.6),.05,ink);rod((.35*s,0,1.6),(.3*s,-.1,1.3),.05,ink)
bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.data.materials.append(floor)
for x,z in [(-3,4),(3,5),(-6,6)]:
 rod((x,2,0),(x,2,2.5),.15,ink);sphere('tree',(x,2,3),1,mint)
bpy.ops.object.light_add(type='AREA',location=(0,-3,7));bpy.context.object.data.energy=1200;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=5
bpy.ops.object.camera_add(location=(4,-8,3));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8;scene.camera=cam
started=time.monotonic()
for i in range(3):
 scene.render.filepath=str(out/f'blender-cost-{i}.png');bpy.ops.render.render(write_still=True)
json.dump({'frames':3,'seconds':time.monotonic()-started,'resolution':[1920,1080],'samples':4,'threads':1,'note':'Simple mesh proxy, not equivalent art; no encoding; not representative full-film throughput'},(out/'blender-cost.json').open('w'),indent=2)
