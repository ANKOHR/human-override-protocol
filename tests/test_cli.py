import json
import subprocess
import sys
import time
from human_override_protocol.cli import main
from human_override_protocol.fixtures import generate, document

def test_run_completes_on_fixture(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    generate(tmp_path/'demo')
    start = time.perf_counter()
    assert main(['run', '--input', 'demo']) == 0
    assert main(['report', '--format', 'md']) == 0
    assert time.perf_counter()-start < 5
    assert 'SYNTHETIC FIXTURES' in capsys.readouterr().out

def test_empty_input_renders_without_traceback(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path/'empty').mkdir()
    assert main(['run', '--input', 'empty']) == 0
    assert main(['report', '--format', 'json']) == 0
    assert '"total": 0' in capsys.readouterr().out

def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path/'requests.json').write_text('{\n bad')
    assert main(['validate', '--input', str(tmp_path)]) == 2
    err = capsys.readouterr().err
    assert 'ParseError' in err and 'requests.json: line 2' in err
    assert 'Traceback' not in err

def test_determinism_byte_identical(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    generate(tmp_path/'demo')
    before = (tmp_path/'demo/requests.json').read_bytes()
    generate(tmp_path/'demo')
    assert before == (tmp_path/'demo/requests.json').read_bytes()
    outputs = []
    for _ in range(2):
        assert main(['run', '--input', 'demo']) == 0
        capsys.readouterr()
        assert main(['report', '--format', 'json']) == 0
        outputs.append(capsys.readouterr().out.encode())
    assert outputs[0] == outputs[1]

def test_cli_smoke_all_subcommands(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(['fixtures', '--out', 'demo']) == 0
    assert main(['validate', '--input', 'demo']) == 0
    assert main(['inspect', '--input', 'demo', '--id', 'HOP-004']) == 0
    assert main(['run', '--input', 'demo']) == 0
    assert main(['report', '--format', 'md', '--out', 'report.md']) == 0
    for name in ('fixtures', 'validate', 'inspect', 'run', 'report'):
        try:
            main([name, '--help'])
        except SystemExit as exc:
            assert exc.code == 0
    assert chr(0x2014) not in capsys.readouterr().out

def test_missing_input_and_state(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(['run', '--input', 'missing']) == 2
    assert 'MissingInput' in capsys.readouterr().err
    assert main(['report']) == 2
    assert 'run hop run' in capsys.readouterr().err

def test_report_write_failure_no_partial_files(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    generate(tmp_path/'demo')
    main(['run', '--input', 'demo'])
    (tmp_path/'blocker').write_text('keep')
    assert main(['report', '--out', 'blocker/report.md']) == 2
    assert 'WriteError' in capsys.readouterr().err
    assert (tmp_path/'blocker').read_text() == 'keep'
    assert not list(tmp_path.glob('tmp*'))

def test_hand_written_five_records(tmp_path):
    data = document(5)
    (tmp_path/'requests.json').write_text(json.dumps(data))
    assert main(['validate', '--input', str(tmp_path)]) == 0
