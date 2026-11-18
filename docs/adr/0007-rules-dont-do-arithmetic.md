# 0007: Rules don't do arithmetic

- Status: accepted
- Date: 2026-11-18

## Context

A comparison compares two operands. Some rules would like arithmetic between them, such as "price at least 5% above its 50-day average" (price ≥ 1.05 × SMA 50) or "max loss at most 2% of the account" (max loss ≤ 0.02 × account value).

## Decision

Rules stay comparisons. Any calculation becomes an indicator, or a field when it has only one possible definition: `sma_distance_ratio` with `window` 50 compared with 0.05, or `trade.max_loss_account_ratio` compared with 0.02. Each such value is named, typed and unit-checked, versioned when it is an indicator (see [ADR 0003](0003-rules-dont-pin-indicator-versions.md)), and can be shown on the ticker page and in entry snapshots.

## Considered options

- Arithmetic operand nodes, such as `{ "kind": "mul", "left": …, "right": … }`: more flexible, but unit checking gets harder (a ratio times USD is USD) and rules start holding formulas that have no version. If named indicators turn out not to give users enough room, a JSON structure for arithmetic can be revisited.
