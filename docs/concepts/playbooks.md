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

Thresholds are named parameters, not numbers written into rules: a rule says FF > `ff_min`, and the playbook sets `ff_min` to 0.2. Parameters are also what backtesting sweeps when looking for the best configuration of a playbook.

Every edit applies as soon as it is saved, whether it changes a parameter value or the structure, edge, add-ons, rules or checklist:

- One save is one version. The editor keeps unsaved edits as a draft, and saving writes a single new version covering everything that changed, however many parameters and rules that is. A save that changes nothing creates no version.
- Each version stores a diff against the one before it, so history shows what changed without comparing snapshots by hand.
- If the latest version isn't referenced yet (no position, screener run or rule violation points at it), saving amends it in place instead of adding another version, so a burst of tweaks doesn't pile up versions. Once anything references a version, it is frozen.
- Each trade records the version it was entered under, and an open position is always managed under that version. Its management rules, alerts and digest suggestions keep using the rules it was entered with, so editing a playbook never rewrites the rules of a trade in progress. New entries use the current version.

Every playbook has a read-only version history: number, date, source, note, the diff, and how many of the user's positions were entered under each version. There is no revert; to go back, the user sets the old values again and saves.

Findings from self-analytics and models don't change playbooks. They appear as [suggestions](weekly-review.md#playbooksuggestion) in the weekly review, and the user makes any change by hand.

## Composition and storage

- Presets are named combinations defined in code.
- Overrides store only what the user changed: parameter values, disabled rules, extra user rules and checklist items, and edits to individual rules. They are keyed by the block and rule id they apply to.
- Resolving a playbook merges structure, edge and add-ons in that order, applies the overrides, and tags every resulting rule and checklist item with its `source` (edge, add-on or user). Violations and adherence stats can then point at the block a broken rule came from.
- Every saved change creates a version (see above) recording the version of each block and the resolved rules, selectors and parameters.
- When a block's version is bumped in code, improvements still reach fields the user hasn't overridden: new parameter defaults, and new or changed rules, selectors and checklist items. The deploy is the decision, so these apply automatically. A deploy writes one `block_update` version per affected playbook, covering every block bumped in that deploy, and the weekly review lists it under what changed that week.
- If a bump removes or renames a rule the user has an override on, the override is orphaned. It is kept and flagged on the playbook page and in the weekly review, never dropped silently.

## Public playbooks

A playbook is private by default. Its owner can make it public, like a [watchlist](market-data.md#watchlists), so a small group doesn't have to build the same strategy several times.

- Any user can choose a public playbook when planning a trade. Their positions, journals, stats and self-analytics stay private to them.
- Only the owner edits a public playbook. Edits and block updates apply to everyone using it, while each open position stays on the version it was entered under.
- A user who wants different settings creates their own playbook, usually from the same [preset](#playbookpreset). There is no fork or follow link between playbooks.
- Once another user has a position on a public playbook, it can't be made private or deleted, so their trades always point at something they can see. The owner archives it instead (`is_active = false`): no new entries and no screener, but existing references still resolve. A public playbook nobody else has used can be switched back to private or deleted freely.
- A public playbook can have one public screener, whose hits go to the shared Discord server (see [screener](screener.md#public-and-private-screeners)).

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### Structure
*(code)* What is traded: the legs and their mechanics.
- `key` (calendar, vertical, diagonal, double_calendar, iron_condor, iron_fly, straddle, stock, …)
- `version`
- `name`
- `legs` (named slots with side, right, quantity ratio)
- `selector_slots` (what an edge must fill, such as `front_expiry`, `back_expiry`, `strike`, `right`)
- `exposes` (fields rules can read, such as `legs.front.dte`, `net_debit`, `max_loss`)
- `actions` (lifecycle actions, such as `roll(front)`)

### Edge
*(code)* Why the trade is taken.
- `key` (forward_factor, earnings_iv_crush, …)
- `version`
- `name`
- `structures` (compatible structure keys)
- `params_schema` (name, type, default, allowed range, description)
- `selectors` (leg selector binding per compatible structure)
- default entry rules, management rules, sizing rules, checklist

### Addon
*(code)* Cross-cutting rule pack. Adds rules only; never sets selectors.
- `key` (liquidity_baseline, risk_2pct, checklist_core, …)
- `version`
- `name`
- `structures` (optional; applies to all when empty)
- `params_schema`
- default rules and checklist items

### PlaybookPreset
*(code)* A named starting combination, such as "FF calendar".
- `key`
- `name`
- `structure_key`
- `edge_key`
- `addon_keys`
- `param_defaults` (optional, on top of the blocks' defaults)

### Playbook
A user's combination of one structure, one edge and any add-ons. `structure_key`, `edge_key` and `addon_keys` mirror the current version.
- `id`
- `user_id` → User (owner; the only user who can edit it)
- `name`
- `visibility` (public, private; can't return to private once another user has a position on it)
- `preset_key` (nullable; null when built from scratch)
- `structure_key`
- `edge_key` (must list `structure_key` as compatible)
- `addon_keys`
- `current_version_id` → PlaybookVersion
- `is_active` (false when archived: no new entries or screener runs)

### PlaybookVersion
Snapshot of the effective playbook at a point in time, written by one save. Frozen once a position, screener run or rule violation references it; until then a later save amends it in place.
- `id`
- `playbook_id` → Playbook
- `version_number`
- `structure_key`, `structure_version`
- `edge_key`, `edge_version`
- `addons` (JSONB: add-on key → version)
- `params` (JSONB, resolved values: block defaults plus user overrides)
- `overrides` (JSONB, user changes keyed by block and rule id: parameter values, disabled rules, edited rules, extra user rules and checklist items)
- `selectors` (JSONB, resolved leg selectors for the structure)
- `entry_rules` (JSONB, resolved)
- `checklist` (JSONB, resolved)
- `management_rules` (JSONB, resolved)
- `sizing_rules` (JSONB, resolved)
- `source` (initial, user, block_update)
- `changes` (JSONB, diff against the previous version: a list of `{kind, key, from, to}` where `kind` is param, block, rule or checklist)
- `note` (optional, why the change was made)

### ChecklistItem
*(value object, stored as JSONB)*
- `id`
- `prompt`
- `answer_type` (text, bool, number)
- `required`
- `source` (`edge:<key>`, `addon:<key>` or `user`)

## Related

- [Rule engine](rule-engine.md) for the rule format, `$legs` and `$params` references
- [Screener](screener.md), [journal and trade log](journal-and-trade-log.md) and [weekly review](weekly-review.md), which all read playbooks
- [Users and access](users-and-access.md) for what public playbooks share and what stays private
- [Rule](rule-engine.md#rule), the value object stored in `PlaybookVersion`
- [PlaybookSuggestion](weekly-review.md#playbooksuggestion), findings about a playbook shown in the weekly review
- [ADR 0001](../adr/0001-public-playbooks-without-change-proposals.md) for why there are no change proposals or forks
