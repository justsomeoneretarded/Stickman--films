"""Direct BGRA streaming to FFmpeg; no per-frame disk or Python pixel loops."""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import time
import cairocffi as cairo
import numpy as np
from .drawing import *
from .world import background,ground,foreground,camera
from .motion import pose,smooth

PRESETS={"draft":(640,360,24),"preview":(1280,720,24),"production":(1920,1080,60)}


def draw_frame(scene,t,width,height,*,benchmark=False,previous=None):
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
    c=cairo.Context(surface);c.scale(width/1600,height/900)
    duration=scene.duration;u=min(1,t/max(duration,.001))
    if benchmark:
        from .benchmark import benchmark_pose,benchmark_camera
        poses=[benchmark_pose(t)]
        focus=poses[0].root[0]
        # Hold the establish, then gently pick up the tracking camera.
        cx,cy,zoom=benchmark_camera(t,focus)
        pan=cx-800
    else:
        poses=[pose(a,t,duration,ground=650+60*a.depth) for a in scene.actors]
        focus=poses[0].root[0]
        cx,cy,zoom=camera(scene,t,duration,focus)
        pan=cx-800
    background(c,scene.environment,scene.lighting,t,pan)
    c.save();c.translate(800,450);c.scale(zoom,zoom);c.translate(-cx,-cy)
    ground(c,scene.environment,t,pan)
    prop_x=1040 if not benchmark else 1570
    prop_y=710
    kind=scene.prop if not benchmark else "box"
    primary=poses[0]
    if primary.pickup>0:
        w=primary.pickup
        prop_x=prop_x*(1-w)+(primary.prop_hand[0])*w
        prop_y=prop_y*(1-w)+(primary.prop_hand[1]+30)*w
    main_scale=.75 if benchmark else 1.1
    if scene.prop_motion in ("grow","reveal"):main_scale*=max(.001,smooth((u-.15)/.6))
    if not benchmark or t>14:draw_prop(c,kind,prop_x,prop_y,t,scale=main_scale,label=scene.prop_label,progress=smooth((u-.25)/.45) if scene.prop_motion=="open" else 0)
    for obj in scene.props:
        q=smooth((u-obj.start_at)/max(.001,obj.end_at-obj.start_at))
        if obj.motion=="reveal" and q<=0:continue
        scale=obj.scale*(max(.001,q) if obj.motion in ("reveal","grow") else 1)
        ox,oy=obj.x,obj.y
        if obj.attach_to!="world":
            hand=poses[obj.actor_index].joints["wrist_"+("left" if obj.attach_to=="left-hand" else "right")]
            ox+=hand[0];oy+=hand[1]
        draw_prop(c,obj.kind,ox+obj.travel*q,oy+obj.travel_y*(min(1,max(0,(u-obj.start_at)/(obj.end_at-obj.start_at)))**2 if obj.motion=="drop" else q),t,scale=scale,label=obj.label,progress=q if obj.motion=="open" else 0)
    for a,p in sorted(zip(scene.actors,poses),key=lambda v:v[0].depth):
        c.save()
        # A depth plane scales a whole rig around its ground anchor.
        if a.depth!=1:c.translate(p.root[0],p.ground);c.scale(a.depth,a.depth);c.translate(-p.root[0],-p.ground)
        talking=.45*max(0,math.sin(t*16)) if scene.dialogue else 0
        draw_character(c,p,a.character,talking)
        c.restore()
    foreground(c,scene.environment,t,pan)
    c.restore()
    # Graphic typography belongs to screen space. It is never the main action.
    label=scene.label
    if benchmark:
        label=next((v for limit,v in [(2,"01 / FIND YOUR BALANCE"),(7,"02 / ONE STEP AT A TIME"),(9,"03 / BUILD MOMENTUM"),(12,"04 / RUN WITH IT"),(15,"05 / LAND THE STOP"),(17,"06 / CHANGE YOUR MIND"),(20.3,"07 / PICK UP SOMETHING NEW"),(23,"08 / WELL, HELLO THERE")] if t<limit),"")
    header_color=PAPER if scene.lighting in ("night","dramatic") else INK
    text(c,"SMALL WORLDS  /  ORIGINAL ANIMATION",80,74,16,header_color,True)
    if label:
        for i,v in enumerate(wrap(c,label,1120,38,2)):text(c,v,80,135+i*47,38,header_color,True)
    if scene.narration:
        words=scene.narration.split()
        # Segment-level timing is measured, word positions are explicitly estimates.
        group=7;chunks=[" ".join(words[i:i+group]) for i in range(0,len(words),group)]
        idx=min(len(chunks)-1,int(max(0,t-.12)/max(.1,duration-scene.pause)*len(chunks)))
        if chunks and t<duration-scene.pause:
            caption=chunks[max(0,idx)]
            c.select_font_face("DejaVu Sans");c.set_font_size(25)
            w=c.text_extents(caption)[2]
            rect(c,800-w/2-23,808,w+46,49,INK,12,alpha=.88)
            text(c,caption,800-w/2,841,25,PAPER)
    # Subtle edge vignette, without black transitions or hidden frames.
    g=cairo.RadialGradient(800,420,430,800,420,1050)
    g.add_color_stop_rgba(0,0,0,0,0);g.add_color_stop_rgba(1,.08,.13,.17,.16)
    c.set_source(g);c.paint()
    if scene.transition in ("dissolve","wipe") and t<.25:
        rect(c,0,0,1600 if scene.transition=="dissolve" else 1600*(1-smooth(t/.25)),900,"#e9dfc9",alpha=(1-smooth(t/.25))*.35)
    surface.flush()
    return surface,poses,(cx,cy,zoom)


