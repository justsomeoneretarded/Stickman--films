"""Original procedural score/foley; no unlicensed downloaded sound library."""
from pathlib import Path
import json
import math
import subprocess
import numpy as np
from .voice import read_wav,write_wav
from .motion import pose

SR=24000
MOODS={"curious":([146.83,174.61,220,261.63],.7),"comic":([196,246.94,293.66,392],1.1),
"tense":([110,116.54,164.81,220],.42),"warm":([130.81,164.81,196,261.63],.6),
"wonder":([146.83,220,293.66,369.99],.55),"silence":([0],.5)}


def effect(kind,rng,gain=.4):
    duration={"step":.12,"impact":.22,"click":.06,"chime":.6,"whoosh":.4,"tick":.07,"pickup":.25}[kind]
    t=np.arange(round(duration*SR))/SR
    env=np.exp(-t/(duration*.22))*np.minimum(t/.004,1)
    if kind in ("step","impact","tick","click"):
        a=(rng.normal(0,.4,len(t))*.35+np.sin(2*np.pi*(90 if kind=="step" else 160)*t))*env
    elif kind in ("chime","pickup"):
        a=(np.sin(2*np.pi*660*t)+.4*np.sin(2*np.pi*990*t))*env
    else:
        noise=rng.normal(0,.5,len(t));a=noise*np.sin(np.pi*t/duration)**2*.3
    return (a*gain*.24).astype(np.float32)


def add(target,a,start,gain=1):
    start=max(0,int(start*SR));end=min(len(target),start+len(a))
    if end>start:target[start:end]+=a[:end-start]*gain


def sound_mix(plan,segments,out,benchmark=False):
    out=Path(out);total=plan.scenes[-1].end
    voice=np.zeros(round(total*SR),np.float32);music=voice.copy();fx=voice.copy()
    rng=np.random.default_rng(plan.seed);events=[]
    for scene,seg in zip(plan.scenes,segments):
        a,sr=read_wav(seg['path'])
        if sr!=SR:raise ValueError("Narration must be 24 kHz")
        add(voice,a,scene.start)
        length=round(scene.duration*SR);t=np.arange(length)/SR
        notes,tempo=MOODS[scene.music]
        score=np.zeros(length,np.float32)
        if scene.music!="silence":
            # Soft sustained harmony and sparse plucked tones; distinct niche moods.
            for j,note in enumerate(notes[:3]):score+=.006*np.sin(2*np.pi*note*t+j*.3)
            for beat in np.arange(0,scene.duration,1/tempo):
                note=notes[int(beat*tempo)%len(notes)];z=t-beat
                mask=z>=0;score[mask]+=.018*np.sin(2*np.pi*note*2*z[mask])*np.exp(-z[mask]*4)
            fade=np.minimum(t/.6,1)*np.minimum((scene.duration-t)/.7,1)
            score*=np.maximum(0,fade)
        # Fast attack and 250ms release ducking from measured speech envelope.
        padded=np.zeros(length,np.float32);padded[:min(length,len(a))]=a[:length]
        block=240;blocks=math.ceil(length/block)
        env=np.array([np.sqrt(np.mean(padded[i*block:(i+1)*block]**2)) for i in range(blocks)])
        active=(env>.008).astype(float)
        for i in range(1,len(active)):active[i]=max(active[i],active[i-1]*.96)
        duck=np.repeat(1-.75*active,block)[:length]
        add(music,score*duck,scene.start)
        for cue in scene.cues:
            at=scene.start+cue.at*max(.01,scene.duration-scene.pause)
            add(fx,effect(cue.kind,rng,cue.gain),at);events.append({"scene":scene.id,"at":at,"kind":cue.kind,"basis":"authored narration fraction"})
        # Foley from actual contact-state changes, not a separate ticking timer.
        previous={};laststep=-1
        for i in range(math.ceil(scene.duration*60)):
            at=i/60
            if benchmark:
                from .benchmark import benchmark_pose
                p=benchmark_pose(at)
            else:p=pose(scene.actors[0],at,scene.duration)
            for side,contact in p.contacts.items():
                if contact and previous.get(side) is False and at-laststep>.12:
                    add(fx,effect("step",rng,.35),scene.start+at)
                    events.append({"scene":scene.id,"at":scene.start+at,"kind":"step","basis":"IK contact"});laststep=at
                previous[side]=contact
    # Pre-normalization headroom and final two-pass EBU R128 mastering.
    raw=voice+music+fx;peak=float(np.max(np.abs(raw)))
    if peak>.90:raw*=.90/peak
    write_wav(out/'mix-unmastered.wav',raw)
    first=subprocess.run(["ffmpeg","-v","info","-i",str(out/'mix-unmastered.wav'),"-af","loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json","-f","null","-"],capture_output=True,text=True,check=True,timeout=120)
    pos=first.stderr.rfind('{');measurement=json.JSONDecoder().raw_decode(first.stderr[pos:])[0]
    measured=all(math.isfinite(float(measurement[k])) for k in ['input_i','input_tp','input_lra','input_thresh','target_offset'])
    af=(f"loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={measurement['input_i']}:measured_TP={measurement['input_tp']}:measured_LRA={measurement['input_lra']}:measured_thresh={measurement['input_thresh']}:offset={measurement['target_offset']}:linear=true" if measured else "alimiter=limit=0.8")
    subprocess.run(["ffmpeg","-v","error","-y","-i",str(out/'mix-unmastered.wav'),"-af",af,"-ar",str(SR),str(out/'mix.wav')],check=True,timeout=120)
    (out/'sound-events.json').write_text(json.dumps(events,indent=2));(out/'loudness.json').write_text(json.dumps(measurement,indent=2))
    return out/'mix.wav'
