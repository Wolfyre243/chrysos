# 0006: Per-leg checks use summary fields on the trade

- Status: accepted
- Date: 2026-11-18

## Context

Add-ons such as `liquidity_baseline` apply across structures, so their rules can't name leg slots: a calendar has `front` and `back`, a vertical `long` and `short`, an iron condor four legs. They still need per-leg checks, such as every leg having enough open interest.

## Decision

Per-leg checks read summary fields on the trade that cover every leg, such as `trade.min_leg_open_interest` (the lowest open interest of any leg) and `trade.max_leg_spread_ratio` (the widest bid-ask spread of any leg, as a fraction of its mid price). The rule format gains no new kind of node. Add-on rules can't reference leg slots unless the add-on declares the structures it applies to.

## Considered options

- An `every_leg` node whose condition runs once per leg, where a leg field without a slot means the leg being checked. More general, but a new kind of node with its own rules for what "the current leg" means. Worth adding if summary fields start to multiply.
