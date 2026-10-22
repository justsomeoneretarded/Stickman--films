"""Genuine local-model writer. Fixed examples are never a title fallback."""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import re
from difflib import SequenceMatcher
from pydantic import BaseModel,Field
from typing import Literal
from .schema import Plan,Scene,Actor,Cue,NICHES,ENVIRONMENTS,ACTIONS,CAMERAS,Source,PROPS

KEYWORDS=[['brain','psychology','procrastin','behavior','dopamine'],['funny','comedy','awkward','queue'],['money','business','cash','bank','finance'],['history','war','border','geopolit'],['surviv','what if','what-if','island'],['story','lesson','friendship','kindness'],['science','gravity','physics','space'],['habit','improve','routine','discipline'],['cyber','password','technology','computer'],['mystery','scam','fraud','prize']]


def detect(title,brief):
    combined=(title+' '+brief).lower()
    scores=[sum(combined.count(k) for k in words) for words in KEYWORDS]
    return NICHES[max(range(10),key=lambda i:scores[i])] if max(scores)>0 else NICHES[5]

class Outline(BaseModel):
    hook: str = Field(min_length=10,max_length=180)
    conflict: str = Field(min_length=10,max_length=180)
    discovery: str = Field(min_length=10,max_length=180)
    ending: str = Field(min_length=10,max_length=180)

class Shot(BaseModel):
    narration: str = Field(min_length=30,max_length=450)
    label: str = Field(max_length=50)
    environment: Literal[tuple(ENVIRONMENTS)]
    action: Literal[tuple(ACTIONS)]
    prop: Literal[tuple(PROPS)]
    prop_motion: Literal["still","open","reveal","grow"] = "still"
    camera: Literal[tuple(CAMERAS)]
    mood: Literal['curious','comic','tense','warm','wonder','silence']

class Batch(BaseModel):
    scenes: list[Shot] = Field(min_length=1,max_length=8)


class SceneEvent(BaseModel):
    event: str = Field(min_length=15,max_length=180)

class SceneOutline(BaseModel):
    beats: list[SceneEvent] = Field(min_length=6,max_length=60)


def repeated_passages(texts,previous=()):
    """Use the same final gate while rejecting bad batches before they accumulate."""
    accepted=list(previous);bad=[]
    for i,text in enumerate(texts):
        words=text.lower().split()
        matches=[j for j,earlier in enumerate(accepted) if max(SequenceMatcher(None,words,earlier.lower().split()).ratio(),SequenceMatcher(None,earlier.lower().split(),words).ratio())>.80]
        if matches:bad.append((i,matches[0]))
        accepted.append(text)
    return bad


def batch_problem(batch,previous,size,sources):
    if len(batch.scenes)!=size:return f'Expected exactly {size} scenes, received {len(batch.scenes)}.'
    for i,shot in enumerate(batch.scenes):
        if len(shot.narration.split())<8:return f'Scene {i+1} has fewer than eight words.'
        try:validate_spoken_text(shot.narration,sources)
        except ValueError as e:return f'Scene {i+1}: {e}'
    repeats=repeated_passages([s.narration for s in batch.scenes],[s.narration for s in previous])
    if repeats:
        return 'Repeated narration: '+ '; '.join(f'candidate {i+1} repeats accepted/candidate scene {j+1}' for i,j in repeats)+'. Advance the assigned events instead of restarting the story.'
    return None


def story_phase(index,count):
    fraction=index/max(1,count-1)
    if fraction<.12:return 'HOOK AND SETUP: establish the problem and stakes; do not resolve it.'
    if fraction<.32:return 'ESCALATION: show a new obstacle, action and concrete cost; no final resolution.'
    if fraction<.55:return 'COMPLICATION: worsen the problem through a new event; no final resolution.'
    if fraction<.72:return 'DISCOVERY: consequences change the protagonist’s understanding; no final resolution.'
    if fraction<.86:return 'DECISIVE ACTION: act on the discovery and face its immediate cost.'
    return 'PAYOFF: resolve the conflict through visible change; reserve the final ending for the final scene.'


