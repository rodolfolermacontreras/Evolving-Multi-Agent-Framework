# Dedup Scan Log

Rolling log of cross-feature deduplication scans (SDD-020.R6).
One line per `cli/dedup.py scan` invocation.

Maintained automatically by `spec-driven-development/cli/dedup.py` when
invoked with `--emit-logs` (default ON). Seeded at SDD-032 close
(2026-06-09); first real entry will be appended on the next post-merge
`/triage` or `/clarify` invocation per SDD-020.R8.

| timestamp_utc | scope | candidates | overlaps | exit |
|---------------|-------|------------|----------|------|
| 2026-06-09T00:00:00+00:00 | seed | 0 | 0 | 0 |
