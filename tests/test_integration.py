"""Real encode/decode/audio/QA test; deliberately independent of neural models."""
import json
import shutil
import pytest
from stickfilm.benchmark import benchmark_plan
from stickfilm.pipeline import produce

@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_actual_mp4_passes_measured_qa_and_cache(tmp_path):
    p=benchmark_plan();p.scenes[0].duration=8;p.scenes[0].end=8;p.requested_minutes=8/60
    video,report=produce(p,tmp_path,'unused',preset='draft',benchmark=True)
    assert video.is_file()
    assert report['technical_pass'],report['checks']
    assert abs(report['actual_seconds']-8)<.1
    assert (tmp_path/'contact-sheet.jpg').is_file()
    assert (tmp_path/'motion-preview.mp4').is_file()
    assert not report['artistic_review']['professional_quality_claimed']


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='FFmpeg required')
def test_motion_recovery_produces_real_video_that_passes_final_qa(monkeypatch,tmp_path):
    import numpy as np
    import stickfilm.pipeline as pipeline
    from stickfilm.schema import Scene,Actor
    from stickfilm.voice import write_wav
    from stickfilm.quality import motion_report,motion_passes
    p=benchmark_plan()
    p.requested_minutes=8/60
    p.scenes=[Scene(id='fast_walk',beat='hook',narration='She hurries toward the door.',pause=.1,
                    duration=.5,start=0,end=.5,actors=[Actor(action='walk',travel=-800)]),
              Scene(id='sitting',beat='payoff',narration='She sits and considers her next move.',pause=.1,
                    duration=7.5,start=.5,end=8,actors=[Actor(action='sit')])]
    assert not motion_passes(motion_report(p,24))
    def measured_voice(plan,models,out,fps,rate_factor=1):
        out.mkdir(parents=True,exist_ok=True);segments=[]
        for s in plan.scenes:
            seconds=s.duration-s.pause;t=np.arange(round(seconds*24000))/24000
            path=out/(s.id+'.wav');write_wav(path,.08*np.sin(2*np.pi*220*t))
            segments.append(dict(scene=s.id,start=s.start,end=s.end,audio_seconds=seconds,
                                 text=s.narration,path=str(path)))
        return segments
    monkeypatch.setattr(pipeline,'narrate',measured_voice)
    video,report=pipeline.produce(p,tmp_path,'unused',preset='draft')
    assert video.exists()
    assert p.scenes[0].actors[0].travel==-600
    assert p.scenes[0].actors[0].action=='walk'
    assert report['technical_pass'],report['checks']
    assert json.loads((tmp_path/'motion-repairs.json').read_text())['all_gates_pass']
