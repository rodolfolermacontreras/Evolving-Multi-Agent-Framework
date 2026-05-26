# docs/Temp/ -- DEPRECATED

**This folder is deprecated as of PI-3/S5 (ADR-0011).**

All sprint detail documents have been migrated to the three-tier navigation
layer under `docs/Management/`:

```
docs/Management/
  PI-N/
    INDEX.md                          <- PI-level navigation
    Sprint-N-{title}/
      SPEC.md                         <- was SPRINT_#_DETAILED_*.md
      AGENT_NOTES.md                  <- on-the-ground notes from workers
```

**Do not add new sprint detail documents to this folder.** Per Rule 13
(RULES.md v1.1.0): "No work on a sprint without a corresponding
`Management/PI-#/Sprint-#-{title}/` folder and tracker entry."

## Where things moved

| Old location | New location |
|---|---|
| `SPRINT_1_DETAILED_DASHBOARD_FRESHNESS_UNBLOCK.md` | `Management/PI-3/Sprint-1-dashboard-freshness-unblock/SPEC.md` |
| `SPRINT_2_DETAILED_DAY_TO_DAY_BROWNFIELD_BOOTSTRAP.md` | `Management/PI-3/Sprint-2-day-to-day-brownfield-bootstrap/SPEC.md` |
| `SPRINT_3_DETAILED_PI2_LESSONS_CURATION.md` | `Management/PI-3/Sprint-3-pi2-lessons-curation/SPEC.md` |
| `SPRINT_4_DETAILED_LIVE_UI_V2_SPEC.md` | `Management/PI-3/Sprint-4-live-ui-v2-spec/SPEC.md` |
| `SPRINT_5_DETAILED_MANAGEMENT_NAVIGATION_LAYER.md` | `Management/PI-3/Sprint-5-management-navigation-layer/SPEC.md` |

## See also
- [ADR-0011: Three-Tier Navigation Layer](../ADR/011-three-tier-navigation-layer.md)
- [HIGH_LEVEL_DEV_TRACKER.md](../HIGH_LEVEL_DEV_TRACKER.md)
