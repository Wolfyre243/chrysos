# Chrysos architecture

Technical design behind [features.md](features.md). See [entities.md](entities.md) for the data model.

## Stack

| Layer         | Choice                                    |
| ------------- | ----------------------------------------- |
| Frontend      | React Router, shadcn/ui                   |
| Charts        | TradingView `lightweight-charts`          |
| Backend       | FastAPI (Python)                          |
| Database      | Postgres                                  |
| Market data   | moomoo OpenAPI via OpenD (first provider) |
| LLM           | OpenAI (behind an adapter)                |
| Notifications | Discord webhooks (in-app later)           |

## Deployment

- Docker Compose stack: `postgres`, `api`, `worker`, `web`, `opend`.
- Target host: a mini PC running a Proxmox VM. A Raspberry Pi is ruled out: performance aside, OpenD's Linux build appears to be x86-64 only (to verify).
- OpenD has no official Docker image as far as known; community images exist. Before using one, confirm it pulls the official OpenD binary and supports headless first-login phone verification.
- During development, OpenD runs natively on Windows.
- The second user connects through Tailscale, so no ports are exposed publicly.

## Adapters

Every external dependency sits behind an interface so providers can be swapped.

| Interface            | Responsibility                                                                                        | First implementation                                 |
| -------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `MarketDataProvider` | Quotes, option chains, IV/greeks, price history, earnings calendar, fundamentals, consensus estimates | moomoo (OpenD); fundamentals and estimates to verify |
| `BrokerProvider`     | Positions and fills (read-only)                                                                       | None yet; interface only                             |
| `NewsSource`         | Fetch and parse news items                                                                            | Generic RSS                                          |
| `LLMProvider`        | Summaries and digests                                                                                 | OpenAI                                               |
| `Notifier`           | Deliver alerts and digests                                                                            | Discord webhook                                      |

Broker credentials, if ever added, are read-only. Chrysos records trades and never places orders.

## Users and access

- Two users (owner and one friend). There is no signup UI; users are created with a CLI script.
- Simple session-based login and logout.
- Private per user: journals, positions, trade records, playbooks, reviews, alert rules, screeners, digests.
- Watchlists: public (visible to all Chrysos users) or private (owner only).
- Shared globally: market data cache, chain snapshots, news sources, articles and their summaries.

User settings cover timezone, the soft enforcement toggle, the Discord webhook URL, and the weekly review day and time.

## Market data

- Data comes through `MarketDataProvider`: quotes, option chains with IV and greeks, price history, earnings dates, fundamentals and consensus earnings estimates.
- Results are cached in Postgres. There is no universal ticker master table; tickers are cached on demand.
- A token-bucket rate limiter enforces provider quotas. Long jobs spread their calls over time instead of trying to evade limits.
- Provider calls are logged so quota usage is visible.

### Chain snapshots

- End-of-day snapshots cover every watchlist ticker and every open position.
- Until enough history exists, history-dependent indicators such as IV rank and IV percentile show "insufficient history".
- Expected volume is roughly 15 million option rows per year for about 20 watchlist tickers. Snapshot tables are partitioned by date.

### To verify

- moomoo OpenAPI request limits for chain and snapshot calls.
- Whether the moomoo account is entitled to live US options quotes (OPRA).
- Whether moomoo provides fundamentals and consensus earnings estimates. If not, they need a second `MarketDataProvider` implementation.

## Analytics registry

Every indicator or calculator is a plugin registered in code. Each plugin declares:

| Field        | Meaning                                               |
| ------------ | ----------------------------------------------------- |
| `id`, `name` | Identifier and display name                           |
| `version`    | Bumped whenever the formula changes                   |
| `scope`      | `stock`, `option` or `spread`                         |
| `requires`   | Data needed: `chain`, `price_history`, `fundamentals` |
| `params`     | Parameter schema (e.g. front/back DTE targets)        |
| `output`     | `scalar`, `per_strike_series` or `term_curve`         |

The output type selects the visualisation on the ticker page, and scalar outputs can be used as screener filters. Snapshots store the indicator version, so historical values are only compared within the same formula version. New stock or option indicators can be added without changes elsewhere.

Fundamentals metrics such as P/E, and the in-house health score, are registered the same way (`scope` stock, `requires` fundamentals), so they work as screener filters and rule conditions. They wait on confirming a fundamentals source (see "To verify" under Market data).

## Rule engine

A single rule format and evaluator serves four features:

| Feature           | Rules used                         | Evaluated against               |
| ----------------- | ---------------------------------- | ------------------------------- |
| Screener          | Playbook entry rules               | Universe tickers                |
| Soft enforcement  | Playbook entry rules and checklist | Trade entry snapshot and plan   |
| Management alerts | Playbook management rules          | Open positions                  |
| Real-time alerts  | User alert rules                   | News events, prices, indicators |

A rule references either an analytics registry indicator or a known field (position state, earnings, price, news). Rules can be combined with `all` / `any` groups.

Inside a playbook, rules can also use two kinds of reference, resolved before evaluation:

