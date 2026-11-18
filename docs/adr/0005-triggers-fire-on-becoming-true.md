# 0005: Triggers fire when they become true, with a cooldown

- Status: accepted
- Date: 2026-11-18

## Context

A trigger is a rule read on its own, such as a management rule or a user's alert rule: a true result raises an alert. Triggers are evaluated again and again, so a rule that stays true for days, or a value that hovers around its threshold, could raise the same alert over and over.

## Decision

- A trigger fires when its result goes from false to true for a subject (one ticker or one position).
- After firing, it can't fire again until it has been false and the cooldown since its last firing has passed.
- Unknown results neither fire nor count as false, so a data outage between two true results doesn't raise a second alert.
- The cooldown belongs to whatever raises the alert, never to the rule, so a rule has the same format wherever it is used.
- Alerts report changes. Whether a rule is still true is shown as current rule status, on the position page and in session digests.

## Considered options

- Fire on every evaluation while true, limited only by the cooldown: too noisy for a profit target that stays reached for days.
- Fire on becoming true, with no cooldown: a value hovering around its threshold fires on every crossing.

## Future options

Other firing modes could later be offered per alert: on every evaluation while true, at most once a day, or once only (fire, then switch off).
