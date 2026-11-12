# Weekly review and self-analytics

Learning from the user's own trades.

## Weekly review

Scheduled, mostly generated, and about 15 minutes long.

- Shows results and rule adherence by playbook, structure and edge.
- The user grades each closed trade's process from A to F. Grades are crossed with outcome: a good process with a loss counts as variance, and a bad process with a win is flagged hardest.
- Checks open positions against their plans and takes a short reflection.
- Applies or rejects pending playbook change proposals (see [playbooks](playbooks.md#parameters-and-changes)).
- Ends with one commitment that the next review checks.

Reviews lock on submission, completed reviews build a streak, and monthly and quarterly views roll up from them.

## Self-analytics

Once enough trades exist, outcomes are compared against entry conditions. For example, do FF calendars entered with FF > 0.3 do better than those entered with FF > 0.2? Results can be grouped by edge across structures (how do IV crush trades do, whatever the structure?) or by structure across edges. This works because every trade carries its entry snapshot, playbook version, structure and edge. Sizing history is charted here too.

## Models (later)

Once enough data exists, two kinds of model can build on it:

- On the user's trades: an ML model or LLM that reads the trade log (entry snapshots, playbook versions and outcomes) and finds which entry conditions go with good results, extending self-analytics.
- On market history: a custom model trained on stored chain snapshots and backtests that recognises past patterns when they show up again.

Findings reach the user as playbook change proposals in the weekly review, where they are applied or rejected like any other proposal.

## Related

- [Journal and trade log](journal-and-trade-log.md), the data the review reads
- Data model: [Weekly review](../references/data-model.md#weekly-review), [PlaybookChangeProposal](../references/data-model.md#playbooks-and-rules)
