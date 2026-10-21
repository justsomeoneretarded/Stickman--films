"""Measured gates plus explicitly separate, non-scored artistic review."""
from __future__ import annotations
import json
import math
from pathlib import Path
import re
import subprocess
import numpy as np
from PIL import Image,ImageDraw
from .motion import pose
from .world import camera
from .voice import read_wav


def probe(path):
    return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(path)],timeout=60))


def motion_report(plan,fps=60,benchmark=False):
    slides=[];reaches=[];jumps=[];scale_errors=[];ground_errors=[];camera_acc=[];intersections=0
    for scene in plan.scenes:
        previous={};prev_camera=None;prev_camera_velocity=None
        for i in range(math.ceil(scene.duration*fps)):
            t=i/fps
            if benchmark:
                from .benchmark import benchmark_pose,benchmark_camera
                poses=[benchmark_pose(t)]
            else:poses=[pose(a,t,scene.duration,ground=650+60*a.depth) for a in scene.actors]
            for n,p in enumerate(poses):
                reaches.append(p.reach_error)
                for side in ("left","right"):
                    ankle=p.joints['ankle_'+side];key=(n,side)
                    old=previous.get(key)
                    if old and old[0] and p.contacts[side]:slides.append(math.dist(ankle,old[1])*fps)
                    ground_errors.append(max(0,ankle[1]-p.ground))
                    previous[key]=(p.contacts[side],ankle)
                    # Limb lengths are checked at every frame, including turns.
                    for a,b,length in [("hip_","knee_",66),("knee_","ankle_",66)]:
                        scale_errors.append(abs(math.dist(p.joints[a+side],p.joints[b+side])-length))
                oldroot=previous.get((n,"root"))
                if oldroot:jumps.append(math.dist(p.root,oldroot)*fps)
                previous[(n,"root")]=p.root
            cx,cy,z=camera(scene,t,scene.duration,poses[0].root[0]) if not benchmark else benchmark_camera(t,poses[0].root[0])
            cur=np.array([cx,cy,z*100])
            if prev_camera is not None:
                velocity=(cur-prev_camera)*fps
                if prev_camera_velocity is not None:camera_acc.append(float(np.linalg.norm(velocity-prev_camera_velocity))*fps)
                prev_camera_velocity=velocity
            prev_camera=cur
    return {
      "samples_per_second":fps,"max_planted_foot_speed_px_s":max(slides,default=0),
      "max_leg_reach_error_px":max(reaches,default=0),"max_ground_penetration_px":max(ground_errors,default=0),
      "max_leg_length_error_px":max(scale_errors,default=0),"max_root_speed_px_s":max(jumps,default=0),
      "max_camera_acceleration_design_units_s2":max(camera_acc,default=0),
      "passes_contact_gate":max(slides,default=0)<2 and max(reaches,default=0)<2 and max(ground_errors,default=0)<.1 and max(scale_errors,default=0)<.1,
      "limitations":["Limb overlap is artistically reviewed; no general collision solver.","Camera statistic excludes intentional scene cuts.","Root speed is measured; speed discontinuities need sequence review.","Stair, sit and fall clips are simplified; benchmark qualifies level-ground locomotion only."]}


def review_images(video,out,duration):
    out=Path(out);frames=out/'frames';frames.mkdir(exist_ok=True)
    stamps=np.linspace(.2,max(.2,duration-.3),12)
    sheet=Image.new('RGB',(1280,4*210),'#182938');draw=ImageDraw.Draw(sheet)
    for i,t in enumerate(stamps):
        path=frames/f'{i:02d}.png'
        subprocess.run(["ffmpeg","-v","error","-y","-ss",str(t),"-i",str(video),"-frames:v","1","-vf","scale=426:240",str(path)],check=True,timeout=30)
        im=Image.open(path).convert('RGB').resize((320,180));x=(i%4)*320;y=(i//4)*210
        sheet.paste(im,(x,y));draw.text((x+8,y+185),f'{t:.2f}s',fill='#f4eddb')
    sheet=sheet.crop((0,0,1280,3*210));sheet.save(out/'contact-sheet.jpg',quality=94)
    # Actual playable excerpt, no optical-flow interpolation hiding bad poses.
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(min(7,duration/3)),"-i",str(video),"-t","6","-c:v","libx264","-crf","20","-c:a","aac",str(out/'motion-preview.mp4')],check=True,timeout=90)