def generate(title,brief,minutes,niche,model_dir,out,seed=42,sources=None,word_factor=1.):
    from llama_cpp import Llama,LlamaGrammar
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    sources=sources or []
    from .models import ROOT
    filename=json.loads((ROOT/'config/models.json').read_text())['writer']['file']
    model=Path(os.getenv('WRITER_MODEL',str(Path(model_dir)/filename)))
    if not model.exists():raise FileNotFoundError('Missing local writer model; run stickfilm models --local. Alternatively pass --plan with a reviewed JSON plan.')
    llm=Llama(model_path=str(model),n_ctx=8192,n_threads=2,n_batch=256,seed=seed,verbose=False,chat_format='chatml')

    niche=detect(title,brief) if niche=='Auto-detect' else niche
    count=max(6,math.ceil(minutes*6))
    words_per_scene=max(13,round(minutes*155*word_factor/count))
    allshots=[];raws=[]
    outline_grammar=LlamaGrammar.from_json_schema(json.dumps(Outline.model_json_schema()),verbose=False)
    print('Writing original story outline with the local model',flush=True)
    outline_result=llm.create_chat_completion(messages=[{'role':'system','content':'You write original fictional stories. Return JSON with hook, conflict, discovery, ending. Each field is ONE complete short sentence of at most 20 words. Follow the brief directly; do not add an unrelated mystery or extraneous characters. Every story needs a concrete resolved ending with a visible change. No repeated failed attempts as an ending. No factual claims without source notes.'},{'role':'user','content':f'Title: {title}. Brief: {brief}. Niche: {niche}. Create a short story arc using the characters named in the brief; use Milo and Ada only if no names are specified. Source context: {json.dumps(sources)}'}],grammar=outline_grammar,temperature=.55,max_tokens=900,seed=seed,repeat_penalty=1.12)
    outline=Outline.model_validate_json(outline_result['choices'][0]['message']['content'])
    (out/'writer-outline.json').write_text(outline.model_dump_json(indent=2))
    if sources:
        policy='Use ONLY the supplied source notes for factual claims. Do not add dates, statistics, diagnoses or guarantees. The characters and framing story may be invented.'
    else:
        policy='Write explicitly FICTIONAL entertainment about imaginary people. No assertions about neuroscience, medicine, actual history, actual statistics, real people, or real companies. Do not pretend to answer factual questions without sources.'
    spine_schema=SceneOutline.model_json_schema()
    spine_schema['properties']['beats'].update(minItems=count,maxItems=count)
    spine_grammar=LlamaGrammar.from_json_schema(json.dumps(spine_schema),verbose=False)
    spine=None
    planning_feedback=''
    for attempt in range(2):
        print(f'Planning {count} distinct story events (attempt {attempt+1}/2)',flush=True)
        spine_result=llm.create_chat_completion(messages=[
            {'role':'system','content':'Plan one continuous original story, not several retellings. Return JSON beats, exactly one short physical event per scene. Every event advances time or changes the situation. Never repeat an earlier event or restart the story. Follow the supplied act assignments. Do not put the final resolution before the last act. Keep each event under 22 words.'},
            {'role':'user','content':f'Title: {title}. Brief: {brief}. Arc: {outline.model_dump_json()}. Return exactly {count} sequential events. Assignments: '+ '\n'.join(f'{i+1}: {story_phase(i,count)}' for i in range(count))+planning_feedback}
        ],grammar=spine_grammar,temperature=.6,max_tokens=max(1800,count*55),seed=seed+100+attempt,repeat_penalty=1.15)
        try:
            candidate=SceneOutline.model_validate_json(spine_result['choices'][0]['message']['content'])
            repeats=repeated_passages([b.event for b in candidate.beats])
            if len(candidate.beats)!=count or repeats:raise ValueError(f'Expected {count} distinct events; repeats={repeats}')
            spine=candidate;break
        except ValueError as error:
            planning_feedback=f' Previous attempt rejected: {error}. Rewrite a chronological, nonrepeating plan.'
    if spine is None:raise ValueError('Local writer could not plan distinct story events after two attempts.')
    (out/'writer-scene-outline.json').write_text(spine.model_dump_json(indent=2))
    system=f'''You write original short animated stories. Output valid JSON, nothing else.
Niche: {niche}. Title: {title}. Brief: {brief}.
You are writing ONLY one assigned segment of a longer screenplay. Do not compress the entire arc into this batch. The user supplies exact events and act assignments; follow those events in order. Only the final batch may deliver the ending.
{policy}
The story must satisfy the brief within those limits. Start with an intriguing concrete situation, build a conflict, discover something, end with a payoff. No generic introduction, no presenter, no references to watching a video.
Each scene has narration (about {words_per_scene} words), a brief editorial label (max 50 characters), environment, character action, prop, camera, and music mood.
Write narration that can be spoken naturally, not stage directions. Each narration must be a COMPLETE short sentence or two, ending in punctuation. Stay close to the requested word count. Do not copy the outline phrasing or include every detail of it. Every shot should use its action and prop to show what is being said. Keep the character names requested in the brief. Use Milo and Ada only when the brief names nobody. Avoid impossible actions: a finite procedural animation engine executes these scenes.
Use prop_motion=open when a door actually opens; otherwise still. Choose different actions, settings and cameras when useful. Do not repeat scenes or sentences. No subtitles or JSON examples inside narration.
Overall story arc (context only, NOT the plot of every batch): {outline.model_dump_json()}
Source notes: {json.dumps(sources) if sources else 'NONE — fiction only'}'''
    for offset in range(0,count,6):
        size=min(6,count-offset)
        print(f'Writing scenes {offset+1}–{offset+size} of {count}',flush=True)
        schema=Batch.model_json_schema();schema['properties']['scenes']['minItems']=size;schema['properties']['scenes']['maxItems']=size
        schema['$defs']['Shot']['properties']['narration']['maxLength']=min(450,words_per_scene*8+50)
        schema['$defs']['Shot']['properties']['narration']['minLength']=max(30,words_per_scene*4)
        grammar=LlamaGrammar.from_json_schema(json.dumps(schema),verbose=False)
        # Keep a numbered ledger of ALL accepted events, rather than only a tail
        # of prose that lets the model forget and repeat the opening/ending.
        ledger='\n'.join(f'{i+1}: {s.narration[:150]}' for i,s in enumerate(allshots))
        assignments='\n'.join(f'{i+1}: {spine.beats[i].event} [{story_phase(i,count)}]' for i in range(offset,offset+size))
        prompt=f'Write exactly {size} scenes, numbered {offset+1} through {offset+size} of {count}. Write ONLY these assigned events in this order:\n{assignments}\n'
        prompt+='Do not restart the story, revisit a completed event, or repeat any prior narration. '
        if offset+size==count:prompt+=f'The final scene must finish this ending: {outline.ending}. '
        else:prompt+='This is not the final batch. Do not deliver the ending yet. '
        prompt+=f'Already completed events (do not retell):\n{ledger or "None yet."}'
        feedback='';batch=None
        for attempt in range(3):
            result=llm.create_chat_completion(messages=[{'role':'system','content':system},{'role':'user','content':prompt+feedback}],grammar=grammar,temperature=.65+attempt*.08,top_p=.9,max_tokens=2600,seed=seed+offset+attempt*1000,repeat_penalty=1.15,frequency_penalty=.2)
            raw=result['choices'][0]['message']['content'];raws.append(raw)
            (out/'writer-raw.json').write_text(json.dumps(raws,indent=2))
            try:
                candidate=Batch.model_validate_json(raw)
                problem=batch_problem(candidate,allshots,size,sources)
            except ValueError as error:
                problem=str(error);candidate=None
            if problem is None:batch=candidate;break
            print(f'Rewriting scenes {offset+1}–{offset+size}: {problem} (attempt {attempt+1}/3)',flush=True)
            feedback='\nYour previous attempt was REJECTED: '+problem+' Rewrite this batch with fresh, complete narration for its assigned events. Do not paraphrase a completed event.'
        if batch is None:
            raise ValueError(f'Writer could not produce a valid nonrepeating batch {offset+1}–{offset+size} after three attempts: {problem}. Diagnostics preserved.')
        allshots.extend(batch.scenes)
        (out/'writer-accepted.json').write_text(json.dumps([s.model_dump() for s in allshots],indent=2))
    scenes=[]
    for i,s in enumerate(allshots):
        if len(s.narration.split())<8:raise ValueError('Local writer returned an empty/short narration; use a reviewed plan')
        validate_spoken_text(s.narration,sources)
        action=s.action
        beat='hook' if i==0 else 'setup' if i==1 else 'payoff' if i==len(allshots)-1 else 'conflict' if i<len(allshots)/2 else 'discovery'
        actor=Actor(action=action,x=940 if action in ('reach','pickup','inspect') else 480,travel=350 if action in ('walk','stairs') else 520 if action in ('run','sprint') else 0)
        actors=[actor]
        if 'ada' in s.narration.lower():actors.append(Actor(character='friend',action='point' if beat=='discovery' else 'think' if beat!='payoff' else 'happy',x=1220,depth=.87,facing=-1))
        scenes.append(Scene(id=f's{i+1:03}',beat=beat,narration=s.narration,label=s.label[:65],environment=s.environment,actors=actors,prop=s.prop,camera=s.camera,music=s.mood,prop_motion=s.prop_motion,
            transition='dissolve' if i%4==0 else 'cut',cues=[Cue(at=.5,kind='click' if s.prop=='phone' else 'chime',gain=.15)]))
    repeats=repeated_passages([s.narration for s in scenes])
    if repeats:
        later,earlier=repeats[0]
        raise ValueError(f'Writer repeated substantially the same narration in {scenes[earlier].id}/{scenes[later].id}; diagnostics preserved')
    if not sources:scenes[0].label='FICTIONAL STORY / '+scenes[0].label[:45]
    p=Plan(title=title,brief=brief,niche=niche,requested_minutes=minutes,seed=seed,provenance='local-model',factual_status='source-grounded' if sources else 'fiction',sources=sources,scenes=scenes)
    from .direction import refine
    p=refine(p)
    (out/'generated-plan.json').write_text(p.model_dump_json(indent=2))
    del llm
    return p


def validate_spoken_text(text,sources=None):
    if not re.search(r"[.!?][\"'”’]?$",text.strip()):
        raise ValueError("Writer returned truncated or unfinished narration; raw output preserved. Use a reviewed plan or rewrite with shorter complete sentences.")
    if not sources and re.search(r"\b(research (shows|proves)|studies (show|prove)|scientists (found|discovered)|\d+\s*% of (people|patients|adults))\b",text,re.I):
        raise ValueError("Unsourced factual claim in local script; supply reviewed source notes")
