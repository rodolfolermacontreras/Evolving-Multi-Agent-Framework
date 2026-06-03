# Level-2 Decision Brief: {TITLE}

- Date: {YYYY-MM-DD}
- Proposing Principal: {ROLE}
- Trigger: {WHAT_TRIGGERED_THIS}
- Requested approval from: Rodolfo (human)
- Related ADR (drafted on approval): ADR-{NNN}
- Status: **Pending human approval**

> Every Level 2 decision (per `decision-policy.md`) MUST submit this brief
> before approval. Fill in all five sections. Empty sections must say "none"
> with a one-sentence justification. Keep this brief to one page. After
> approval, the human signs off below and the decision is recorded as an ADR
> that links back to this file.

---

## 1. Money cost (one-time + recurring)

- One-time: {DOLLAR_AMOUNT_OR_NONE}
- Recurring (monthly): {DOLLAR_AMOUNT_OR_NONE}
- Recurring (annual): {DOLLAR_AMOUNT_OR_NONE}
- Cost source / quote: {LINK_OR_REFERENCE}

If "none", justify in one sentence: {WHY_FREE}.

## 2. Complexity cost (added moving parts; new dependencies)

- New runtime dependency: {NAME_AND_VERSION_OR_NONE}
- New service / external integration: {NAME_OR_NONE}
- New agent role: {ROLE_OR_NONE}
- New failure modes introduced: {LIST_OR_NONE}

If "none", justify in one sentence: {WHY_NO_NEW_PARTS}.

## 3. Maintenance burden (who maintains; cadence of upkeep)

- Owner of new surface: {PRINCIPAL_OR_HUMAN}
- Upkeep cadence: {WEEKLY_MONTHLY_QUARTERLY_AS_NEEDED}
- What happens if the owner is unavailable: {FALLBACK_PLAN}
- Estimated upkeep effort per cadence: {HOURS_OR_TASKS}

## 4. Expected benefit (concrete, measurable where possible)

- Primary benefit: {ONE_SENTENCE}
- How measured: {METRIC_OR_QUALITATIVE_INDICATOR}
- Who benefits: {ROLE_OR_STAKEHOLDER}
- Timeframe to realize: {IMMEDIATE_OR_PI_OR_LONGER}

Vague benefits (e.g. "better velocity", "more flexibility") will be flagged
at the approval gate. Replace with a measurable statement.

## 5. Alternatives considered (cheaper paths evaluated and why rejected)

At least one alternative MUST be evaluated. "We considered no alternatives"
is not an acceptable answer.

- **Alternative A: {NAME}** -- Cost / complexity: {SHORT}. Rejected because:
  {ONE_SENTENCE}.
- **Alternative B: {NAME}** -- Cost / complexity: {SHORT}. Rejected because:
  {ONE_SENTENCE}.
- **Alternative C (do nothing): {WHAT_NULL_OPTION_LOOKS_LIKE}** -- Rejected
  because: {ONE_SENTENCE}.

---

## Human approval

- [ ] Approved by Rodolfo on {YYYY-MM-DD}
- [ ] Rejected (with reason): {REASON}
- [ ] Deferred (re-submit after): {CONDITION}

On approval, drafting Principal records the decision in
`spec-driven-development/docs/ADR/{NNN}-{slug}.md` and links back to this
brief in the ADR's `Related` field.
