# Weekly review and self-analytics

Learning from the user's own trades.

## Weekly review

Scheduled, mostly generated, and about 15 minutes long. The review is private, so its reminder is an in-app notification once those exist; until then the review shows as due in the app.

- Shows results and rule adherence by playbook, structure and edge.
- The user grades each closed trade's process from A to F. Grades are crossed with outcome: a good process with a loss counts as variance, and a bad process with a win is flagged hardest.
- Checks open positions against their plans and takes a short reflection.
- Lists what changed this week in the playbooks the user trades: their own edits, owner edits to public playbooks they use, and `block_update` versions from deploys, plus any orphaned overrides (see [playbooks](playbooks.md#parameters-and-changes)).
- Shows suggestions from self-analytics and models. The user reads them and makes any playbook change by hand; there is no apply button.
- Ends with one commitment that the next review checks.

Reviews lock on submission, completed reviews build a streak, and monthly and quarterly views roll up from them.

## Self-analytics

Once enough trades exist, outcomes are compared against entry conditions. For example, do FF calendars entered with FF > 0.3 do better than those entered with FF > 0.2? Results can be grouped by edge across structures (how do IV crush trades do, whatever the structure?) or by structure across edges. This works because every trade carries its entry snapshot, playbook version, structure and edge. Sizing history is charted here too.

Self-analytics only ever reads the reviewing user's own trades, including trades on other users' public playbooks. It never combines several users' trades, even on a shared playbook, because journals and positions are private.

## Models (later)

Once enough data exists, two kinds of model can build on it:

- On the user's trades: an ML model or LLM that reads the trade log (entry snapshots, playbook versions and outcomes) and finds which entry conditions go with good results, extending self-analytics.
- On market history: a custom model trained on stored chain snapshots and backtests that recognises past patterns when they show up again.

## Suggestions

Findings from self-analytics and models reach the user as suggestions in the weekly review. A suggestion names a playbook, states the finding and keeps the evidence behind it. It never changes the playbook: the user decides, edits the playbook by hand, and marks the suggestion done (linking the version that resulted) or dismissed. Linking the resulting version lets later reviews check whether acting on suggestions helped.

A suggestion about another user's public playbook says so, since only its owner can edit it. The user can raise it with the owner or create their own playbook.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### WeeklyReview
- `id`
- `user_id` → User
- `week_start`
- `week_end`
- `status` (draft, submitted)
- `submitted_at`
- `stats` (JSONB, auto-generated numbers by playbook, structure and edge)
- `adherence_score`
- `went_well`
- `biggest_mistake`
- `do_differently`
- `commitment` (focus for next week)
- `previous_commitment_kept` (bool)
- `llm_summary` (nullable)

### TradeGrade
- `id`
- `review_id` → WeeklyReview
- `position_id` → Position
- `process_grade` (A–F)
- `outcome` (win, loss, scratch)
- `quadrant` (repeat, variance, dangerous, lesson)
- `comment`

### PlaybookSuggestion
A finding about a playbook, shown in a review. Private to the user whose trades it came from.
- `id`
- `user_id` → User
- `playbook_id` → Playbook (may be another user's public playbook)
- `review_id` → WeeklyReview (the review it was shown in)
- `source` (self_analytics, model)
- `finding` (text)
- `evidence` (JSONB, the stats or model output behind it)
- `status` (open, dismissed, done; set by the user)
- `resulting_version_id` → PlaybookVersion (nullable; set when marked done)

## Related

- [Journal and trade log](journal-and-trade-log.md), the data the review reads
- [Playbooks](playbooks.md#parameters-and-changes) for versions, block updates and orphaned overrides shown in the review
