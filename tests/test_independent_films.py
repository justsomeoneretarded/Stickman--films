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
    spoken=[set(s.narration for s in p.scenes if s.narration) for p in plans]
    assert not spoken[0]&spoken[1]
    from stickfilm.cinema import report,actor_state
    for plan in plans:
        assert plan.requested_minutes==5
        assert len(plan.scenes)==50
        assert sum(s.directed_seconds for s in plan.scenes)==300
        assert sum(not s.narration for s in plan.scenes)>=15
        measured=report(plan)
        assert measured['passes_direction_gate']
        assert not measured['contact_gate_applicable']
        assert measured['largest_actor_travel']>=900
        for s in plan.scenes:
            assert s.cinema is not None
            s.duration=s.directed_seconds
            draw_frame(s,3,320,180)
            for actor in s.cinema.performers:
                for u in (0,.3,.6,1):
                    v=actor_state(actor,u,u*s.duration)
                    assert all(math.isfinite(n) for k in ('hip','neck','head','lf','rf','lw','rw') for n in v['rig'][k])
