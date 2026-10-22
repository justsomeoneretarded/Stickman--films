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
    system=f'''You write original short animated stories. Output valid JSON, nothing else.
Niche: {niche}. Title: {title}. Brief: {brief}.
{policy}
The story must satisfy the brief within those limits. Start with an intriguing concrete situation, build a conflict, discover something, end with a payoff. No generic introduction, no presenter, no references to watching a video.
Each scene has narration (about {words_per_scene} words), a brief editorial label (max 50 characters), environment, character action, prop, camera, and music mood.
Write narration that can be spoken naturally, not stage directions. Each narration must be a COMPLETE short sentence or two, ending in punctuation. Stay close to the requested word count. Do not copy the outline phrasing or include every detail of it. Every shot should use its action and prop to show what is being said. Keep the character names requested in the brief. Use Milo and Ada only when the brief names nobody. Avoid impossible actions: a finite procedural animation engine executes these scenes.
Use prop_motion=open when a door actually opens; otherwise still. Choose different actions, settings and cameras when useful. Do not repeat scenes or sentences. No subtitles or JSON examples inside narration.
Mandatory story arc: {outline.model_dump_json()}
Source notes: {json.dumps(sources) if sources else 'NONE — fiction only'}'''
    for offset in range(0,count,6):
        size=min(6,count-offset)
        print(f'Writing scenes {offset+1}–{offset+size} of {count}',flush=True)
        schema=Batch.model_json_schema();schema['properties']['scenes']['minItems']=size;schema['properties']['scenes']['maxItems']=size
        schema['$defs']['Shot']['properties']['narration']['maxLength']=min(450,words_per_scene*8+50)
        grammar=LlamaGrammar.from_json_schema(json.dumps(schema),verbose=False)
        context=' '.join(s.narration for s in allshots)[-5000:]
        prompt=f'Write exactly {size} scenes, scenes {offset+1} through {offset+size} of a {count}-scene story. '
        if not offset:prompt+='Begin with the hook and setup. '
        if offset+size==count:prompt+=f'The FINAL scene MUST resolve the conflict by showing this exact ending: {outline.ending}. Do not repeat a failed attempt. '
        prompt+='Each scene advances to a new event. Do not simply restate the previous action. '
        prompt+=f'Previous story (continue without repetition): {context or "The story has not started."}'
        result=llm.create_chat_completion(messages=[{'role':'system','content':system},{'role':'user','content':prompt}],grammar=grammar,temperature=.65,top_p=.9,max_tokens=2600,seed=seed+offset,repeat_penalty=1.12,frequency_penalty=.15)
        raw=result['choices'][0]['message']['content'];raws.append(raw)
        (out/'writer-raw.json').write_text(json.dumps(raws,indent=2))
        batch=Batch.model_validate_json(raw)
        if len(batch.scenes)!=size:raise ValueError(f'Writer produced {len(batch.scenes)} scenes; requested {size}. Raw output preserved.')
        allshots.extend(batch.scenes)
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
    for i,a in enumerate(scenes):
        for b in scenes[i+1:]:
            overlap=SequenceMatcher(None,a.narration.lower().split(),b.narration.lower().split()).ratio()
            if overlap>.80:raise ValueError(f'Writer repeated substantially the same narration in {a.id}/{b.id}; revise with a reviewed plan or a larger model')
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
