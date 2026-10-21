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
