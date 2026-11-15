# Journal and trade log

## Notes

Markdown notes the trader writes, from a trade idea jotted down while watching the news to thoughts recorded during a trade. Notes are private to their author.

- Theses: a trade idea, written whenever it comes up. The trader names it when creating it. Most theses never become trades. A thesis can be linked to any number of positions (planning a trade on it, or re-entering on the same idea after a stop-out), and a position doesn't need one.
- Journal notes: thoughts about one position as the trade plays out, written from that position and linked to it alone. A position can have any number of them, and each shows on the trade's timeline next to its fills. A blank title defaults to `{symbol} {structure} - {date}`, such as `AAPL calendar - 2026-11-20`, using the note's date (ISO, in the user's timezone). The default is filled once on first save and never rewritten.
- Mentions: typing a cashtag such as `$AAPL` mentions that ticker. A cashtag is `$` followed by a symbol that starts with a letter (`$BRK.B` works, `$230` is ignored); it's case-insensitive and stored uppercase. On save, each symbol is checked against the market data provider and added to the ticker cache. A cashtag that doesn't resolve stays plain text, and the UI warns about it. Mentions link both ways: a note lists the tickers it mentions, and the ticker page lists the notes that mention it.
- Hashtags: `#earnings` or `#macro` tags a note. A hashtag is `#` directly followed by a word that starts with a letter (`# Heading` stays a markdown heading), stored lowercase. Hashtags also mark observations and outside factors on a stock, such as `#risk` or `#tailwind`.
- Cashtags and hashtags inside code spans and code blocks are ignored. Mentions and tags are rebuilt from the text on every save.
- Editing: notes can be edited at any time. The UI marks a note as edited once it changes after creation. There's no edit history.
- Archiving: archiving hides a note from note lists, search and the ticker page, and moves it to an archived view where it can be restored. Its mentions, tags and position links are kept, so restoring loses nothing. A position page still shows its archived notes, marked as archived, so a trade's history never disappears. Notes are never deleted from the app.
- Ticker page: the notes panel shows notes mentioning the ticker plus notes linked to positions on it, so a journal note that never types the cashtag still shows up.
- Research: a ticker's [research file](analytics.md#research-files) is its business summary plus the notes that mention it.

## Journal

Every trade can get a written plan before entry, and the trader's thinking is recorded as the trade plays out.

- Plan: choose a playbook (one of your own or any [public playbook](playbooks.md#public-playbooks)), state why you're entering now, answer the checklist, and set size, max loss, target and planned exit. Linking a thesis, or writing a new one from the plan, is optional so entry stays quick. A plan is complete once its checklist is answered.
- Journal notes: see [notes](#notes).
- Feelings: at each fill (open, adjust, roll, close), the trader can record how they felt: an emotion from a fixed list, an intensity from 1 to 5 and an optional comment. A fill can have several (anxious and FOMO at once). Feelings are only recorded at fills, so self-analytics can compare them with what each fill led to.

## Trade log

The record of what actually happened in each trade. Reviews, alerts and models read from it.

- Positions: one position is one trade idea from plan to close. It holds executions (open, adjust, roll, close), and P&L is tracked across all of them, so a rolled calendar stays one position. Covers stocks and options, single legs and spreads. Every leg is on the position's underlying; a pairs trade is two positions.
- Fast entry: picking a playbook pre-fills the legs using its edge's leg selectors, and entering a strike fetches the current mark for the user to correct to the real fill. Fills are entered by hand for now, so entry has to be quick or it won't be done consistently.
- Entry snapshot: when a trade opens, Chrysos saves every relevant indicator value. Self-analytics depends on these.
- Playbook version: each position records the playbook version it was entered under and is managed under it until it closes, even if the playbook is edited meanwhile. The playbook, structure and edge are all reached through that version.
- Derived values: status, open and close times, P&L, fees, whether the trade was planned and whether its plan is complete are computed from the executions, the plan and the playbook version, never stored, so they can't drift from the fills. They come from the [`position_summary`](#position_summary) view.
  - Status: planned (no executions yet), open (some contract still has a net quantity), closed (it has executions and every contract nets to zero), cancelled (the plan was dropped before any execution).
  - Realized P&L is worked out per contract: once a contract's net quantity is back to zero, its cash flows are realized. A roll therefore realizes the legs it closes while the new legs stay open.

## Soft enforcement

Chrysos always records violations, at the fill where each is detected:

- No plan and incomplete checklist: at the first open.
- Failed entry criteria and sizing breach: at an open or adjustment.
- Off-plan exit: at the close. An option that expires is entered as a close at zero.

A per-user toggle only controls whether the UI warns about them, so review statistics stay complete either way. Checks while planning are live warnings in the UI and aren't stored, since a plan that is never traded has nothing to review. Trades opened without a plan are flagged as unplanned.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

These tables are normalized to third normal form. Anything that can be derived from other rows lives in the `position_summary` view instead of a column. The one accepted break is `ExecutionLeg.multiplier`.

### Note
A thesis or a journal note. Private to its author.
- `id`
- `user_id` → User
- `type` (thesis, journal)
- `title` (required; a thesis is named at creation, a blank journal title gets the default format)
- `body` (markdown)
- `archived_at` (nullable)

### PositionNote
Links notes to positions. Primary key (`position_id`, `note_id`). A thesis can be linked to many positions. A journal note is linked to exactly one, created together with the note; the app enforces this. The note and the position must belong to the same user.
- `position_id` → Position
- `note_id` → Note

### NoteTicker
The tickers a note mentions, rebuilt from its body on every save. Primary key (`note_id`, `symbol`).
- `note_id` → Note
- `symbol` → Ticker

### NoteTag
The hashtags in a note, rebuilt from its body on every save. Primary key (`note_id`, `tag`). There is no tag table, since a tag has no attributes of its own.
- `note_id` → Note
- `tag` (lowercase)

### TradePlan
- `id`
- `position_id` → Position (one-to-one)
- `entry_reason` (why enter now)
- `checklist_answers` (JSONB)
- `planned_size`
- `max_loss`
- `profit_target`
- `planned_exit`

### Position
One trade idea from plan to close. Created with the plan in status planned, or at its first execution when the trade is unplanned.
- `id`
- `user_id` → User
- `playbook_version_id` → PlaybookVersion (entered under; management rules are checked against this version, and the playbook, structure and edge are reached through it)
- `symbol` → Ticker (the underlying; every leg is on it)
- `screener_result_id` → ScreenerResult (nullable, origin)
- `cancelled_at` (nullable; set when a plan is dropped before any execution)

### Execution
- `id`
- `position_id` → Position
- `type` (open, adjust, roll, close)
- `executed_at`
- `fees`

### ExecutionLeg
One leg of a fill. The contract is described on the leg itself; there is no contract table.
- `id`
- `execution_id` → Execution
- `instrument_type` (stock, option)
- `expiry` (options only)
- `strike` (options only)
- `right` (options only)
- `side` (buy, sell)
- `position_effect` (open, close)
- `quantity`
- `price`
- `multiplier` (defaults to 100 for options and 1 for stock, editable so adjusted contracts can be entered correctly)

`multiplier` belongs to the contract rather than the leg, so it repeats on every leg of the same contract. This is the one accepted break from third normal form: a contract table would hold it properly, but it isn't worth the extra entity.

### TradeFeeling
How the trader felt at a fill. Kept apart from notes so self-analytics can compare feelings with results.
- `id`
- `execution_id` → Execution
- `emotion` (calm, confident, anxious, fearful, greedy, fomo, frustrated, bored)
- `intensity` (1 to 5)
- `comment` (nullable)

### EntrySnapshot
Indicator values captured at an execution.
- `id`
- `execution_id` → Execution
- `captured_at`
- `spot_price`
- `values` (JSONB: indicator id → version, params, value)
- `chain_snapshot_id` → ChainSnapshot (nullable)

### RuleViolation
Always recorded, regardless of the enforcement toggle. Checked against the playbook version of the execution's position; `created_at` is when it was detected.
- `id`
- `execution_id` → Execution
- `rule_ref` (rule or checklist item id)
- `violation_type` (no_plan, incomplete_checklist, entry_rule_failed, off_plan_exit, sizing_breach)
- `expected` (JSONB)
- `actual` (JSONB)
- `acknowledged` (bool)

### position_summary
*(view)* One row per position, computed on read from its executions, legs, plan and playbook version. Nothing in it is stored.
- `position_id`
- `playbook_id`, `structure_key`, `edge_key` (from the playbook version, for grouping)
- `status` (planned, open, closed, cancelled)
- `opened_at` (first execution)
- `closed_at` (last execution, once closed)
- `realized_pnl`
- `fees_total`
- `is_planned` (the plan was created before the first execution)
- `is_plan_complete` (every checklist item is answered)

Each execution's net amount (debit negative, credit positive) is computed the same way: the sum over its legs of quantity × price × multiplier, signed by side.

## Related

- [Playbooks](playbooks.md) for the checklist, entry and sizing rules checked here
- [Weekly review](weekly-review.md), which grades closed trades
- [Analytics](analytics.md) for the ticker page and research files
