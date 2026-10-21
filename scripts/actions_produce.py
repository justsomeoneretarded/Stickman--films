"""Construct an argv list from JSON, avoiding shell command injection."""
import json
import os
from pathlib import Path
from stickfilm.cli import main
import sys

inputs=json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text()).get('inputs',{})
comparison=inputs.get('production_mode')=='Ten-Niche Comparison'
plan=os.environ.get('PLAN_PATH','')
argv=['stickfilm','produce','--minutes',os.getenv('COMPARISON_MINUTES','1.25') if comparison else inputs.get('minutes','3'),
      '--models','models','--out','output/'+os.environ['JOB_KEY'],'--preset',inputs.get('quality','production')]
if plan:argv+=['--plan',plan]
if not comparison:
    argv+=['--title',inputs['video_title'],'--brief',inputs['video_description'],'--niche',inputs.get('niche','Auto-detect')]
    if inputs.get('source_notes_path'):argv+=['--sources',inputs['source_notes_path']]
sys.argv=argv
main()
