---
name: respect-existing
description: "Use during any worker dispatch in a brownfield host project. Constrains the worker from rewriting code outside the explicit task scope, even when the existing code seems suboptimal. Existing conventions stay; SDD wraps them, does not replace them."
argument-hint: "Which file or scope are you currently working in?"
license: MIT
metadata:
  author: emf-framework
  version: '1.0'
---

# Respect Existing

Brownfield work succeeds only when the host team can trust SDD to improve delivery without disrupting code, conventions, and history that already work.

## Why This Matters

In a brownfield host, the project already has working code, tests, style, naming, folder structure, CI behavior, and team expectations. Some of those patterns may look suboptimal from the outside. That is not permission to replace them.

SDD wraps the existing project. It does not erase it. A worker who rewrites unrelated code creates review noise, breaks local knowledge, invalidates archaeology, and makes adoption feel unsafe.

## Canonical Instruction

Modify only the files and behavior required by the explicit task scope. Read the local pattern first, mimic it, and leave unrelated improvements for a separate approved decision.

## Protocol

1. Identify the exact file, function, module, or behavior assigned to you.
2. Read nearby code before editing.
3. Follow the existing naming, layout, error handling, imports, test style, and formatting.
4. Add only the smallest change that satisfies the task.
5. Add focused tests in the existing test style when the task requires code behavior changes.
6. Do not move, rename, reorganize, or modernize unrelated code.
7. Do not introduce a new framework, package manager, formatter, linter, or architectural pattern unless the task explicitly says to.
8. Report any suspicious existing pattern as a lesson-capture candidate instead of fixing it inline.

## What Not To Do

- Do not rewrite a module because you think it is messy.
- Do not collapse duplication outside your task scope.
- Do not convert style conventions to your preferred style.
- Do not rename public APIs unless the task explicitly requires it.
- Do not reorganize tests, folders, CI, or package files as a drive-by improvement.
- Do not silently expand the task because the existing code annoys you.

## Escape Hatch

If you genuinely cannot complete the task without touching out-of-scope code, stop.

Route the issue to the Architect with:

- The assigned task scope.
- The out-of-scope file or subsystem blocking the work.
- The exact reason the blocker prevents completion.
- The smallest architectural decision needed to proceed.

Do not make the out-of-scope change first and explain later.

## Captures-as-Lesson Hatch

If an existing pattern is genuinely harmful but does not block the task, leave it alone and file a `lesson-capture` candidate.

Capture:

- The pattern observed.
- Where it appears.
- Why it may hurt future SDD work.
- Whether it should become a future refactor, domain skill, ADR, or constitution amendment.

The lesson can become planned work. It is not part of your current task unless explicitly accepted.

## Compliance Example

Task: Add a new parser for `InvoiceUpdated` events.

Observation: Two existing event parsers duplicate date parsing logic.

Compliant behavior: You add the third parser using the same local pattern, include focused tests, and note a lesson-capture candidate that date parsing is duplicated. You do not refactor all parsers in the same patch.

## Escape Example

Task: Add a new route that requires authenticated user context.

Observation: The target module has no safe way to access user identity, and every nearby route bypasses the required authorization check.

Compliant behavior: You stop and route to the Architect. You report that completing the route safely requires an authentication-context decision outside the assigned route file. You do not invent a new auth helper inline.

## Completion Checklist

Before reporting done:

- The diff is limited to the assigned scope.
- Local patterns were followed even if they were imperfect.
- Any out-of-scope concern was routed or captured, not fixed inline.
- Tests or verification match the host's existing conventions.
