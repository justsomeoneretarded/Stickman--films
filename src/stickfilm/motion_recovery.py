"""Bounded, audited motion repairs before expensive frame rendering.

Repairs change movement parameters, never narration, action identity, timing,
quality thresholds, or cinematic direction. Unsupported failures stay failures.
"""
import json
from pathlib import Path
from .quality import motion_report,motion_passes

TRAVELLING_ACTIONS={'walk','run','sprint','stairs','jump','fall'}


def prepare_motion(plan,out,fps=60,benchmark=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    original=plan.model_dump_json(indent=2)
    repairs=[];unresolved=[]
    for index,scene in enumerate(plan.scenes):
        candidate=scene.model_copy(deep=True)
        changes=[];attempts=[]
        if not benchmark and candidate.cinema is None:
            for actor_index,actor in enumerate(candidate.actors):
                if actor.travel and actor.action not in TRAVELLING_ACTIONS:
                    changes.append({'actor':actor_index,'field':'travel','before':actor.travel,'after':0,
                                    'reason':'Stationary acting cannot translate planted feet.'})
                    actor.travel=0
        def measure(shot):
            return motion_report(plan.model_copy(update={'scenes':[shot]}),fps,benchmark)
        before=measure(scene)
        result=measure(candidate) if changes else before
        # Try a few smaller traversals in the same action. Always start from
        # the original candidate, avoiding cumulative or unbounded retries.
        if not motion_passes(result) and candidate.cinema is None and not benchmark:
            for factor in (.75,.5,.25):
                retry=candidate.model_copy(deep=True)
                adjusted=[]
                for actor_index,actor in enumerate(retry.actors):
                    if actor.travel and actor.action in TRAVELLING_ACTIONS:
                        old=actor.travel;actor.travel=old*factor
                        adjusted.append({'actor':actor_index,'field':'travel','before':old,'after':actor.travel,
                                         'reason':'Reduce traversal while preserving action and timing.'})
                if not adjusted:break
                retry_result=measure(retry)
                attempts.append({'factor':factor,'changes':adjusted,'motion':retry_result})
                if motion_passes(retry_result):
                    candidate=retry;result=retry_result;changes+=adjusted;break
        if not motion_passes(result):unresolved.append(scene.id)
        elif changes:plan.scenes[index]=candidate
        if changes or attempts or not motion_passes(result):
            repairs.append({'scene':scene.id,'resolved':motion_passes(result),'changes':changes,
                            'before':before,'attempts':attempts,'after':result})
    report=motion_report(plan,fps,benchmark)
    (out/'motion-preflight.json').write_text(json.dumps(report,indent=2))
    (out/'motion-repairs.json').write_text(json.dumps({'repairs':repairs,'unresolved_scenes':unresolved,
        'all_gates_pass':motion_passes(report),'policy':'Preserve action, story and timing; never bypass QA.'},indent=2))
    if repairs:(out/'motion-original-plan.json').write_text(original)
    (out/'plan.json').write_text(plan.model_dump_json(indent=2))
    if unresolved or not motion_passes(report):
        raise RuntimeError(f'Motion preflight failed after bounded repair in {", ".join(unresolved) or "combined plan"}; '
                           f'inspect {out}/motion-repairs.json. Rendering has not started.')
    for repair in repairs:
        print(f'Automatically repaired motion in {repair["scene"]}; verified at {fps} FPS',flush=True)
    return report
