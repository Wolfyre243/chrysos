# Playbooks

A playbook is one strategy written as rules. Each part is read by a different layer:

- Entry criteria: conditions a trade must meet, such as FF > 0.2 or no earnings between expirations. The screener uses them as filters, and each new trade is checked against them.
- Pre-trade checklist: questions to answer before entering, such as thesis, max loss and planned exit.
- Management rules: when to take profit or close, such as +25% or 7 DTE before front expiry. The alerts engine checks open positions against them.
- Sizing rules: limits such as the maximum share of the account per trade. Every entry is checked against them, and sizing over time is charted to show trading habits.
- Leg selection: the trade's structure and how its expiries and strikes are picked, used to pre-fill entry and to tell the screener which part of the chain to fetch.

All of these rules use the shared format described in [rule-engine.md](rule-engine.md).

## Building blocks

A playbook is not one fixed template. It is put together from blocks defined in code, because what a trade is and why it is taken are separate choices:

- Structure: what is traded, meaning the legs. Calendar, vertical, diagonal, iron condor, straddle, plain stock. A structure knows its leg slots (such as `front` and `back`), its P&L and max-loss maths, and what a roll means.
- Edge: why the trade is taken, meaning the mispricing or event being bet on. Forward factor (term-structure mispricing) and earnings IV crush are the first two. An edge brings the entry and management rules, the checklist items, the leg selectors (how expiries and strikes are picked), and named parameters such as `ff_min`. It lists the structures it works with.
- Add-ons: small rule packs that apply across edges, such as a liquidity baseline (open interest, bid-ask width), a 2% risk sizing rule, or a core checklist.

All three kinds of block are registered and versioned in code like analytics plugins. Users choose and combine blocks; they don't define new ones in the UI.

A playbook is one structure, exactly one edge, any number of add-ons, plus the user's parameter overrides and extra rules. Only the edge picks the legs; add-ons only add rules, so blocks never compete over leg selection.

The same structure can carry different edges, and the same edge can sit on different structures:

| Playbook           | Structure       | Edge                |
| ------------------ | --------------- | ------------------- |
| FF calendar        | calendar        | `forward_factor`    |
| IV crush calendar  | calendar        | `earnings_iv_crush` |
| IV crush condor    | iron condor     | `earnings_iv_crush` |
| FF double calendar | double calendar | `forward_factor`    |

Presets are ready-made combinations (such as "FF calendar" = calendar + `forward_factor` + liquidity baseline + 2% risk) that users start from. Users can also put together their own combination from any compatible structure, edge and add-ons.

### Structures

What is traded. Each structure declares:

| Field            | Meaning                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------ |
| `key`, `name`    | Identifier and display name (`calendar`, `vertical`, `iron_condor`, `stock`, …)            |
| `version`        | Bumped whenever legs, maths or exposed fields change                                       |
| `legs`           | Named leg slots with side, right and quantity ratio (calendar: `front` sells, `back` buys) |
| `selector_slots` | The slots the edge must fill (calendar: `front_expiry`, `back_expiry`, `strike`, `right`)  |
| `exposes`        | Fields rules can read (`legs.front.dte`, `net_debit`, `max_loss`, width, …)                |
| `actions`        | Lifecycle actions the trade log understands (calendar: `roll(front)`)                      |

Structures own the mechanics: building the legs, P&L and max-loss maths, adding up greeks, and what an adjustment or roll means for a position.

### Edges

Why the trade is taken. Each edge declares:

| Field           | Meaning                                                                |
| --------------- | ---------------------------------------------------------------------- |
| `key`, `name`   | Identifier and display name (`forward_factor`, `earnings_iv_crush`, …) |
| `version`       | Bumped whenever rules, selectors or parameter defaults change          |
| `structures`    | Structures the edge works with                                         |
| `params_schema` | Parameter schema: name, type, default, allowed range, description      |
| `selectors`     | Leg selectors per supported structure                                  |
| `rules`         | Default entry, management and sizing rules                             |
| `checklist`     | Default checklist items                                                |

Selectors are data, so fast entry, the screener and backtests all pick legs the same way. Expiry selectors include `nearest(dte=…)`, `first_after(event)` and `next_after(slot, min_gap=…)`; strike selectors include `atm`, `delta(…)`, `pct_otm(…)` and `expected_move(…)`. Because structures have different slots (a condor has one expiry, a calendar two), an edge gives one selector binding per structure it supports rather than a single universal set.

Example: `forward_factor` on a calendar picks `front_expiry = nearest(dte=$params.front_dte)`, `back_expiry = nearest(dte=$params.back_dte)` and an ATM strike, enters when FF > `ff_min` with no earnings between the legs, and closes at `exit_front_dte`. `earnings_iv_crush` on a calendar picks `front_expiry = first_after(earnings)` and `back_expiry = next_after(front, min_gap=21d)`, enters within `entry_days` of the report, and closes the day after it.

### Add-ons

Small rule packs that apply across edges (`liquidity_baseline`, `risk_2pct`, `checklist_core`). They declare `key`, `version`, `params_schema`, `rules` and `checklist`, and optionally the structures they apply to. Add-ons only add rules; they never set selectors.

## Parameters and changes

Thresholds are named parameters, not numbers written into rules: a rule says FF > `ff_min`, and the playbook sets `ff_min` to 0.2. This splits changes cleanly:

- Threshold changes: changing a parameter value. They apply immediately.
- Structural changes: changing the structure, edge or add-ons, or adding, removing or rewriting a rule. They are stored as a proposal until the weekly review applies or rejects it, so rules don't get rewritten in the middle of a trade.

Every change creates a new version, and each trade records the version it was entered under. Parameters are also what backtesting sweeps when looking for the best configuration of a playbook.

## Composition and storage

- Presets are named combinations defined in code.
- Overrides store only what the user changed: parameter values, disabled rules, extra user rules and checklist items, and edits to individual rules. They are keyed by the block and rule id they apply to.
- Resolving a playbook merges structure, edge and add-ons in that order, applies the overrides, and tags every resulting rule and checklist item with its `source` (edge, add-on or user). Violations and adherence stats can then point at the block a broken rule came from.
- Every playbook change creates a new immutable version recording the version of each block and the resolved rules, selectors and parameters.
- When a block's version is bumped in code, improvements still reach fields the user hasn't overridden. Playbooks using it pick up new parameter defaults for parameters they haven't overridden in a new `block_update` version, which applies immediately like a threshold change. New or changed rules and selectors arrive as change proposals (source `block_update`) for the next weekly review.

## Related

- [Rule engine](rule-engine.md) for the rule format, `$legs` and `$params` references
- [Screener](screener.md), [journal and trade log](journal-and-trade-log.md) and [weekly review](weekly-review.md), which all read playbooks
- Data model: [Playbooks and rules](../references/data-model.md#playbooks-and-rules)
