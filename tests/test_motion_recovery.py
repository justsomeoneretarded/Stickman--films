import json
from pathlib import Path
import pytest
from stickfilm.benchmark import benchmark_plan
from stickfilm.schema import ACTIONS,Actor,Scene,ActingBeat
from stickfilm.quality import motion_report,motion_passes
from stickfilm.motion import pose
from stickfilm.motion_recovery import prepare_motion


@pytest.mark.parametrize('action',ACTIONS)
def test_supported_motion_across_timing_and_staging(action,tmp_path):
    # Pairwise coverage of signed travel, scale planes, placement, camera,
    # setting, frame rate and clip length, including the production maximum.
    cases=[(.5,-800,.65,-1000,24,'forest','wide'),
           (2,800,1.15,4000,60,'office','follow'),
           (9,350,1,520,60,'bedroom','close-up'),
           (30,-350,1.15,940,24,'classroom','pan'),
           (45,0,.65,500,60,'city','reveal')]
    p=benchmark_plan()
    for duration,travel,depth,x,fps,env,camera in cases:
        scene=Scene(id='matrix',beat='hook',duration=duration,end=duration,
                    environment=env,camera=camera,
                    actors=[Actor(action=action,travel=travel,depth=depth,x=x,facing=-1),
                            Actor(action='stand',depth=.87,x=1200)],
                    acting=[ActingBeat(at=.4,action='point',emotion='frustrated')])
        candidate=p.model_copy(update={'scenes':[scene]})
        report=prepare_motion(candidate,tmp_path/str(duration),fps)
        assert motion_passes(report),(action,cases,report)
        assert candidate.scenes[0].actors[0].action==action
        assert candidate.scenes[0].duration==duration
        assert candidate.scenes[0].environment==env


@pytest.mark.parametrize('action',['jump','fall'])
def test_aerial_clips_travel_only_in_flight_and_land_at_destination(action):
    actor=Actor(action=action,travel=350)
    for t in [0,1,2]:
        p=pose(actor,t,10)
        assert p.root[0]==actor.x
        assert all(p.contacts.values())
    middle=pose(actor,4.5,10)
    assert not any(middle.contacts.values())
    assert all(middle.joints['ankle_'+side][1]<middle.ground for side in ('left','right'))
    for t in [7.3,9,10]:
        p=pose(actor,t,10)
        assert p.root[0]==actor.x+350
        assert all(p.contacts.values())


def test_stairs_gain_height_without_moving_stance_anchors():
    actor=Actor(action='stairs',travel=350)
    assert pose(actor,9,9).root[1]<pose(actor,0,9).root[1]-30


def test_stationary_travel_is_normalized_and_audited(tmp_path):
    p=benchmark_plan();s=p.scenes[0]
    s.actors=[Actor(action='think',travel=350)];s.duration=4;s.end=4
    original=s.model_dump();prepare_motion(p,tmp_path)
    actual=s.model_dump();actual['actors'][0]['travel']=0
    assert p.scenes[0].model_dump()==actual
    assert s.model_dump()==original  # replacement does not mutate the source shot
    audit=json.loads((tmp_path/'motion-repairs.json').read_text())
    assert audit['all_gates_pass']
    assert audit['repairs'][0]['changes'][0]['before']==350
    assert (tmp_path/'motion-original-plan.json').exists()


def fault_measure(monkeypatch,always_fail=False):
    import stickfilm.motion_recovery as recovery
    real=motion_report
    def measure(plan,*args):
        result=real(plan,*args)
        if always_fail or any(abs(a.travel)>200 for s in plan.scenes for a in s.actors):
            result['passes_contact_gate']=False
        return result
    monkeypatch.setattr(recovery,'motion_report',measure)


def test_real_traversal_failure_retries_only_affected_scene(tmp_path):
    p=benchmark_plan();s=p.scenes[0]
    s.duration=.5;s.end=.5;s.actors=[Actor(action='walk',travel=-800)]
    good=s.model_copy(deep=True,update={'id':'good','actors':[Actor(action='think')],'start':4,'end':8})
    p.scenes.append(good);original=s.model_dump();unchanged=good.model_dump()
    assert not motion_passes(motion_report(p,24))
    assert motion_passes(prepare_motion(p,tmp_path,24))
    assert p.scenes[0].actors[0].travel==-600
    expected=original;expected['actors'][0]['travel']=-600
    assert p.scenes[0].model_dump()==expected
    assert p.scenes[1].model_dump()==unchanged
    audit=json.loads((tmp_path/'motion-repairs.json').read_text())
    assert len(audit['repairs'][0]['attempts'])==1
    assert audit['repairs'][0]['after']['passes_contact_gate']


def test_unrepairable_failure_keeps_gate_and_diagnostics(monkeypatch,tmp_path):
    fault_measure(monkeypatch,always_fail=True)
    p=benchmark_plan();p.scenes[0].actors=[Actor(action='walk',travel=600)]
    original=p.model_dump()
    with pytest.raises(RuntimeError,match='before|Rendering has not started'):
        prepare_motion(p,tmp_path)
    assert p.model_dump()==original
    audit=json.loads((tmp_path/'motion-repairs.json').read_text())
    assert not audit['all_gates_pass']
    assert audit['unresolved_scenes']==[p.scenes[0].id]
    assert len(audit['repairs'][0]['attempts'])==3


def test_failed_preflight_never_starts_render_or_mix(monkeypatch,tmp_path):
    import stickfilm.pipeline as pipeline
    fault_measure(monkeypatch,always_fail=True)
    def forbidden(*args,**kwargs):pytest.fail('Rendering/mixing must not start after failed motion recovery')
    monkeypatch.setattr(pipeline,'sound_mix',forbidden)
    monkeypatch.setattr(pipeline,'render_scene',forbidden)
    with pytest.raises(RuntimeError,match='Rendering has not started'):
        pipeline.produce(benchmark_plan(),tmp_path,'unused',preset='draft',benchmark=True)
    assert json.loads((tmp_path/'failure.json').read_text())['type']=='RuntimeError'


def test_mixed_plan_must_pass_both_motion_engines():
    from stickfilm.schema import Plan
    root=Path(__file__).parents[1]
    p=Plan.model_validate_json((root/'episodes/psychology.json').read_text())
    scene=p.scenes[0].model_copy(deep=True)
    scene.cinema.items=[]
    for performer in scene.cinema.performers:
        first=performer.keys[0]
        performer.keys=[first.model_copy(update={'at':0}),first.model_copy(update={'at':1})]
    legacy=Scene(id='legacy',beat='setup',duration=2,end=2,actors=[Actor(action='think')])
    p.scenes=[scene,legacy]
    report=motion_report(p)
    assert report['passes_contact_gate']
    assert not report['passes_direction_gate']
    assert not motion_passes(report)
