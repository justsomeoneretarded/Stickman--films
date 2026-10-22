from pathlib import Path
import math
import pytest
from stickfilm.cinema_schema import Performer,Cinema
from stickfilm.cinema import actor_state,report
from stickfilm.schema import Plan
from stickfilm import voice

ROOT=Path(__file__).parents[1]

def test_cinema_rejects_unordered_timeline():
    with pytest.raises(ValueError):
        Performer(name='Noah',look='witness',keys=[dict(at=0,x=200),dict(at=0,x=800)])

def test_visual_timing_survives_silent_or_short_speech(tmp_path,monkeypatch):
    p=Plan.model_validate_json((ROOT/'episodes/psychology.json').read_text());p.scenes=p.scenes[:2]
    class Stub:
        def __init__(self,*a):pass
        def speak(self,*a):
            import numpy as np
            return np.zeros(24000),24000
    monkeypatch.setattr(voice,'Narrator',Stub)
    segments=voice.narrate(p,'unused',tmp_path)
    assert [s.duration for s in p.scenes]==[6,6]
    assert segments[-1]['end']==12

def test_cinematic_direction_does_not_claim_legacy_contact_qualification():
    p=Plan.model_validate_json((ROOT/'episodes/psychology.json').read_text())
    r=report(p)
    assert r['passes_direction_gate'] and r['contact_gate_applicable'] is False
    assert 'passes_contact_gate' not in r
    p.scenes=p.scenes[:1];s=p.scenes[0];s.cinema.items=[]
    for a in s.cinema.performers:
        a.keys[1]=a.keys[0].model_copy(update={'at':1})
    assert not report(p)['passes_direction_gate']

def test_large_crossings_are_continuous():
    p=Plan.model_validate_json((ROOT/'episodes/psychology.json').read_text());s=p.scenes[22];a=s.cinema.performers[0]
    positions=[actor_state(a,t/120,t/120*6)['x'] for t in range(121)]
    assert max(positions)-min(positions)>900
    assert max(abs(b-a) for a,b in zip(positions,positions[1:]))<15
