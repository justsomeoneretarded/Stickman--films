"""Read dispatch JSON as data. No workflow input is interpolated into shell code."""
import json
import os
from pathlib import Path
from stickfilm.schema import minutes,NICHES


def validate():
    event=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    i=event.get('inputs',{})
    mode=i.get('production_mode','Animation Quality Test')
    if mode not in ['Single Video','Ten-Niche Comparison','Animation Quality Test']:raise ValueError('Unknown mode')
    duration=minutes(i.get('minutes','3'),float(os.getenv('MAX_MINUTES','10')))
    if len(i.get('video_title',''))>180 or len(i.get('video_description',''))>4000:raise ValueError('Title/description exceed size limits')
    if i.get('quality','production') not in ('draft','preview','production'):raise ValueError('Invalid preset')
    parallel=int(os.getenv('MAX_PARALLEL','2'))
    if not 1<=parallel<=10:raise ValueError('MAX_PARALLEL must be between 1 and 10')
    comparison=minutes(os.getenv('COMPARISON_MINUTES','1.25'),float(os.getenv('MAX_MINUTES','10')))
    if mode=='Ten-Niche Comparison':matrix={'include':[{'key':f'{n:02}','plan':f'examples/plans/{n:02}.json'} for n in range(10)]}
    else:matrix={'include':[{'key':'single','plan':i.get('plan_path','')}]}  # unused in benchmark-only mode
    with Path(os.environ['GITHUB_OUTPUT']).open('a') as f:
        for key,value in {'matrix':json.dumps(matrix,separators=(',',':')),'parallel':parallel,'mode':mode}.items():f.write(f'{key}={value}\n')
    print(f'Validated {mode}; requested {duration} minutes, comparison {comparison} minutes, concurrency {parallel}.')

if __name__=='__main__':validate()
