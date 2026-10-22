import json
from pathlib import Path
import pytest
import yaml
from stickfilm.workflow import selected_plan,validate_inputs,failure_report

ROOT=Path(__file__).parents[1]

def test_new_story_ignores_stale_reviewed_plan():
    assert selected_plan('New story','episodes/psychology.json','episodes/psychology.json')==''
    for key in ('psychology','what-if'):
        w=yaml.safe_load((ROOT/f'.github/workflows/{key}.yml').read_text())
        on=w.get('on',w.get(True));inputs=on['workflow_dispatch']['inputs']
        assert inputs['story_mode']['default']=='New story'
        assert 'default' not in inputs['reviewed_plan_path']
        expr=next(iter(w['jobs'].values()))['with']['plan']
        assert "inputs.story_mode == 'Reviewed plan'" in expr
        assert expr.endswith("|| '' }}")

def test_reviewed_mode_preserves_exact_title_check():
    p=json.loads((ROOT/'episodes/psychology.json').read_text())
    env=dict(FILM_TITLE='Different title',FILM_BRIEF=p['brief'],FILM_MINUTES='5',FILM_NICHE=p['niche'],FILM_PLAN=str(ROOT/'episodes/psychology.json'))
    with pytest.raises(ValueError,match='story_mode = New story'):validate_inputs(env)
    env['FILM_PLAN']=''
    assert validate_inputs(env)==''
    assert selected_plan('Reviewed plan','','episodes/psychology.json')=='episodes/psychology.json'

def test_preproduction_failure_writes_downloadable_original_error(tmp_path,monkeypatch):
    summary=tmp_path/'summary.md';monkeypatch.setenv('GITHUB_STEP_SUMMARY',str(summary))
    try:raise ValueError('Original title mismatch')
    except ValueError as e:failure_report(tmp_path/'film',e)
    assert json.loads((tmp_path/'film/failure.json').read_text())['message']=='Original title mismatch'
    assert 'Original title mismatch' in summary.read_text()
    assert (tmp_path/'film/failure.md').is_file()
