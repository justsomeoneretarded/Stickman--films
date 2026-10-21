"""One workflow, one film, one isolated output directory; no comparison matrix."""
import json
import os
from pathlib import Path
from stickfilm.cli import main
from stickfilm.schema import Plan
import sys


def repo_path(value):
    p=Path(value).resolve()
    if not p.is_relative_to(Path.cwd().resolve()) or not p.is_file():
        raise ValueError('Reviewed files must exist inside this repository')
    return str(p)


def production():
    out=Path('output/film');out.mkdir(parents=True,exist_ok=True)
    argv=['stickfilm','produce','--title',os.environ['FILM_TITLE'],'--brief',os.environ['FILM_BRIEF'],
          '--minutes',os.environ['FILM_MINUTES'],'--niche',os.environ['FILM_NICHE'],
          '--models','models','--out',str(out),'--preset',os.getenv('FILM_QUALITY','production')]
    if os.getenv('FILM_PLAN'):
        path=repo_path(os.environ['FILM_PLAN'])
        if Plan.model_validate_json(Path(path).read_text()).niche!=os.environ['FILM_NICHE']:
            raise ValueError('Reviewed plan belongs to a different niche')
        argv+=['--plan',path]
    if os.getenv('FILM_SOURCES'):argv+=['--sources',repo_path(os.environ['FILM_SOURCES'])]
    sys.argv=argv
    main()
    p=Plan.model_validate_json((out/'plan.json').read_text())
    if float(os.environ['FILM_MINUTES'])==5 and not 240<=p.scenes[-1].end<=360:
        raise ValueError('A requested five-minute film must finish between four and six minutes')
    (out/'script.md').write_text('# '+p.title+'\n\n'+'\n\n'.join(f'**{s.start:.2f}–{s.end:.2f}s / {s.label}**\n\n{s.narration}' for s in p.scenes)+'\n\nSources:\n'+ '\n'.join(f'- {s.url}: {s.claim}' for s in p.sources))
    (out/'storyboard.md').write_text('# Directed storyboard\n\n'+ '\n\n'.join(f'**{s.id} / {s.start:.2f}–{s.end:.2f}s**\n\n{s.environment}; {s.lighting}; camera: {s.camera}; set: {s.setpiece}; characters: '+', '.join(f'{a.character}: {a.action}' for a in s.actors)+f'; music: {s.music}.\n\n{s.label}' for s in p.scenes))
    manifest=dict(title=p.title,niche=p.niche,seconds=p.scenes[-1].end,independent=True,run_id=os.getenv('GITHUB_RUN_ID'),workflow=os.getenv('GITHUB_WORKFLOW'),reviewed_plan=os.getenv('FILM_PLAN') or None)
    (out/'episode.json').write_text(json.dumps(manifest,indent=2))


if __name__=='__main__':production()
