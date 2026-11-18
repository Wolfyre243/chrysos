# Screener

Finds trade candidates that match a playbook.

- Each screener runs one playbook's entry rules, plus its own custom rules, every night across the universe: the S&P 500 plus liquid optionable names. The first ones cover calendar and vertical playbooks.
- It screens in two stages to stay within rate limits (see below).
- A hit becomes a trade plan in one click, pre-filled with the playbook, legs and the indicator values at screening time.

## Pipeline

Screening runs nightly as a background job. Rate limits are handled by doing less work:

1. Stage 1 (cheap, whole universe): evaluate the rules that need no option chain and read no legs, such as price, average volume, options volume and earnings date. Expected to cut roughly 600 tickers to 50 to 100.
2. Stage 2 (expensive, survivors only): run the edge's leg selectors to decide which expirations to fetch (near the target DTEs for forward factor, either side of the earnings date for IV crush), fetch only those and near-the-money strikes, then evaluate the remaining rules.
3. Save the hits as screener results and record one alert event for the run listing the top hits. A public screener's alert event is public and goes to the shared Discord server. A private screener's is pushed only once in-app notifications exist (see [alerts](alerts.md#delivery)).

The rate limiter spreads calls across the overnight window. Stage 2 fetches go through the shared [market data cache](market-data.md#market-data), keyed by symbol, expiry and fetch date, so when several screeners need the same chain in one nightly window it is fetched once, whatever each screener's visibility.

## Public and private screeners

A screener's visibility follows its playbook:

- A [public playbook](playbooks.md#public-playbooks) can have at most one public screener, created and managed by the playbook's owner. Its hits hold only market data (ticker, proposed legs, indicator values), never who traded them, so they are shared: every user sees them in the app and they are posted to the shared Discord server.
- Any user can also create private screeners on their own playbooks or on a public one, for example with their own [custom rules](#custom-rules). Their hits stay private.
- An archived playbook's screeners stop running.

## Custom rules

A screener reads its rules from its playbook: each run evaluates the entry rules of the playbook's current version and records that version. On top of them, a screener can have its own custom rules:

- They are combined with the playbook's entry rules using `and`, so they can only narrow the results, never loosen them. A user who wants looser settings builds their own playbook from the same preset.
- They can do anything an entry rule can, including reading the playbook's leg slots, and are staged automatically like every other rule.
- They use literals only. The screener owns its numbers instead of borrowing the playbook's params, so it doesn't change when the playbook's owner edits them.
- They only affect that screener's results. Soft enforcement and management triggers never read them, so entering a trade the custom rules would have screened out isn't a violation.
- Custom rules aren't [add-ons](playbooks.md#add-ons): an add-on is a playbook block, and a screener can't attach one.
- Each run stores a copy of the custom rules it ran with, so past hits can still be explained after the rules are edited.

For example, Bob creates a private screener on Alice's public "FF calendar" playbook with two custom rules, price under $300 and forward factor above 0.3. His screener finds the same kind of trades as hers, but only the cheaper, stronger ones. A worked run is in the [rule engine](rule-engine.md#example-a-screener-run).

## Stage assignment

Rules are assigned to a stage automatically from what their fields and indicators [require](rule-engine.md#requires): a rule runs in stage 2 if it needs `chain` or reads a leg, since legs are only picked in stage 2, and in stage 1 otherwise. The IV crush edge's "earnings within N days" rule is therefore a stage 1 rule without being written as one. Custom rules are staged the same way.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### Screener
- `id`
- `user_id` → User
- `playbook_id` → Playbook
- `name`
- `visibility` (public, private; public only on a public playbook owned by the same user, at most one per playbook)
- `custom_rules` (JSONB, a rule set combined with the playbook's entry rules)
- `schedule`
- `is_enabled`

### ScreenerRun
- `id`
- `screener_id` → Screener
- `playbook_version_id` → PlaybookVersion
- `custom_rules` (JSONB, copy of the screener's custom rules as they were for this run)
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
- [Rule engine](rule-engine.md) for the rule format and a worked screener run
- [Alerts](alerts.md) for how screener hits are delivered
