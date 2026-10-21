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
