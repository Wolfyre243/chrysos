# Screener

Finds trade candidates that match a playbook.

- Each screener runs one playbook's entry criteria every night across the universe: the S&P 500 plus liquid optionable names. The first ones cover calendar and vertical playbooks.
- It screens in two stages to stay within rate limits (see below).
- A hit becomes a trade plan in one click, pre-filled with the playbook, legs and the indicator values at screening time.

## Pipeline

Screening runs nightly as a background job. Rate limits are handled by doing less work:

1. Stage 1 (cheap, whole universe): filter on price, average volume, options volume and earnings date using snapshot-level data. Expected to cut roughly 600 tickers to 50 to 100.
2. Stage 2 (expensive, survivors only): run the edge's leg selectors to decide which expirations to fetch (near the target DTEs for forward factor, either side of the earnings date for IV crush), fetch only those and near-the-money strikes, then evaluate the remaining entry rules.
3. Save the hits as screener results and record one alert for the run listing the top hits. A public screener's alert is public and goes to the shared Discord server. A private screener's alert is pushed only once in-app notifications exist (see [alerts](alerts.md#delivery)).

The rate limiter spreads calls across the overnight window. Stage 2 fetches go through the shared [market data cache](market-data.md#market-data), keyed by symbol, expiry and fetch date, so when several screeners need the same chain in one nightly window it is fetched once, whatever each screener's visibility.

## Public and private screeners

A screener's visibility follows its playbook:

- A [public playbook](playbooks.md#public-playbooks) can have at most one public screener, created and managed by the playbook's owner. Its hits hold only market data (ticker, proposed legs, indicator values), never who traded them, so they are shared: every user sees them in the app and they are posted to the shared Discord server.
- Any user can also create private screeners on their own playbooks or on a public one, for example with extra `stage1_filters`. Their hits stay private.
- An archived playbook's screeners stop running.

## Stage assignment

Rules are assigned to a stage automatically: a rule whose indicators and fields need only snapshot-level data (price, volume, earnings dates, fundamentals) runs in stage 1, and any rule that needs `chain` runs in stage 2. The IV crush edge's "earnings within N days" rule is therefore a stage 1 filter without being written as one. A screener's own `stage1_filters` add to the derived ones; they don't replace them.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### Screener
- `id`
- `user_id` → User
- `playbook_id` → Playbook
- `name`
- `visibility` (public, private; public only on a public playbook owned by the same user, at most one per playbook)
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
