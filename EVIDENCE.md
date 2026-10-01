# Local acceptance evidence

Measured on 2026-10-01 with Python 3.12.10 on this Windows machine.

The installed hop executable completed fixtures, run and Markdown report in 0.846 seconds total, including process startup. Target: under 5 seconds. This is a measured local run, not a performance guarantee or a time-savings baseline.

The labelled synthetic fixture contains 200 requests. Independent hand arithmetic: 20 groups of ten, each with four eligible, four blocked, one denied and one pending. Expected counts: 80 eligible, 80 blocked, 20 denied, 20 pending. Each declared amount is 100 minor units, yielding 20000 total. Exact blocked ID membership is checked independently in tests. No false positives or missed planted blocks on this fixture.

31 pytest cases passed. Altering a request changed its status and total; altering expectation metadata had no effect. Two identical runs produce byte-identical reports. The five-request synthetic example and empty-directory path also complete.

Boundary: all acceptance inputs are synthetic, roles and identities are asserted in input, no infrastructure actions were executed, and real effectiveness remains unmeasured. The two-week verdict is pending real-use evidence.
