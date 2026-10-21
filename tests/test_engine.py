import copy
import json
import math
from pathlib import Path
import pytest
from stickfilm.schema import Plan,Actor,Scene,minutes,slug,ACTIONS,NICHES
from stickfilm.motion import pose,trajectory,ik
from stickfilm.benchmark import benchmark_plan,benchmark_pose,travel
from stickfilm.render import draw_frame
from stickfilm.quality import motion_report

ROOT=Path(__file__).parents[1]

@pytest.mark.parametrize('bad',['0','-2','NaN','inf','1e999','eleven','11','.01'])
def test_reject_unsafe_duration(bad):
    with pytest.raises(ValueError):minutes(bad)

@pytest.mark.parametrize('value',[1.5,2.5,7.5])
def test_decimal_duration(value):assert minutes(str(value))==value


def test_plan_rejects_unknown_assets_and_unverified_claims():
    d=json.loads((ROOT/'examples/plans/00.json').read_text())
    d['scenes'][0]['actors'][0]['action']='execute_python'
    with pytest.raises(ValueError):Plan.model_validate(d)
    d=json.loads((ROOT/'examples/plans/00.json').read_text());d['factual_status']='unverified'
    with pytest.raises(ValueError):Plan.model_validate(d)


def test_duplicate_scene_ids_rejected():
    d=json.loads((ROOT/'examples/plans/00.json').read_text());d['scenes'][1]['id']=d['scenes'][0]['id']
    with pytest.raises(ValueError):Plan.model_validate(d)


def test_examples_are_distinct_and_structured():
    plans=[Plan.model_validate_json(p.read_text()) for p in sorted((ROOT/'examples/plans').glob('*.json'))]
    assert len(plans)==10
    assert {p.niche for p in plans}==set(NICHES)
    assert len({tuple(s.narration for s in p.scenes) for p in plans})==10
    assert len({tuple(s.actors[0].action for s in p.scenes) for p in plans})>=8
    assert all(p.provenance=='authored-example' for p in plans)


def test_acceleration_is_continuous_and_integrates_to_position():
    for t in [2,5,7,9,12,15]:
        x0,v0=travel(t-1e-5);x1,v1=travel(t+1e-5)
        assert abs(x1-x0)<.01
        assert abs(v1-v0)<.01
    for t in [2.5,6,8.5,10,14]:
        d0,_=travel(t-1e-4);d1,v=travel(t+1e-4)
        assert abs((d1-d0)/.0002-v)<.05
    assert travel(22)==(1360,0)


def test_benchmark_world_contacts_and_bone_lengths():
    p=benchmark_plan();r=motion_report(p,60,True)
    assert r['max_planted_foot_speed_px_s']<.001
    assert r['max_leg_reach_error_px']==0
    assert r['max_leg_length_error_px']<.01
    assert r['passes_contact_gate']
    assert r['max_camera_acceleration_design_units_s2']<300

@pytest.mark.parametrize('action',['walk','run','sprint'])
@pytest.mark.parametrize('direction',[-1,1])
def test_clips_have_stable_contacts(action,direction):
    p=benchmark_plan();s=p.scenes[0]
    s.duration=7;s.end=7;s.actors=[Actor(action=action,x=500,travel=600*direction,facing=direction)]
    r=motion_report(p)
    assert r['passes_contact_gate'],r

@pytest.mark.parametrize('action',ACTIONS)
def test_every_action_draws_without_missing_assets(action):
    scene=Scene(id='test',beat='hook',label='TEST',duration=4,actors=[Actor(action=action,travel=300 if action in ('run','walk') else 0)],narration='An original scene with a visible action.')
    for t in [.2,2,3.8]:
        surface,poses,_=draw_frame(scene,t,320,180)
        assert len(surface.get_data())==320*180*4
        assert all(math.isfinite(v) for p in poses for joint in p.joints.values() for v in joint)


def test_benchmark_keeps_object_after_pickup():
    assert benchmark_pose(20.2).pickup>.99
    assert benchmark_pose(21).pickup==1


def test_sanitized_output_name_cannot_escape_directory():
    assert '/' not in slug('../../hello $(touch file)')
    assert slug('Why Your Brain Hates Hard Things')=='why-your-brain-hates-hard-things'


