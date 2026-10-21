"""Regressions for independent productions and directed, measured animation."""
import math
from pathlib import Path
import yaml
from stickfilm.schema import Plan
from stickfilm.motion import scene_poses
from stickfilm.render import draw_frame

ROOT=Path(__file__).parents[1]

def test_independent_workflows_do_not_share_concurrency_or_creative_inputs():
    workflows=[yaml.safe_load((ROOT/f'.github/workflows/{key}.yml').read_text()) for key in ('psychology','what-if')]
    assert workflows[0]['concurrency']['group']!=workflows[1]['concurrency']['group']
    jobs=[next(iter(w['jobs'].values())) for w in workflows]
    assert all('needs' not in job for job in jobs)
    assert jobs[0]['with']['niche']!=jobs[1]['with']['niche']
    assert jobs[0]['with']['key']!=jobs[1]['with']['key']
    assert all(job['with']['title']=='${{ inputs.video_title }}' and job['with']['brief']=='${{ inputs.video_description }}' for job in jobs)

def test_each_authored_film_has_its_own_complete_story_and_drawable_direction():
    plans=[Plan.model_validate_json((ROOT/f'episodes/{key}.json').read_text()) for key in ('psychology','what-if')]
    assert plans[0].title!=plans[1].title and plans[0].brief!=plans[1].brief
    assert not set(s.narration for s in plans[0].scenes)&set(s.narration for s in plans[1].scenes)
    assert not set(s.setpiece for s in plans[0].scenes)&set(s.setpiece for s in plans[1].scenes)
    for plan in plans:
        assert plan.requested_minutes==5
        assert 750<sum(len(s.narration.split()) for s in plan.scenes)<1100
        for s in plan.scenes:
            s.duration=15
            draw_frame(s,7,320,180)
            for t in (0,4.9,5.3,7.0,11.3,14.8):
                for p in scene_poses(s,t):
                    for side in ('left','right'):
                        j=p.joints
                        assert abs(math.dist(j['hip_'+side],j['knee_'+side])-66)<.01
                        assert abs(math.dist(j['knee_'+side],j['ankle_'+side])-66)<.01
                        assert abs(math.dist(j['shoulders'],j['elbow_'+side])-55)<.01
                        assert abs(math.dist(j['elbow_'+side],j['wrist_'+side])-56)<.01
