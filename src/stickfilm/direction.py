"""Small semantic correction pass, never a substitute for a general director.

The model writes the story. This pass keeps a few literal on-screen events from
contradicting that narration. Complex actions still require authored clips.
"""
import re

def refine(plan):
    door_open=False
    for scene in plan.scenes:
        words=(scene.narration+' '+' '.join(scene.dialogue)).lower()
        actor=scene.actors[0]
        if re.match(r'^ada\b',words):
            actor.character='friend'
            for supporting in scene.actors[1:]:
                if supporting.character=='friend':supporting.character='hero'
        if actor.action in ('walk','run','sprint','stairs') and not re.search(r'\b(walk\w*|run\w*|sprint\w*|race\w*|rush\w*|approach\w*|chase\w*|step\w*)\b',words):
            actor.action='think';actor.travel=0
        if re.search(r'\b(knocks?|slams? (?:his |her |a )?fist)\b',words):
            actor.action='knock';actor.travel=0;actor.x=940
        elif 'laugh' in words:
            actor.action='happy';actor.travel=0
        elif 'eyes wide' in words:
            actor.action='surprise';actor.travel=0
        if scene.prop=='door':
            if re.search(r'door.{0,25}(?:closes|slams shut)',words):door_open=False
            scene.prop_state='open' if door_open else 'closed'
            if not door_open and re.search(r'door (?:gently |slowly |finally )?(?:swings? open|opens?\b)|now-open door',words):
                scene.prop_motion='open';door_open=True
    return plan
