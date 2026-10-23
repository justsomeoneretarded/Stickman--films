"""Resumable production: plan → measured voice → scene cache → mix → QA."""
from __future__ import annotations
import json
import os
from pathlib import Path
import resource
import shutil
import time
import traceback
from .schema import Plan,slug
from .render import PRESETS,render_scene,assemble
from .voice import narrate,write_wav
from .audio import sound_mix
from .quality import assess,motion_report
from .resources import Monitor
import numpy as np


def produce(plan: Plan,out,model_dir,preset="production",benchmark=False):
    started=time.monotonic();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    w,h,fps=PRESETS[preset];requested=plan.requested_minutes*60
    if shutil.disk_usage(out).free<1024**3:raise RuntimeError("Need at least 1 GiB of free disk")
    monitor=Monitor(out)
    try:
        if benchmark:
            (out/'voice').mkdir(exist_ok=True)
            silent=out/'voice'/'benchmark.wav';write_wav(silent,np.zeros(round(plan.scenes[0].duration*24000)))
            segments=[{"scene":"benchmark","start":0,"audio_seconds":plan.scenes[0].duration,"end":plan.scenes[0].duration,"voice":"none — action-only benchmark","speed":1,"text":"","path":str(silent)}]
        else:
            segments=narrate(plan,model_dir,out/'voice',fps)
            measured=plan.scenes[-1].end
            # A modest delivery change is synthesis, never audio stretching. If
            # content length is genuinely wrong, fail and request a script rewrite.
            if not .90*requested<=measured<=1.1*requested:
                ratio=measured/requested
                factor=max(.92,min(1.12,ratio))
                segments=narrate(plan,model_dir,out/'voice',fps,rate_factor=factor)
            measured=plan.scenes[-1].end
            if not .75*requested<=measured<=1.25*requested:
                (out/'plan.json').write_text(plan.model_dump_json(indent=2))
                raise ValueError(f"Measured narration timeline {measured:.1f}s is outside {requested*.75:.1f}–{requested*1.25:.1f}s. Rewrite the script with {requested/measured:.2f}× its content. No filler or audio stretching was applied.")
        (out/'plan.json').write_text(plan.model_dump_json(indent=2))
        # Preserve measured segment information even when a later scene fails.
        (out/'narration-manifest.json').write_text(json.dumps(segments,indent=2))
        motion=motion_report(plan,fps,benchmark)
        (out/'motion-preflight.json').write_text(json.dumps(motion,indent=2))
        if not motion.get('passes_direction_gate',motion.get('passes_contact_gate',False)):
            failed=[]
            for scene in plan.scenes:
                result=motion_report(plan.model_copy(update={'scenes':[scene]}),fps,benchmark)
                if not result.get('passes_direction_gate',result.get('passes_contact_gate',False)):
                    failed.append(scene.id)
            raise RuntimeError(f'Motion preflight failed in {", ".join(failed)}; inspect {out}/motion-preflight.json. Rendering has not started.')
        audio=sound_mix(plan,segments,out,benchmark)
        files=[];times=[]
        for s in plan.scenes:
            path=out/'scenes'/f'{s.id}.mp4'
            print(f'Rendering {s.id}: {s.duration:.2f}s at {w}x{h}/{fps}',flush=True)
            times.append(render_scene(s,path,w,h,fps,benchmark=benchmark));files.append(path)
        final=out/(slug(plan.title)+'.mp4');assemble(files,audio,final)
        report=assess(final,plan,out,w,h,fps,segments,benchmark)
        stats={"elapsed_seconds":time.monotonic()-started,"peak_process_ram_mib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
            "disk_free_gib":shutil.disk_usage(out).free/(1024**3),"cpu_count":os.cpu_count(),"scenes":times,"output":str(final),
            "note":"RAM measures Python process; FFmpeg child peak is not included. Actions monthly minutes must be checked in account billing."}
        (out/'resources.json').write_text(json.dumps(stats,indent=2))
        if not report['technical_pass']:
            failed=', '.join(k for k,v in report['checks'].items() if not v)
            raise RuntimeError(f'Technical QA failed ({failed}); inspect {out}/quality-report.json')
        (out/'failure.json').unlink(missing_ok=True)
        return final,report
    except BaseException as e:
        (out/'failure.json').write_text(json.dumps({"type":type(e).__name__,"message":str(e),"traceback":traceback.format_exc()},indent=2))
        raise
    finally:
        monitor.stop()