def render_scene(scene,path,width,height,fps,benchmark=False,revision="v1"):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    # Revision also hashes renderer sources: edits cannot reuse stale scene files.
    source_hash=hashlib.sha256(b"".join((Path(__file__).parent/n).read_bytes() for n in ["render.py","drawing.py","world.py","motion.py","benchmark.py"])).hexdigest()
    key=hashlib.sha256(json.dumps([scene.model_dump(),width,height,fps,benchmark,revision,source_hash],sort_keys=True).encode()).hexdigest()
    meta=path.with_suffix(".cache.json")
    if path.exists() and meta.exists() and json.loads(meta.read_text()).get("key")==key:
        try:
            subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(path),"-f","null","-"],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=120)
            return json.loads(meta.read_text())|{"cache_hit":True}
        except (subprocess.CalledProcessError,subprocess.TimeoutExpired):pass
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","bgra","-s",f"{width}x{height}","-r",str(fps),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","18","-pix_fmt","yuv420p","-threads",os.getenv("RENDER_THREADS","2"),"-movflags","+faststart",str(path)]
    started=time.monotonic();frames=round(scene.duration*fps)
    log=path.with_suffix(".ffmpeg.log")
    with log.open("w") as errors:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=errors)
        try:
            for i in range(frames):
                surface,_,_=draw_frame(scene,i/fps,width,height,benchmark=benchmark)
                p.stdin.write(surface.get_data())
            p.stdin.close()
            code=p.wait(timeout=120)
            if code:raise RuntimeError(f"Encoder failed ({code}); see {log}")
        except BaseException:
            p.kill();p.wait();raise
    result={"key":key,"frames":frames,"seconds":time.monotonic()-started,"width":width,"height":height,"fps":fps,"cache_hit":False}
    meta.write_text(json.dumps(result,indent=2))
    return result


def assemble(scene_files,audio,out):
    out=Path(out)
    listing=out.parent/"concat.txt"
    # Paths are generated by the pipeline, not model-provided shell code.
    listing.write_text("".join("file '"+str(Path(p).resolve()).replace("'","'\\''")+"'\n" for p in scene_files))
    subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(listing),"-i",str(audio),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000","-ac","2","-shortest","-movflags","+faststart",str(out)],check=True,timeout=600)
