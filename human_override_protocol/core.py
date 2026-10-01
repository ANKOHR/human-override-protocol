"""Pure eligibility checks. Hypothetical savings are never measured here."""
from datetime import date


class SchemaError(ValueError):
    """An input field violates the explicit protocol."""


def fail(field, reason):
    raise SchemaError(f"SchemaError: {field}: {reason}")


def text(value, field):
    if not isinstance(value, str) or not value.strip() or len(value) > 10000:
        fail(field, "expected nonempty string of at most 10000 characters")
    if chr(0x2014) in value:
        fail(field, "em dash is forbidden; use a hyphen")
    return value


def day(value, field):
    text(value, field)
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError()
        return parsed
    except ValueError:
        fail(field, "expected ISO date YYYY-MM-DD")


def fields(obj, required, field):
    if not isinstance(obj, dict):
        fail(field, "expected object")
    if set(obj) != set(required):
        fail(field, f"missing={sorted(set(required)-set(obj))}, unknown={sorted(set(obj)-set(required))}")


def evaluate(document):
    fields(document, ['synthetic', 'source', 'as_of', 'requests'], 'document')
    if type(document['synthetic']) is not bool:
        fail('synthetic', 'expected boolean')
    text(document['source'], 'source')
    as_of = day(document['as_of'], 'as_of')
    if not isinstance(document['requests'], list):
        fail('requests', 'expected array')
    results, seen = [], set()
    required = ['id', 'requester', 'operator', 'role', 'required_role', 'scope',
                'approved_scope', 'created', 'expires', 'decision', 'reason', 'amount']
    for index, item in enumerate(document['requests']):
        prefix = f'requests[{index}]'
        fields(item, required, prefix)
        for key in required:
            if key != 'amount':
                text(item[key], f'{prefix}.{key}')
        if item['id'] in seen:
            fail(f'{prefix}.id', 'duplicate id')
        seen.add(item['id'])
        amount = item['amount']
        if type(amount) is not int or amount < 0 or amount > 10**12:
            fail(f'{prefix}.amount', 'expected integer minor units from 0 to 1000000000000')
        created = day(item['created'], f'{prefix}.created')
        expires = day(item['expires'], f'{prefix}.expires')
        if created > as_of:
            fail(f'{prefix}.created', 'future request relative to as_of')
        if expires < created:
            fail(f'{prefix}.expires', 'precedes created')
        if item['decision'] not in ('approve', 'deny', 'pending'):
            fail(f'{prefix}.decision', 'expected approve, deny, or pending')
        reasons = []
        if item['decision'] == 'deny':
            status, reasons = 'denied', ['operator_denied']
        elif item['decision'] == 'pending':
            status, reasons = 'pending', ['awaiting_decision']
        else:
            if expires < as_of:
                reasons.append('approval_expired')
            if item['operator'] == item['requester']:
                reasons.append('self_approval')
            if item['role'] != item['required_role']:
                reasons.append('role_mismatch')
            if item['scope'] != item['approved_scope']:
                reasons.append('scope_mismatch')
            status = 'blocked' if reasons else 'eligible'
        results.append({'id': item['id'], 'status': status, 'reasons': reasons, 'amount': amount})
    results.sort(key=lambda row: row['id'])
    counts = {key: sum(row['status'] == key for row in results)
              for key in ('eligible', 'blocked', 'denied', 'pending')}
    return {'as_of': document['as_of'], 'provenance': {'synthetic': document['synthetic'],
            'source': document['source']}, 'total': len(results), 'counts': counts,
            'amount_total_minor_units': sum(row['amount'] for row in results),
            'results': results, 'savings': 'Unmeasured: time and money saved are not reported.'}
