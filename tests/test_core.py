import pytest
from human_override_protocol.core import evaluate, SchemaError
from human_override_protocol.fixtures import document

@pytest.mark.parametrize('field,value', [('amount', -1), ('amount', True), ('amount', 1.2), ('created', '2027-01-01'), ('reason', 'x'*10001), ('decision', 'force'), ('expires', '2020-01-01')])
def test_rejects_adversarial_values(field, value):
    data = document(1)
    data['requests'][0][field] = value
    with pytest.raises(SchemaError, match=field):
        evaluate(data)

def test_duplicate_ids_rejected():
    data = document(2)
    data['requests'][1]['id'] = data['requests'][0]['id']
    with pytest.raises(SchemaError, match='duplicate id'):
        evaluate(data)

def test_handles_unicode_and_long_inputs():
    data = document(1)
    data['requests'][0]['id'] = '恢复 C:\\Users\\Henry | operator'
    data['requests'][0]['reason'] = '恢复'*5000
    assert evaluate(data)['total'] == 1

def test_all_checks_and_expiry_boundary():
    data = document(1)
    row = data['requests'][0]
    row['expires'] = data['as_of']
    assert evaluate(data)['counts']['eligible'] == 1
    row.update(operator='requester', role='viewer', approved_scope='other', expires='2026-09-29')
    assert evaluate(data)['results'][0]['reasons'] == ['approval_expired', 'self_approval', 'role_mismatch', 'scope_mismatch']

def test_schema_drift_named_field():
    data = document(1)
    data['requests'][0]['extra'] = 1
    with pytest.raises(SchemaError, match='extra'):
        evaluate(data)

@pytest.mark.parametrize('field,value', [('synthetic', 'true'), ('as_of', 'bad'), ('requests', {}), ('source', '')])
def test_document_schema(field, value):
    data = document(1)
    data[field] = value
    with pytest.raises(SchemaError, match=field):
        evaluate(data)
