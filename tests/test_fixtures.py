import json
from human_override_protocol.fixtures import generate
from human_override_protocol.core import evaluate

def test_fixtures_labelled_synthetic(tmp_path):
    generate(tmp_path)
    for path in tmp_path.glob('*.json'):
        assert json.loads(path.read_text())['synthetic'] is True
    assert 'Synthetic' in (tmp_path/'SYNTHETIC.md').read_text()

def test_fixture_ground_truth_matches_hand_computed(tmp_path):
    generate(tmp_path)
    expected = json.loads((tmp_path/'expectations.json').read_text())
    actual = evaluate(json.loads((tmp_path/'requests.json').read_text()))
    assert actual['total'] == expected['total'] == 200
    assert actual['counts'] == expected['counts'] == dict(eligible=80, blocked=80, denied=20, pending=20)
    assert actual['amount_total_minor_units'] == expected['amount_total_minor_units'] == 20000
    assert [r['id'] for r in actual['results'] if r['status']=='blocked'] == expected['blocked_ids']

def test_corrupted_ground_truth_changes_computed_result(tmp_path):
    generate(tmp_path)
    data = json.loads((tmp_path/'requests.json').read_text())
    data['requests'][0]['operator'] = 'requester'
    data['requests'][0]['amount'] = 7
    actual = evaluate(data)
    assert actual['counts']['blocked'] == 81
    assert actual['counts']['eligible'] == 79
    assert actual['amount_total_minor_units'] == 19907
    (tmp_path/'expectations.json').write_text('{"synthetic": true, "total": 999}')
    assert evaluate(data) == actual
