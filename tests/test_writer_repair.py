import json
from pathlib import Path
from types import SimpleNamespace
from stickfilm.writer import repeated_passages,batch_problem,story_phase

ROOT=Path(__file__).parents[1]

def test_duplicate_is_checked_against_all_batches_not_only_recent_tail():
    earlier=['Maya stares at her phone, the screen glowing with a request for another favor.']
    previous=earlier+[f'A distinct event {i} happens at another location with a new consequence.' for i in range(36)]
    assert repeated_passages(earlier,previous)==[(0,0)]

def test_batch_rejection_keeps_original_quality_threshold():
    text='Maya puts down her phone and walks into the classroom where a stranger saves her a seat.'
    old=[SimpleNamespace(narration=text)]
    duplicate=SimpleNamespace(scenes=[SimpleNamespace(narration=text)])
    assert 'Repeated narration' in batch_problem(duplicate,old,1,[])
    fresh=SimpleNamespace(scenes=[SimpleNamespace(narration='The teacher places two brushes beside the canvas, and Maya chooses the bright blue paint.')])
    assert batch_problem(fresh,old,1,[]) is None

def test_repair_does_not_accept_truncated_or_unsourced_text():
    for text in ['Maya leaves the classroom and walks into the street where', 'Research proves that 90% of people fear being abandoned by friends.']:
        b=SimpleNamespace(scenes=[SimpleNamespace(narration=text)])
        assert batch_problem(b,[],1,[]) is not None

def test_long_story_assigns_ending_only_to_last_act():
    assert 'HOOK' in story_phase(0,42)
    assert 'ESCALATION' in story_phase(7,42)
    assert 'DECISIVE ACTION' in story_phase(33,42)
    assert 'PAYOFF' in story_phase(41,42)

def test_generate_rewrites_rejected_batch_before_accepting(tmp_path,monkeypatch):
    import sys
    import types
    from stickfilm.writer import generate
    from stickfilm.models import ROOT
    filename=json.loads((ROOT/'config/models.json').read_text())['writer']['file']
    (tmp_path/filename).touch()
    texts=[
        'Maya waits beside a cake while the last candle burns down alone.',
        'A friend asks for help moving boxes instead of visiting her birthday party.',
        'She cancels her drawing lesson and carries the heaviest box upstairs.',
        'The promised thank-you never arrives, and Maya finally notices her abandoned sketchbook.',
        'Her hands shake as she declines the next request and leaves home.',
        'At class a stranger moves a bag aside, making space for Maya without asking for anything.'
    ]
    def shot(text):return dict(narration=text,label='A new event',environment='office',action='think',prop='book',camera='wide',mood='warm')
    responses=[
        dict(hook='Maya waits alone on her birthday.',conflict='Her friend asks for another unpaid favor.',discovery='She notices what she keeps giving up.',ending='A stranger saves her a place at class.'),
        dict(beats=[dict(event=t) for t in texts]),
        dict(scenes=[shot(texts[0])]*6),
        dict(scenes=[shot(t) for t in texts])
    ]
    calls=[]
    class FakeLlama:
        def __init__(self,**kwargs):pass
        def create_chat_completion(self,**kwargs):
            calls.append(kwargs)
            return {'choices':[{'message':{'content':json.dumps(responses.pop(0))}}]}
    class Grammar:
        @staticmethod
        def from_json_schema(*a,**kw):return None
    monkeypatch.setitem(sys.modules,'llama_cpp',types.SimpleNamespace(Llama=FakeLlama,LlamaGrammar=Grammar))
    out=tmp_path/'output'
    p=generate('A New Seat','A fictional birthday story about Maya.',.6,'Psychology & Human Behavior',tmp_path,out)
    assert len(calls)==4 and not responses
    assert 'REJECTED' in calls[-1]['messages'][-1]['content']
    assert p.provenance=='local-model'
    assert [s.narration for s in p.scenes]==texts
    assert len(json.loads((out/'writer-accepted.json').read_text()))==6
