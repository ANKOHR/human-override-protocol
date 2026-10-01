"""Deterministic reports with explicit provenance."""
import json


def banner(result):
    p = result['provenance']
    kind = 'SYNTHETIC FIXTURES' if p['synthetic'] else 'REAL INPUT (user-declared; ownership not verified)'
    return f"Data provenance: {kind}. Source: {p['source']}. All figures computed from explicit inputs."


def render(result, format='md'):
    if format == 'json':
        return json.dumps({'banner': banner(result), **result}, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
    lines = ['# Human Override Protocol', '', banner(result), '',
             f"Evaluation date: {result['as_of']}", f"Total requests: {result['total']}"]
    lines.extend(f'{key}: {value}' for key, value in result['counts'].items())
    lines.extend([f"Declared amount total (minor units, single input currency): {result['amount_total_minor_units']}",
                  result['savings'], '', 'Eligibility is a policy check, not proof of operational safety.', '',
                  '| Request | Status | Reasons | Amount (minor units) |', '| --- | --- | --- | --- |'])
    for row in result['results']:
        ident = row['id'].replace('\\', '\\\\').replace('|', r'\|').replace('\n', ' ').replace('\r', ' ')
        lines.append(f"| {ident} | {row['status']} | {', '.join(row['reasons']) or 'checks_passed'} | {row['amount']} |")
    return '\n'.join(lines) + '\n'
