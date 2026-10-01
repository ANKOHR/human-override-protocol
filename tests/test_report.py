import json
from human_override_protocol.fixtures import document
from human_override_protocol.core import evaluate
from human_override_protocol.report import render

def test_report_matches_ground_truth_exact():
    result = json.loads(render(evaluate(document()), 'json'))
    assert result['counts'] == dict(eligible=80, blocked=80, denied=20, pending=20)
    assert sum(result['counts'].values()) == result['total'] == 200
    assert result['amount_total_minor_units'] == 20000

def test_report_zero_false_positives():
    rows = json.loads(render(evaluate(document()), 'json'))['results']
    assert {r['id'] for r in rows if r['status']=='blocked'} == {f'HOP-{i:03d}' for i in range(200) if i%10 in (4,5,6,7)}

def test_report_carries_provenance_banner():
    for fmt in ('md', 'json'):
        assert 'Data provenance: SYNTHETIC FIXTURES' in render(evaluate(document()), fmt)
    data = document(1)
    data['synthetic'] = False
    data['source'] = 'Henry hand-entered trial'
    assert 'ownership not verified' in render(evaluate(data))

def test_hypothetical_figures_labelled():
    for fmt in ('md', 'json'):
        assert 'Unmeasured: time and money saved are not reported.' in render(evaluate(document()), fmt)

def test_no_em_dashes_in_outputs():
    for fmt in ('md', 'json'):
        assert chr(0x2014) not in render(evaluate(document()), fmt)
