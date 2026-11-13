# Screener

Finds trade candidates that match a playbook.

- Each screener runs one playbook's entry criteria every night across the universe: the S&P 500 plus liquid optionable names. The first ones cover calendar and vertical playbooks.
- It screens in two stages to stay within rate limits (see below).
- A hit becomes a trade plan in one click, pre-filled with the playbook, legs and the indicator values at screening time.

## Pipeline

Screening runs nightly as a background job. Rate limits are handled by doing less work:

1. Stage 1 (cheap, whole universe): filter on price, average volume, options volume and earnings date using snapshot-level data. Expected to cut roughly 600 tickers to 50 to 100.
2. Stage 2 (expensive, survivors only): run the edge's leg selectors to decide which expirations to fetch (near the target DTEs for forward factor, either side of the earnings date for IV crush), fetch only those and near-the-money strikes, then evaluate the remaining entry rules.
3. Save the hits as screener results and record one alert for the run listing the top hits. Screeners are private, so the alert is pushed only once in-app notifications exist (see [alerts](alerts.md#delivery)).

The rate limiter spreads calls across the overnight window.

## Stage assignment

Rules are assigned to a stage automatically: a rule whose indicators and fields need only snapshot-level data (price, volume, earnings dates, fundamentals) runs in stage 1, and any rule that needs `chain` runs in stage 2. The IV crush edge's "earnings within N days" rule is therefore a stage 1 filter without being written as one. A screener's own `stage1_filters` add to the derived ones; they don't replace them.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### Screener
- `id`
- `user_id` → User
- `playbook_id` → Playbook
- `name`
- `stage1_filters` (JSONB, extra filters on top of those derived from the playbook's rules)
- `schedule`
- `is_enabled`

### ScreenerRun
- `id`
- `screener_id` → Screener
- `playbook_version_id` → PlaybookVersion
- `started_at`
- `finished_at`
- `status` (running, succeeded, failed)
- `universe_count`
- `stage1_count`
- `stage2_count`
- `error`

### ScreenerResult
- `id`
- `run_id` → ScreenerRun
- `symbol` → Ticker
- `legs` (JSONB, proposed structure)
- `metrics` (JSONB, indicator values)
- `rank`

## Related

- [Playbooks](playbooks.md) for entry rules and leg selectors
- [Alerts](alerts.md) for how screener hits are delivered
