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

## Related

- [Playbooks](playbooks.md) for the checklist, entry and sizing rules checked here
- [Weekly review](weekly-review.md), which grades closed trades
- Data model: [Journal](../references/data-model.md#journal), [Trade log](../references/data-model.md#trade-log)
