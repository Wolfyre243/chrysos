# 0003: Rules don't pin indicator versions

- Status: accepted
- Date: 2026-11-17

## Context

Playbook versions freeze their rules, so an open position is managed under the rules it was entered with. Those rules reference indicators from the analytics registry, and each indicator has a `version` that is bumped whenever its formula changes. A rule could reference `forward_factor` or pin `forward_factor` at a given version.

## Decision

Rules reference indicators by id only. Evaluation always uses the indicator's current version, and every stored result (entry snapshots, violations) records the version it was computed with. Pinning would mean keeping every old formula runnable for as long as any position or playbook version refers to it.

## Consequences

- Caveat: a frozen playbook version freezes its rules and parameters, not the formulas behind them. When an indicator's formula changes, open positions are managed with the new formula, and thresholds tuned under the old one (such as `ff_min = 0.2`) may need revisiting.
- Self-analytics only compares stored values within one indicator version, so a formula change splits the history at that point.
- Not designed yet: telling users when an indicator their playbooks use has changed, for example by listing it next to block updates in the weekly review.
