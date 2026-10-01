"""Local file CLI. No network calls and no infrastructure execution."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import SchemaError, evaluate
from .fixtures import generate
from .report import render, banner


class InputError(ValueError):
    pass


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise InputError(f'ParseError: {path}: line {exc.lineno}: {exc.msg}') from exc
    except UnicodeError as exc:
        raise InputError(f'ParseError: {path}: line 1: invalid UTF-8') from exc


def load(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise InputError(f'MissingInput: {directory}; use hop fixtures --out demo')
    path = directory / 'requests.json'
    if not path.exists():
        extras = [p for p in directory.iterdir() if p.is_file()]
        if extras:
            raise InputError(f'MissingInput: {path}; expected requests.json (JSON only)')
        return {'synthetic': False, 'source': 'Empty input directory; no records supplied',
                'as_of': '1970-01-01', 'requests': []}
    try:
        return read_json(path)
    except OSError as exc:
        raise InputError(f'InputReadError: {path}: {exc.strerror}') from exc


def atomic_write(path, content):
    path = Path(path)
    temp = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=path.parent, delete=False) as stream:
            temp = Path(stream.name)
            stream.write(content)
        os.replace(temp, path)
    except OSError as exc:
        raise InputError(f'WriteError: {path}: {exc.strerror}') from exc
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(prog='hop', description='Compute operator intervention eligibility from local JSON.')
    sub = parser.add_subparsers(dest='command', required=True)
    fixture = sub.add_parser('fixtures', help='Generate labelled synthetic drill. Example: hop fixtures --out demo')
    fixture.add_argument('--out', required=True)
    for name, description in [('run', 'Evaluate and save report state'),
                              ('validate', 'Validate intervention schema and policy inputs'),
                              ('inspect', 'Inspect eligibility and reasons for one request')]:
        cmd = sub.add_parser(name, help=f'{description}. Example: hop {name} --input demo' + (' --id HOP-004' if name == 'inspect' else ''), description=description)
        cmd.add_argument('--input', required=True)
        if name == 'run':
            cmd.add_argument('--state', default='.hop/result.json')
        if name == 'inspect':
            cmd.add_argument('--id', required=True)
    report = sub.add_parser('report', help='Render provenance and computed figures. Example: hop report --format md')
    report.add_argument('--format', choices=['md', 'json'], default='md')
    report.add_argument('--state', default='.hop/result.json')
    report.add_argument('--out')
    args = parser.parse_args(argv)
    try:
        if args.command == 'fixtures':
            generate(args.out)
            print('SYNTHETIC FIXTURES: generated 200 records; savings unmeasured.')
        elif args.command == 'report':
            path = Path(args.state)
            if not path.is_file():
                raise InputError(f'MissingInput: {path}; run hop run --input demo first')
            content = render(read_json(path), args.format)
            if args.out:
                atomic_write(args.out, content)
            else:
                print(content, end='')
        else:
            try:
                result = evaluate(load(args.input))
            except SchemaError as exc:
                raise InputError(f'{Path(args.input) / "requests.json"}: {exc}') from exc
            if args.command == 'run':
                atomic_write(args.state, json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
                print(render(result, 'json'), end='')
            elif args.command == 'validate':
                print(f"Valid: {result['total']} requests. " + render(result, 'json'))
            else:
                rows = [row for row in result['results'] if row['id'] == args.id]
                if not rows:
                    raise InputError(f'RequestNotFound: {args.id}')
                print(json.dumps({'banner': banner(result), 'provenance': result['provenance'], 'request': rows[0],
                                  'savings': result['savings']}, ensure_ascii=False, sort_keys=True))
        return 0
    except (InputError, SchemaError, OSError, KeyError, TypeError, ValueError) as exc:
        message = str(exc).replace(chr(0x2014), '-')
        print(f'Error: {message}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
