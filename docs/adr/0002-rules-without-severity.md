# 0002: Rules have no severity; users disable them instead

- Status: accepted
- Date: 2026-11-17

## Context

Every rule carried a `severity` (info, warning, critical), but no feature acted on it. Soft enforcement recorded violations at every level, and nothing said whether a failing `warning` entry rule removed a ticker from the screener. A field that changes nothing invites each feature to read it differently.

## Decision

- Drop `severity`. Every entry, sizing and screener rule is a plain requirement: it passes or it fails.
- A user who doesn't want a rule applied disables it rather than removing it. A disabled rule stays in its playbook, version history and diffs, but evaluation skips it, so it can be switched back on without rewriting it.

## Considered options

- Two levels on requirements: `required` (screened out, violation recorded) and `advisory` (kept in the screener but flagged, recorded as advisory, left out of the adherence score). Not built now. Worth revisiting if "nice to have" rules turn out to be useful in practice.
- Keeping info, warning and critical and defining what each does: more levels than any feature needs.
