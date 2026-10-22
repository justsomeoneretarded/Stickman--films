"""Shared input validation and failure reports for manual film workflows."""
import json
import os
from pathlib import Path
import traceback
from .schema import Plan,minutes


def selected_plan(mode,path='',default=''):
    if mode=='New story':return ''
    if mode=='Reviewed plan':return path.strip() or default
    raise ValueError('Choose New story or Reviewed plan')


def validate_inputs(env):
    title=env.get('FILM_TITLE','').strip();brief=env.get('FILM_BRIEF','').strip()
    if not title or not brief:raise ValueError('Enter a title and creative brief')
    if len(title)>180 or len(brief)>4000:raise ValueError('Title max 180 and brief max 4000 characters')
    minutes(env.get('FILM_MINUTES','5'),float(env.get('MAX_MINUTES','10')))
    path=env.get('FILM_PLAN','').strip()
    if path:
        p=Path(path).resolve()
        if not p.is_relative_to(Path.cwd().resolve()) or not p.is_file():raise ValueError('Reviewed plan must be an existing repository JSON file')
        plan=Plan.model_validate_json(p.read_text())
        if plan.niche!=env.get('FILM_NICHE'):raise ValueError('Reviewed plan belongs to a different niche')
        if title!=plan.title or brief!=plan.brief:
            raise ValueError('This title or brief differs from the reviewed plan. Select story_mode = New story to generate from your inputs, or restore the reviewed plan\'s exact title and brief.')
    return path


def failure_report(out,error):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    # Preserve a more specific pipeline error if one was already recorded.
    path=out/'failure.json'
    if not path.exists():path.write_text(json.dumps({'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()},indent=2))
    if isinstance(error,SystemExit):
        detail=error.__cause__ or error.__context__
        if detail and path.exists():
            d=json.loads(path.read_text())
            if d.get('type')=='SystemExit':
                d.update(type=type(detail).__name__,message=str(detail));path.write_text(json.dumps(d,indent=2))
    data=json.loads(path.read_text())
    (out/'failure.md').write_text('# Film production failed\n\n'+str(data.get('message',error))+'\n\nSelect **New story** when using a new title and brief. Reviewed plans require matching inputs.\n')
    summary=os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with Path(summary).open('a') as f:f.write((out/'failure.md').read_text())
