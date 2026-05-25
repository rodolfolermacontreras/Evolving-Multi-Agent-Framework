---
sprint: PI-2 / S-B
title: qa-retro-schema-lint
owner: developer-cli-specialist-1
last_updated: 2026-05-25
---

# Agent Notes -- PI-2 / Sprint-B (Reconstructed)

Reconstructed during PI-3/S5 backfill.

## Session log
- **2026-05-16**: QA, retro, and schema-lint CLIs implemented. Batch dispatch pattern exercised.

## Surprises
- LESSON-009: Windows SQLite + tempdir tests need explicit `gc.collect()` and `ignore_cleanup_errors=True`.

## What worked
- Batch dispatch of 3 CLIs in one sprint — fleet maturity validated.

## What didn't
- (not captured at the time)

## To remember
- Windows SQLite test pattern (LESSON-009) applies to ALL future CLIs that use tempdir fixtures.
