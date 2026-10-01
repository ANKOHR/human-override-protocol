"""Labelled synthetic scenarios, no randomness (seed: none)."""
import json
from pathlib import Path


def record(index):
    row = dict(id=f'HOP-{index:03d}', requester='requester', operator='operator',
               role='sre', required_role='sre', scope='restart/service-a',
               approved_scope='restart/service-a', created='2026-09-01',
               expires='2026-10-01', decision='approve', reason='Synthetic recovery drill', amount=100)
    category = index % 10
    if category == 4:
        row['expires'] = '2026-09-29'
    elif category == 5:
        row['operator'] = row['requester']
    elif category == 6:
        row['role'] = 'viewer'
    elif category == 7:
        row['approved_scope'] = 'restart/service-b'
    elif category == 8:
        row['decision'] = 'deny'
    elif category == 9:
        row['decision'] = 'pending'
    return row


def document(count=200):
    return {'synthetic': True, 'source': 'Labelled synthetic intervention drill',
            'as_of': '2026-09-30', 'requests': [record(i) for i in range(count)]}


def generate(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'requests.json').write_text(json.dumps(document(), indent=2) + '\n', encoding='utf-8')
    # Hand arithmetic: 20 groups, each with 4 eligible, 4 blocked, 1 denied, 1 pending.
    expected = {'synthetic': True, 'total': 200,
                'counts': {'eligible': 80, 'blocked': 80, 'denied': 20, 'pending': 20},
                'amount_total_minor_units': 20000,
                'blocked_ids': [f'HOP-{i:03d}' for i in range(200) if i % 10 in (4, 5, 6, 7)]}
    (out / 'expectations.json').write_text(json.dumps(expected, indent=2) + '\n', encoding='utf-8')
    (out / 'SYNTHETIC.md').write_text('<!-- Synthetic fixture data -->\n# Synthetic fixture set\n\nAll records and expectations are synthetic. No randomness is used.\n', encoding='utf-8')
