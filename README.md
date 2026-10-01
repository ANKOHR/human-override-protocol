# Human Override Protocol

A deterministic Python CLI for reviewing operator intervention requests. It checks supplied approval decisions against explicit scope, role, separation of duties, and expiry rules. It does not connect to infrastructure or perform actions. CPU only, standard library runtime, no network calls or language models.

Hypothesis: a deterministic gate with planted ground truth can make intervention review auditable. The local acceptance target is 200 synthetic requests, exact counts and amount reconciliation, zero false positives, and a report in under 5 seconds. This establishes correctness on supplied scenarios, not real-world effectiveness.

## Quickstart

Python 3.10 or newer. Install locally without fetching dependencies:

```powershell
python -m pip install --no-deps --no-build-isolation -e .
hop fixtures --out demo
hop run --input demo
hop report --format md
python -m pytest -q
```

On Windows, if the user Scripts directory is absent from PATH, add it for the current PowerShell session before invoking hop:

```powershell
$hopScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts', scheme='nt_user'))"
$env:PATH = "$hopScripts;$env:PATH"
```

The editable install needs setuptools and wheel already installed. Without installation, use `python -m human_override_protocol.cli` in place of `hop`. Test tooling is pytest; it is not a runtime dependency.

`examples/tiny/requests.json` contains five explicitly listed synthetic requests for the smallest demo:

```powershell
hop run --input examples/tiny
hop report --format json
```

## Commands

- `hop fixtures --out demo`: writes 200 synthetic records, independent expectations and a synthetic notice.
- `hop run --input demo --state .hop/result.json`: validates all input and saves computed state atomically. Prints the JSON report.
- `hop report --format md --out report.md`: renders the last saved state. JSON is also supported. `--state` selects another result file. Re-run after changing input; reports are snapshots.
- `hop validate --input demo`: checks schema and prints computed policy results without saving state.
- `hop inspect --input demo --id HOP-004`: computes the input and shows one request's eligibility and reasons, with provenance.

Each command supports `--help`. Exit code 0 means the command succeeded, including when policy blocks a request. Exit code 2 means an input or write error. Eligibility is in the report, not the process exit code.

## Input reference

A directory holds one UTF-8 `requests.json`. `expectations.json` and the fixture notice are metadata only, never read by the engine. JSON is the only supported input encoding. A missing directory is an error. A truly empty directory yields zero requests and an explicitly supplied empty-input sentinel date of 1970-01-01; that date is not a measured event time. A nonempty directory without requests.json is a missing-input error.

The exact top-level fields are:

```json
{
  "synthetic": false,
  "source": "Henry hand-entered trial, source description supplied by Henry",
  "as_of": "2026-09-30",
  "requests": []
}
```

This snippet is an illustrative input template, not a recorded real trial. Set `synthetic: false` only for actual hand-entered real input. Source ownership is user-declared and never independently verified. Each request requires all of these fields, and unknown fields are rejected:

| Field | Meaning |
| --- | --- |
| id | Unique request identifier |
| requester, operator | Exact identities used for separation of duties |
| role, required_role | Supplied operator role and required approval role |
| scope, approved_scope | Exact requested and approved action scope |
| created, expires | ISO dates YYYY-MM-DD; expiry is inclusive |
| decision | approve, deny, or pending |
| reason | Nonempty operator justification |
| amount | Declared nonnegative integer minor units, maximum 1000000000000 |

All non-amount fields are nonempty strings, maximum 10000 characters. Top-level synthetic must be a boolean, requests an array, source a nonempty string, and as_of an ISO date. Identity, role and scope matching is exact and case-sensitive. Dates never depend on the machine clock. Created dates after as_of and expiry before creation are errors; future expiry is valid. Duplicate IDs, floats, booleans used as amounts, negative amounts, unknown fields, extreme strings and em dash characters are rejected with named schema errors. Unicode and Windows path strings are supported.

Every supplied request is accounted for or the entire run fails. An approved request is blocked if expired, self-approved, role-mismatched or scope-mismatched. All applicable block reasons appear in stable order. Denied and pending decisions take precedence over approval checks. No request is silently dropped. Amounts are declared values, not measured expenditure or savings. Use a single currency/unit system per input; this schema cannot verify currency consistency.

## Architecture

```text
requests.json -> CLI parse -> core.evaluate (pure checks)
                               -> deterministic state JSON
state JSON -> report.render -> provenance + counts + per-request reasons
fixtures -> labelled requests.json + independent expectations.json
```

Reports sort requests by ID. No randomness is used (seed: none). Identical inputs produce byte-identical reports. Dates and all policy facts come from input. A saved state is a local trusted artifact, not signed or tamper-evident. No authentication, role-directory lookup, approval signature validation, locks, change execution, revocation service or replay prevention is provided. Eligibility does not establish that an action is operationally safe.

## Honesty boundary and labels

All fixture JSON files include `synthetic: true`. JSON does not permit header comments, so the synthetic field is the in-file label; the fixture notice includes a synthetic header comment. The tiny example follows the same policy. Every report has a provenance banner distinguishing synthetic data from user-declared real data. The tool never discovers, predicts or estimates beyond its inputs. Time and money saved are unmeasured and explicitly not reported. No hypothetical savings figures are emitted. Performance evidence measures a local CLI demo, not operator productivity.

## Evidence and failure modes

`EVIDENCE.md` records the local acceptance run. Tests cover exact counts, the independently specified blocked ID set, totals, determinism, altered requests, altered expectations, malformed JSON, empty input, schema drift, adversarial values, Unicode, long strings, Windows paths, CLI help, provenance and write failure cleanup.

Malformed JSON produces ParseError with file and line. Missing input produces MissingInput with a usage hint. Invalid fields produce SchemaError with a field path. Bad report paths produce WriteError; the destination is replaced only after successful writing and temporary files are removed. Fixture generation may replace files in its selected output directory. The CLI processes requests.json only and does not claim YAML or CSV support. A state file is the output of run; it must not be used as an untrusted input format.

## Two-week improvement hook and verdict

No real use or two-week trial has occurred. Begin a trial by recording its start date and actual uses in a private local journal. After 14 days, hand-check all decisions in a sample and record numerator (incorrect statuses or reasons), denominator (checked requests), error rate, and actual run count. The key metric is core output accuracy against that hand-checked sample. With zero checked requests, accuracy is unmeasured. If error rate exceeds 10 percent, fix the top observed failure cause and repeat the check, or kill with a recorded reason. If unused, record that finding and kill.

The final verdict is pending the evidence window, not invented. Record expand if daily use or revenue supports it, integrate for heavy overlap with a sibling, commercialise if a buyer will pay as-is, maintain as portfolio evidence otherwise, or kill if unused or unable to meet acceptance. Trial data and results are private and not shipped. The current local acceptance evidence supports a working portfolio prototype only.
