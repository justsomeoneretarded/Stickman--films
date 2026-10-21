"""Small command surface shared by local development and GitHub Actions."""
import argparse
import json
import os
from pathlib import Path
import sys
from .schema import Plan,minutes,NICHES
from .models import download,ROOT
from .pipeline import produce
from .benchmark import benchmark_plan


def run(args):
    maximum=float(os.getenv('MAX_MINUTES','10'))
    requested=minutes(args.minutes,maximum)
    if args.plan:
        p=Path(args.plan).resolve()
        # Workflow plans must be repository files, never remote executable input.
        if os.getenv('GITHUB_ACTIONS') and not p.is_relative_to(ROOT):raise ValueError('Plan path must be inside the checked-out repository')
        plan=Plan.model_validate_json(p.read_text())
        if args.title and args.title!=plan.title:raise ValueError('A reviewed plan must match the requested title. Edit the plan; fixed scripts are not a title-to-script fallback.')
        if args.brief and args.brief!=plan.brief:raise ValueError('A reviewed plan must match the requested brief. Edit the plan or leave the CLI brief unset.')
        plan.requested_minutes=requested
    else:
        if not args.title or not args.brief:raise ValueError('Single-video generation requires --title and --brief')
        if len(args.title)>180 or len(args.brief)>4000:raise ValueError('Title max 180 and brief max 4000 characters')
        from .writer import generate
        sources=json.loads(Path(args.sources).read_text()) if args.sources else None
        plan=generate(args.title,args.brief,requested,args.niche,args.models,args.out,args.seed,sources)
    try:return produce(plan,args.out,args.models,args.preset)
    except ValueError as e:
        if args.plan or 'Measured narration timeline' not in str(e):raise
        # A single bounded content rewrite uses real duration rather than filler.
        measured=Plan.model_validate_json((Path(args.out)/'plan.json').read_text()).scenes[-1].end
        from .writer import generate
        plan=generate(args.title,args.brief,requested,args.niche,args.models,args.out,args.seed+1,sources,word_factor=requested*60/measured)
        return produce(plan,args.out,args.models,args.preset)


def parser():
    p=argparse.ArgumentParser(prog='stickfilm');sub=p.add_subparsers(dest='command',required=True)
    models=sub.add_parser('models');models.add_argument('--directory',default='models');models.add_argument('--local',action='store_true')
    b=sub.add_parser('benchmark');b.add_argument('--out',default='output/benchmark');b.add_argument('--models',default='models');b.add_argument('--preset',choices=['draft','preview','production'],default='production')
    r=sub.add_parser('produce');r.add_argument('--title');r.add_argument('--brief');r.add_argument('--minutes',default='3');r.add_argument('--niche',choices=['Auto-detect',*NICHES],default='Auto-detect');r.add_argument('--plan');r.add_argument('--sources');r.add_argument('--seed',type=int,default=42);r.add_argument('--models',default='models');r.add_argument('--out',default='output/video');r.add_argument('--preset',choices=['draft','preview','production'],default='production')
    s=sub.add_parser('schema');s.add_argument('--out',default='config/plan.schema.json')
    v=sub.add_parser('validate');v.add_argument('plan')
    c=sub.add_parser('compare');c.add_argument('directory');c.add_argument('--out',default='output/comparison.md')
    return p


def main():
    args=parser().parse_args()
    try:
        if args.command=='models':download(args.directory,args.local)
        elif args.command=='benchmark':print(produce(benchmark_plan(),args.out,args.models,args.preset,True)[0])
        elif args.command=='produce':print(run(args)[0])
        elif args.command=='schema':Path(args.out).write_text(json.dumps(Plan.model_json_schema(),indent=2))
        elif args.command=='validate':print(Plan.model_validate_json(Path(args.plan).read_text()).title)
        elif args.command=='compare':
            from .comparison import compare
            compare(args.directory,args.out)
    except Exception as e:
        print(f'ERROR: {type(e).__name__}: {e}',file=sys.stderr)
        raise SystemExit(1) from e

if __name__=='__main__':main()
