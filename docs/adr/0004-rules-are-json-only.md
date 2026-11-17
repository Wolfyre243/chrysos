# 0004: Rules are written and stored as JSON only

- Status: accepted
- Date: 2026-11-17

## Context

A rule is a condition tree. Users write theirs in the frontend; playbook versions, screeners and alert rules store them as JSONB; and blocks (structures, edges, add-ons) ship default rules in code. A Python builder (`gt(...)`, `param(...)`, `forward_factor(...)`) was considered for writing block rules, next to the JSON format.

## Decision

JSON is the only way a rule is written, stored or exported. Pydantic models parse JSON into a rule tree and dump the tree back to JSON; validation and evaluation work on the tree. Block rules are written as JSON too, and every block's rules go through the same checks as a saved rule, at startup and in tests. There is no Python builder.

## Considered options

- A Python builder for block rules: shorter to write, and the editor catches misspelt function names. Rejected because it is a second way to express the same rule, and what a block author writes would no longer be what is stored and exported.

## Consequences

- A rule looks the same everywhere: in a block, a playbook version, a screener, an alert rule, the API and an export.
- Block rules are longer to write by hand, and a typo in one surfaces in tests rather than in the editor.
