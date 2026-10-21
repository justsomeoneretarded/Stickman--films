"""Local ONNX speech, content-addressed cache, real segment durations."""
import hashlib
import json
from pathlib import Path
import wave
import numpy as np

VOICE_PROFILES={
 "Psychology & Human Behavior":("af_heart",1.02),"Relatable Comedy":("am_puck",1.08),
 "Money & Business":("am_fenrir",1.00),"History & Geopolitics":("bm_george",.97),
 "What-if & Survival":("am_adam",1.04),"Storytelling & Life Lessons":("af_bella",.97),
 "Science Explained":("af_sarah",1.02),"Self-improvement":("am_michael",1.02),
 "Technology & Cybersecurity":("bf_emma",1.02),"Mysteries & Scams":("bm_daniel",.96)}


def write_wav(path,samples,sr=24000):
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((np.clip(samples,-.999,.999)*32767).astype('<i2').tobytes())


def read_wav(path):
    with wave.open(str(path),"rb") as w:
        sr=w.getframerate();a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
        return a,sr


class Narrator:
    def __init__(self,model_dir):
        from kokoro_onnx import Kokoro
        import onnxruntime as ort
        self.model_dir=Path(model_dir)
        # Kokoro's default session can oversubscribe hosted CPUs. A bounded session
        # avoids three simultaneous workers competing for every available thread.
        opts=ort.SessionOptions();opts.intra_op_num_threads=2;opts.inter_op_num_threads=1
        session=ort.InferenceSession(str(self.model_dir/"kokoro-v1.0.int8.onnx"),sess_options=opts,providers=["CPUExecutionProvider"])
        self.engine=Kokoro.from_session(session,str(self.model_dir/"voices-v1.0.bin"))
        self.digest=hashlib.sha256((self.model_dir/"kokoro-v1.0.int8.onnx").read_bytes()).hexdigest()

    def speak(self,text,path,voice,speed):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        key=hashlib.sha256(json.dumps([text,voice,round(speed,4),self.digest,"kokoro-onnx-0.4.9"]).encode()).hexdigest()
        meta=path.with_suffix('.json')
        if path.exists() and meta.exists() and json.loads(meta.read_text()).get("key")==key:
            a,sr=read_wav(path)
        elif text.strip():
            a,sr=self.engine.create(text,voice=voice,speed=speed,lang="en-gb" if voice.startswith('b') else "en-us")
            # Short boundary margins prevent clipped starts and preserve phrase ends.
            a=np.concatenate([np.zeros(round(.08*sr)),a,np.zeros(round(.12*sr))]).astype(np.float32)
            write_wav(path,a,sr);meta.write_text(json.dumps({"key":key,"voice":voice,"speed":speed,"text":text,"seconds":len(a)/sr}))
        else:
            a=np.zeros(2400,dtype=np.float32);sr=24000;write_wav(path,a,sr)
        if text.strip() and (len(a)<1000 or float(np.sqrt(np.mean(a*a)))<.001):
            raise RuntimeError(f"Missing or silent narration: {path}")
        return a,sr


def voice_text(scene):
    return " ".join([scene.narration,*scene.dialogue]).strip()


def narrate(plan,model_dir,out,fps=60,rate_factor=1.):
    out=Path(out);n=Narrator(model_dir);voice,base_speed=VOICE_PROFILES[plan.niche]
    segments=[];offset=0
    for scene in plan.scenes:
        samples,sr=n.speak(voice_text(scene),out/f'{scene.id}.wav',voice,base_speed*rate_factor)
        audio_seconds=len(samples)/sr
        # Authored action-only sequences retain their directed timing.
        # They are not filler and do not inherit a fake narration duration.
        timing=scene.duration if not voice_text(scene) and scene.duration>0 else audio_seconds+scene.pause
        scene.duration=round(timing*fps)/fps
        if scene.duration>45:raise ValueError(f"Scene {scene.id} too long ({scene.duration:.1f}s); split its narration")
        scene.start=offset;scene.end=offset+scene.duration;offset=scene.end
        segments.append({"scene":scene.id,"start":scene.start,"audio_seconds":audio_seconds,"end":scene.end,"voice":voice,"speed":base_speed*rate_factor,"text":voice_text(scene),"path":str(out/f'{scene.id}.wav')})
    (out/'manifest.json').write_text(json.dumps(segments,indent=2))
    return segments
