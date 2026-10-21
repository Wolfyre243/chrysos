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

## Rule engine

A single rule format and evaluator serves four features:

| Feature           | Rules used                         | Evaluated against               |
| ----------------- | ---------------------------------- | ------------------------------- |
| Screener          | Playbook entry rules               | Universe tickers                |
| Soft enforcement  | Playbook entry rules and checklist | Trade entry snapshot and plan   |
| Management alerts | Playbook management rules          | Open positions                  |
| Real-time alerts  | User alert rules                   | News events, prices, indicators |

A rule references either an analytics registry indicator or a known field (position state, earnings, price, news). Rules can be combined with `all` / `any` groups.

```
{ "indicator": "forward_factor", "params": { "front_dte": 30, "back_dte": 60 }, "op": ">", "value": 0.2 }
{ "field": "position.pnl_pct", "op": ">=", "value": 25 }
{ "field": "earnings.days_until", "op": "<", "value": 7 }
```

## Playbook storage

- Default templates (calendar, vertical, etc.) are hardcoded and versioned in code.
- Each user's copy stores overrides on top of its template, so template improvements still reach fields the user has not overridden.
- Every playbook change creates a new playbook version. Structural changes are stored as proposals until the weekly review applies or rejects them.

## Screener pipeline

The universe is the S&P 500 plus liquid optionable names, screened nightly as a background job. Rate limits are handled by doing less work:

1. Stage 1 (cheap, whole universe): filter on price, average volume, options volume and earnings date using snapshot-level data. Expected to cut roughly 600 tickers to 50 to 100.
2. Stage 2 (expensive, survivors only): fetch only the 2 or 3 expirations near the target DTE and only near-the-money strikes, then evaluate the playbook's entry rules.

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
- The weekly review reminder is a Discord message linking to the review.

## Scheduling and time

- All timestamps are stored in UTC.
- All market-session logic runs in `America/New_York`, so US daylight saving changes are handled correctly.
- User-facing schedules (weekly review) use each user's own timezone.
- Scheduled jobs: end-of-day chain snapshots, nightly screener, news polling, session digests, management-rule checks, review reminders.

## Delivery phases

### MVP: core loop

1. Auth (two users, CLI-seeded, session login and logout)
2. Data layer (moomoo adapter, rate limiter, cache, end-of-day chain snapshots)
3. Analytics registry with the starter set (forward factor, term structure, expected move, GEX)
4. Rule engine and playbooks (templates, user overrides, versioning, change proposals)
5. Trade journal (positions, executions, plans, entry snapshots, soft enforcement, violations)
6. Ticker page (chart with trade markers and GEX levels, analytics panels)
7. Weekly review

The data layer comes first so chain snapshot history starts accumulating as early as possible.

### MVP+1: automation

8. Screeners (two-stage, nightly, calendar and vertical)
9. News (configurable sources, ticker tagging, session digests, rule-based Discord alerts, news markers on the ticker page)
