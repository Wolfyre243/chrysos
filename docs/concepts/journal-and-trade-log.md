# Journal and trade log

## Journal

Every trade gets a written plan before entry, and the trader's thinking is recorded as the trade plays out.

- Plan: choose a playbook, state why you're entering, answer the checklist, and set max loss, target and planned exit.
- Notes: free-form notes on a trade at any point, from planning to close.
- Feelings: the journal records how the trader felt about the trade, so emotional state can be compared with results later.

## Trade log

The record of what actually happened in each trade. Reviews, alerts and models read from it.

- Positions: one position is one trade idea from plan to close. It holds executions (open, adjust, roll, close), and P&L is tracked across all of them, so a rolled calendar stays one position. Covers stocks and options, single legs and spreads.
- Fast entry: picking a playbook pre-fills the legs using its edge's leg selectors, and entering a strike fetches the current mark for the user to correct to the real fill. Fills are entered by hand for now, so entry has to be quick or it won't be done consistently.
- Entry snapshot: when a trade opens, Chrysos saves every relevant indicator value. Self-analytics depends on these.

## Soft enforcement

Chrysos always records violations (no plan, incomplete checklist, failed entry criteria, off-plan exit, sizing breach). A per-user toggle only controls whether the UI warns about them, so review statistics stay complete either way. Trades opened without a plan are flagged as unplanned.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### TradePlan
- `id`
- `position_id` → Position (one-to-one)
- `thesis` (what the trader expects to happen)
- `entry_reason` (why enter now)
- `checklist_answers` (JSONB)
- `planned_size`
- `max_loss`
- `profit_target`
- `planned_exit`
- `is_complete` (bool)

### JournalNote
- `id`
- `position_id` → Position
- `user_id` → User
- `body`

### TradeFeeling
How the trader felt at a point in the trade. Kept apart from journal notes so self-analytics can compare feelings with results.
- `id`
- `position_id` → Position
- `execution_id` → Execution (nullable; null when recorded while planning or holding)
- `body`
- `recorded_at`

### Position
One trade idea from plan to close. Created with the plan, in status `planned`.
- `id`
- `user_id` → User
- `playbook_id` → Playbook
- `playbook_version_id` → PlaybookVersion
- `symbol` → Ticker
- `structure_key` (copied from the playbook version, for grouping)
- `edge_key` (copied from the playbook version, for grouping)
- `status` (planned, open, closed, cancelled)
- `is_planned` (bool, plan existed before first execution)
- `opened_at`
- `closed_at`
- `realized_pnl`
- `fees_total`
- `screener_result_id` → ScreenerResult (nullable, origin)
- `tags`

### Execution
- `id`
- `position_id` → Position
- `type` (open, adjust, roll, close)
- `executed_at`
- `net_amount` (debit negative, credit positive)
- `fees`
- `notes`

### ExecutionLeg
- `id`
- `execution_id` → Execution
- `instrument_type` (stock, option)
- `symbol` → Ticker
- `expiry` (options only)
- `strike` (options only)
- `right` (options only)
- `side` (buy, sell)
- `position_effect` (open, close)
- `quantity`
- `price`
- `multiplier`

### EntrySnapshot
Indicator values captured at an execution.
- `id`
- `position_id` → Position
- `execution_id` → Execution
- `captured_at`
- `spot_price`
- `values` (JSONB: indicator id → version, params, value)
- `chain_snapshot_id` → ChainSnapshot (nullable)

### RuleViolation
Always recorded, regardless of the enforcement toggle.
- `id`
- `position_id` → Position
- `execution_id` → Execution (nullable)
- `playbook_version_id` → PlaybookVersion
- `rule_ref` (rule or checklist item id)
- `violation_type` (no_plan, incomplete_checklist, entry_rule_failed, off_plan_exit, sizing_breach)
- `expected` (JSONB)
- `actual` (JSONB)
- `detected_at`
- `acknowledged` (bool)

## Related

- [Playbooks](playbooks.md) for the checklist, entry and sizing rules checked here
- [Weekly review](weekly-review.md), which grades closed trades
