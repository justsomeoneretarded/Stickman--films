"""Genuine local-model writer. Fixed examples are never a title fallback."""
from __future__ import annotations
import json
import math
from pathlib import Path
import re
from pydantic import BaseModel,Field
from typing import Literal
from .schema import Plan,Scene,Actor,Cue,NICHES,ENVIRONMENTS,ACTIONS,CAMERAS,Source

KEYWORDS=[['brain','psychology','procrastin','behavior','dopamine'],['funny','comedy','awkward','queue'],['money','business','cash','bank','finance'],['history','war','border','geopolit'],['surviv','what if','what-if','island'],['story','lesson','friendship','kindness'],['science','gravity','physics','space'],['habit','improve','routine','discipline'],['cyber','password','technology','computer'],['mystery','scam','fraud','prize']]


def detect(title,brief):
    combined=(title+' '+brief).lower()
    scores=[sum(combined.count(k) for k in words) for words in KEYWORDS]
    return NICHES[max(range(10),key=lambda i:scores[i])] if max(scores)>0 else NICHES[5]

class Shot(BaseModel):
    narration: str
    label: str
    environment: Literal[tuple(ENVIRONMENTS)]
    action: Literal[tuple(ACTIONS)]
    prop: Literal["none","phone","clock","box","coin","book","plant","door","lock","planet","flag","water","evidence","ball","steps"]
    camera: Literal[tuple(CAMERAS)]
    mood: Literal['curious','comic','tense','warm','wonder','silence']

class Batch(BaseModel):
    scenes: list[Shot] = Field(min_length=1,max_length=8)


def generate(title,brief,minutes,niche,model_dir,out,seed=42,sources=None,word_factor=1.):
    from llama_cpp import Llama,LlamaGrammar
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    sources=sources or []
    model=Path(model_dir)/'qwen2.5-1.5b-instruct-q4_k_m.gguf'
    if not model.exists():raise FileNotFoundError('Missing local writer model; run stickfilm models --local. Alternatively pass --plan with a reviewed JSON plan.')
    llm=Llama(model_path=str(model),n_ctx=8192,n_threads=2,n_batch=256,seed=seed,verbose=False,chat_format='chatml')

    niche=detect(title,brief) if niche=='Auto-detect' else niche
    count=max(6,math.ceil(minutes*6))
    words_per_scene=max(13,round(minutes*155*word_factor/count))
    allshots=[];raws=[]
    if sources:
        policy='Use ONLY the supplied source notes for factual claims. Do not add dates, statistics, diagnoses or guarantees. The characters and framing story may be invented.'
    else:
        policy='Write explicitly FICTIONAL entertainment about imaginary people. No assertions about neuroscience, medicine, actual history, actual statistics, real people, or real companies. Do not pretend to answer factual questions without sources.'
    system=f'''You write original short animated stories. Output valid JSON, nothing else.
Niche: {niche}. Title: {title}. Brief: {brief}.
{policy}
The story must satisfy the brief within those limits. Start with an intriguing concrete situation, build a conflict, discover something, end with a payoff. No generic introduction, no presenter, no references to watching a video.
Each scene has narration (about {words_per_scene} words), a brief editorial label (max 50 characters), environment, character action, prop, camera, and music mood.
Write narration that can be spoken naturally, not stage directions. Every shot should use its action and prop to show what is being said. Hero Milo and friend Ada are available. Avoid impossible actions: a finite procedural animation engine executes these scenes.
Choose different actions, settings and cameras when useful. Do not repeat scenes or sentences. No subtitles or JSON examples inside narration.
Source notes: {json.dumps(sources) if sources else 'NONE — fiction only'}'''
    for offset in range(0,count,6):
        size=min(6,count-offset)
        schema=Batch.model_json_schema();schema['properties']['scenes']['minItems']=size;schema['properties']['scenes']['maxItems']=size
        grammar=LlamaGrammar.from_json_schema(json.dumps(schema),verbose=False)
        context=' '.join(s.narration for s in allshots)[-5000:]
        prompt=f'Write exactly {size} scenes, scenes {offset+1} through {offset+size} of a {count}-scene story. '
        if not offset:prompt+='Begin with the hook and setup. '
        if offset+size==count:prompt+='End with a satisfying payoff. '
        prompt+=f'Previous story (continue without repetition): {context or "The story has not started."}'
        result=llm.create_chat_completion(messages=[{'role':'system','content':system},{'role':'user','content':prompt}],grammar=grammar,temperature=.65,top_p=.9,max_tokens=2600,seed=seed+offset)
        raw=result['choices'][0]['message']['content'];raws.append(raw)
        (out/'writer-raw.json').write_text(json.dumps(raws,indent=2))
        batch=Batch.model_validate_json(raw)
        if len(batch.scenes)!=size:raise ValueError(f'Writer produced {len(batch.scenes)} scenes; requested {size}. Raw output preserved.')
        allshots.extend(batch.scenes)
    scenes=[]
    for i,s in enumerate(allshots):
        if len(s.narration.split())<8:raise ValueError('Local writer returned an empty/short narration; use a reviewed plan')
        if re.search(r'\b\d{4}\b|\d+\s*%',s.narration) and not sources:raise ValueError('Unsourced date/statistic in local script; supply reviewed source notes')
        action=s.action
        beat='hook' if i==0 else 'setup' if i==1 else 'payoff' if i==len(allshots)-1 else 'conflict' if i<len(allshots)/2 else 'discovery'
        actor=Actor(action=action,x=940 if action in ('reach','pickup','inspect') else 480,travel=350 if action in ('walk','stairs') else 520 if action in ('run','sprint') else 0)
        scenes.append(Scene(id=f's{i+1:03}',beat=beat,narration=s.narration,label=s.label[:65],environment=s.environment,actors=[actor],prop=s.prop,camera=s.camera,music=s.mood,
            transition='dissolve' if i%4==0 else 'cut',cues=[Cue(at=.5,kind='click' if s.prop=='phone' else 'chime',gain=.15)]))
    if not sources:scenes[0].label='FICTIONAL STORY / '+scenes[0].label[:45]
    p=Plan(title=title,brief=brief,niche=niche,requested_minutes=minutes,seed=seed,provenance='local-model',factual_status='source-grounded' if sources else 'fiction',sources=sources,scenes=scenes)
    (out/'generated-plan.json').write_text(p.model_dump_json(indent=2))
    del llm
    return p