- `$legs.<slot>`: a leg slot of the playbook's structure (such as `$legs.front`), bound to the expiry and strike the edge's selectors picked for this ticker or position. This lets one edge work on a calendar, a diagonal or a double calendar without hardcoding DTEs.
- `$params.<name>`: a named playbook parameter. Changing its value is a threshold change; changing the rule itself is a structural change.

```
{ "indicator": "forward_factor", "params": { "front": "$legs.front", "back": "$legs.back" }, "op": ">", "value": "$params.ff_min" }
{ "field": "earnings.between", "params": { "from": "$legs.front.expiry", "to": "$legs.back.expiry" }, "op": "==", "value": false }
{ "field": "legs.front.dte", "op": "<=", "value": "$params.exit_front_dte" }
{ "field": "position.pnl_pct", "op": ">=", "value": "$params.take_profit_pct" }
{ "field": "earnings.days_until", "op": "<", "value": 7 }
```

User alert rules use the same format with literal values, since they have no playbook to resolve references against.

## Playbooks

A playbook is put together from three kinds of block, all registered and versioned in code like analytics plugins. Users choose and combine blocks; they don't define new ones in the UI.

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

### Composition and storage

- A playbook is one structure, exactly one edge (compatible with the structure), any number of add-ons, plus user overrides.
- Presets (FF calendar, IV crush calendar, …) are named combinations defined in code that users start from.
- Overrides store only what the user changed: parameter values, disabled rules, extra user rules and checklist items, and edits to individual rules. They are keyed by the block and rule id they apply to.
- Resolving a playbook merges structure, edge and add-ons in that order, applies the overrides, and tags every resulting rule and checklist item with its `source` (edge, add-on or user). Violations and adherence stats can then point at the block a broken rule came from.
- Every playbook change creates a new immutable version recording the version of each block and the resolved rules, selectors and parameters.
- Changing a parameter value is a threshold change and applies immediately. Changing the structure, edge or add-ons, or adding, removing or editing a rule, is a structural change and is stored as a proposal until the weekly review applies or rejects it.
- When a block's version is bumped in code, playbooks using it pick up new parameter defaults for parameters they haven't overridden in a new `block_update` version, which applies immediately like a threshold change. New or changed rules and selectors arrive as change proposals (source `block_update`) for the next weekly review.

## Screener pipeline

The universe is the S&P 500 plus liquid optionable names, screened nightly as a background job. Rate limits are handled by doing less work:

1. Stage 1 (cheap, whole universe): filter on price, average volume, options volume and earnings date using snapshot-level data. Expected to cut roughly 600 tickers to 50 to 100.
2. Stage 2 (expensive, survivors only): run the edge's leg selectors to decide which expirations to fetch (near the target DTEs for forward factor, either side of the earnings date for IV crush), fetch only those and near-the-money strikes, then evaluate the remaining entry rules.

Rules are assigned to a stage automatically: a rule whose indicators and fields need only snapshot-level data (price, volume, earnings dates, fundamentals) runs in stage 1, and any rule that needs `chain` runs in stage 2. The IV crush edge's "earnings within N days" rule is therefore a stage 1 filter without being written as one. A screener's own `stage1_filters` add to the derived ones; they don't replace them.
3. Save the hits as screener results and send one alert for the run listing the top hits.

The rate limiter spreads calls across the overnight window.

## News pipeline

Sources are managed from the UI (add, remove, enable, disable, poll interval, priority). Source types are RSS (a generic parser covers most), SEC EDGAR Atom feeds, and HTML scrapers where needed.

Candidate sources are CNBC, MarketWatch, Nasdaq, Fed press releases, SEC EDGAR, and per-ticker feeds from Yahoo Finance and Google News. Reuters discontinued its public RSS feeds around 2020 and needs an alternative. Avoid scraping the Unusual Whales Discord or site; replicating their calculations from raw data is the cleaner path.

The LLM never reads raw articles. Ingestion runs in five steps:

1. Poll sources and deduplicate by URL or title hash.
2. Tag tickers deterministically (cashtags plus a ticker and company-name dictionary).
3. Filter for relevance: open positions, watchlists, screener universe, macro sources.
4. Summarise each relevant article once (headline plus lead paragraph) and cache the summary. Summaries are shared across users and digests.
5. Build digests from cached summaries plus price moves and position state.

## LLM budget

- The monthly cap is about USD 5, covering article summaries, digests and an optional weekly summary of trade notes.
- Digests run four times a day per user, about 120 runs per user per month.
- Every LLM call logs its usage and cost. A budget guard stops non-essential calls when the cap is near.

## Notifications

- Discord webhook first; each user has their own.
- In-app notifications come later as a second `Notifier` channel.
- Every delivery is logged with status and errors.
- Each alert rule has a cooldown to avoid repeated alerts.
- Screener hits are batched: one message per screener run, not one per hit.
- The weekly review reminder is a Discord message linking to the review.

## Scheduling and time

- All timestamps are stored in UTC.
- All market-session logic runs in `America/New_York`, so US daylight saving changes are handled correctly.
- User-facing schedules (weekly review) use each user's own timezone.
- Scheduled jobs: end-of-day chain snapshots, nightly screener, news polling, session digests, management-rule checks, review reminders.