def test_running_has_flight_and_stops_with_both_feet_down():
    flight=[]
    for i in range(9*60,12*60):
        p=benchmark_pose(i/60)
        if not any(p.contacts.values()):
            flight.append(p)
            assert all(p.joints['ankle_'+s][1]<p.ground for s in ('left','right'))
    assert flight, 'Running needs a flight interval, unlike walking'
    stopped=benchmark_pose(15.1)
    assert all(stopped.contacts.values())
    assert all(abs(stopped.joints['ankle_'+s][1]-stopped.ground)<.01 for s in ('left','right'))

@pytest.mark.parametrize('kind',__import__('stickfilm.schema',fromlist=['PROPS']).PROPS)
def test_prop_vocabulary_has_renderable_assets(kind):
    import cairocffi as cairo
    from stickfilm.drawing import draw_prop
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,320,240)
    context=cairo.Context(surface)
    draw_prop(context,kind,160,200,t=1,progress=.5,label=kind)
    assert len(surface.get_data())==320*240*4


def test_writer_rejects_truncation_but_allows_fictional_identifiers():
    from stickfilm.writer import validate_spoken_text
    validate_spoken_text("Milo filed ticket 1203, then took his sandwich to lunch.")
    with pytest.raises(ValueError,match="truncated"):
        validate_spoken_text("Milo arrived just after, s")
    with pytest.raises(ValueError,match="Unsourced"):
        validate_spoken_text("Research shows everyone needs this habit.")


def test_literal_direction_preserves_door_state_and_actor_identity():
    from stickfilm.direction import refine
    p=benchmark_plan();base=p.scenes[0]
    p.scenes=[]
    for i,words in enumerate(["Milo says the door won't open.","Ada pulls the handle, and the door swings open.","Milo stares at the now-open door."]):
        s=base.model_copy(deep=True);s.id=f's{i}';s.narration=words;s.prop='door'
        s.actors[0].action='sprint';p.scenes.append(s)
    refine(p)
    assert p.scenes[0].prop_motion=='still'
    assert p.scenes[0].actors[0].action=='think'
    assert p.scenes[1].prop_motion=='open'
    assert p.scenes[1].actors[0].character=='friend'
    assert p.scenes[2].prop_state=='open'


def test_comparison_requires_ten_results_and_prefers_explicit_repairs(tmp_path):
    from stickfilm.comparison import compare
    primary=tmp_path/'primary';primary.mkdir()
    for i,niche in enumerate(NICHES):
        path=primary/f'{i:02}';path.mkdir()
        (path/'plan.json').write_text(json.dumps({'niche':niche}))
        (path/'quality-report.json').write_text(json.dumps({'technical_pass':i!=6,'actual_seconds':75,'requested_seconds':75,'artistic_review':{'status':'pending human review'}}))
    with pytest.raises(RuntimeError):compare(tmp_path,tmp_path/'result.md',require_complete=True)
    repair=tmp_path/'repair';repair.mkdir()
    (repair/'plan.json').write_text(json.dumps({'niche':NICHES[6]}))
    (repair/'quality-report.json').write_text(json.dumps({'technical_pass':True,'actual_seconds':81.58,'requested_seconds':75,'artistic_review':{'status':'pending human review'}}))
    compare(tmp_path,tmp_path/'result.md',require_complete=True)
    data=json.loads((tmp_path/'result.json').read_text())
    assert len(data)==10 and all(x['technical_pass'] for x in data.values())
    assert data[NICHES[6]]['actual_seconds']==81.58


def test_measured_narration_does_not_collapse_authored_action_only_scene(tmp_path,monkeypatch):
    import numpy as np
    import stickfilm.voice as voice
    class SilentTestNarrator:
        def __init__(self,model_dir):pass
        def speak(self,text,path,identity,speed):
            samples=np.zeros(2400,dtype=np.float32);voice.write_wav(path,samples)
            return samples,24000
    monkeypatch.setattr(voice,'Narrator',SilentTestNarrator)
    p=benchmark_plan();p.scenes[0].duration=4
    segments=voice.narrate(p,'unused',tmp_path)
    assert p.scenes[0].duration==4
    assert segments[0]['audio_seconds']==.1
    assert segments[0]['end']==4