def assess(video,plan,out,width,height,fps,segments,benchmark=False):
    out=Path(out);meta=probe(video);streams=meta['streams'];v=next(s for s in streams if s['codec_type']=='video');a=next((s for s in streams if s['codec_type']=='audio'),{})
    duration=float(meta['format']['duration']);requested=plan.requested_minutes*60
    decode=subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(video),"-f","null","-"],capture_output=True,text=True,timeout=max(120,int(duration*3)))
    # Conservative freeze threshold: intentional held acting must not be called a
    # freeze merely because only brows/breathing change. All detections are reported.
    filters=subprocess.run(["ffmpeg","-v","info","-i",str(video),"-vf","blackdetect=d=0.15:pix_th=0.02:pic_th=0.98,freezedetect=n=0.0001:d=3","-an","-f","null","-"],capture_output=True,text=True,timeout=max(120,int(duration*3)))
    detections=[l.strip() for l in filters.stderr.splitlines() if ('black_start:' in l or 'freeze_' in l)]
    audio=subprocess.run(["ffmpeg","-v","info","-i",str(video),"-af","astats=metadata=0:reset=0,ebur128=peak=true","-vn","-f","null","-"],capture_output=True,text=True,timeout=120)
    peaks=[float(v) for v in re.findall(r'Peak level dB:\s*([-\d.]+)',audio.stderr)]
    fraction=lambda s:float(s.split('/')[0])/float(s.split('/')[1])
    motion=motion_report(plan,fps,benchmark)
    checks={"exists":Path(video).stat().st_size>1000,"decodes":decode.returncode==0,
      "resolution":(v['width'],v['height'])==(width,height),"frame_rate":abs(fraction(v['avg_frame_rate'])-fps)<.01,
      "video_codec":v['codec_name']=='h264',"pixel_format":v['pix_fmt']=='yuv420p',
      "audio_codec":a.get('codec_name')=='aac',"audio_rate":a.get('sample_rate')=='48000',"stereo":a.get('channels')==2,
      "duration":.75*requested<=duration<=1.25*requested,"timeline_contiguous":all(abs(a.end-b.start)<.001 for a,b in zip(plan.scenes,plan.scenes[1:])),
      "timeline_matches_media":abs(plan.scenes[-1].end-duration)<max(.15,2/fps),
      "no_black_frames":not any('black_start:' in x for x in detections),
      "no_detected_freeze":not any('freeze_start:' in x for x in detections),
      "no_audio_clipping":bool(peaks) and max(peaks)<-.1,
      "motion_contacts":motion['passes_contact_gate']}
    narr=[]
    for seg in segments:
        samples,sr=read_wav(seg['path']);rms=float(np.sqrt(np.mean(samples*samples)))
        valid=not seg['text'].strip() or (rms>.001 and seg['audio_seconds']<=seg['end']-seg['start']+.01)
        narr.append({"scene":seg['scene'],"rms":rms,"audio_seconds":seg['audio_seconds'],"present_and_fits":valid})
    checks['narration_present']=all(x['present_and_fits'] for x in narr)
    report={"technical_pass":all(checks.values()),"checks":checks,"requested_seconds":requested,"actual_seconds":duration,
      "technical":{"video":v,"audio":a,"size_bytes":Path(video).stat().st_size,"peak_dbfs":max(peaks,default=None),"detections":detections},
      "script":{"provenance":plan.provenance,"factual_status":plan.factual_status,"beats":[s.beat for s in plan.scenes],"words":sum(len(s.narration.split())+sum(len(d.split()) for d in s.dialogue) for s in plan.scenes),"sources":[s.model_dump() for s in plan.sources]},
      "narration":narr,"motion":motion,
      "sound_sync":"Footsteps follow IK contacts. Authored cues use measured utterance fractions. Word-level alignment is estimated, not forced-aligned.",
      "artistic_review":{"status":"pending human review","professional_quality_claimed":False,"limitations":["Finite procedural action and prop vocabulary; complex brief actions need new clips.","Kokoro voices lack reliable emotional control; no listening panel or ASR fidelity gate.","Basic procedural music, not a bespoke composition.","Segment captions use estimated word timing.","No general physics/collision or autonomous fact-checking."]}}
    (out/'quality-report.json').write_text(json.dumps(report,indent=2))
    (out/'audio-analysis.log').write_text(audio.stderr)
    (out/'decode.log').write_text(decode.stderr);(out/'frame-detection.log').write_text(filters.stderr)
    review_images(video,out,duration)
    lines=[f'# {plan.title}',f'Technical gates: {"PASS" if report["technical_pass"] else "FAIL"}',f'Requested: {requested:.2f}s; measured: {duration:.2f}s.',f'Format: {width} × {height}, {fps} FPS, H.264 + stereo AAC.',f'Creative source: {plan.provenance}; factual status: {plan.factual_status}.','', '| Gate | Result |','|---|---|']
    lines += [f'| {k} | {"PASS" if v else "FAIL"} |' for k,v in checks.items()]
    lines += ['', 'Artistic quality is not numerically scored. See contact-sheet.jpg and motion-preview.mp4.', '', 'Known limitations:']+[f'- {v}' for v in report['artistic_review']['limitations']]
    (out/'quality-report.md').write_text('\n'.join(lines)+'\n')
    return report
