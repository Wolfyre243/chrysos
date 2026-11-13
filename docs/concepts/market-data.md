# Market data

Chrysos collects market data and keeps the history that is hard to get later.

## Market data

- Data comes through `MarketDataProvider`: quotes, option chains with IV and greeks, price history, earnings dates, fundamentals and consensus earnings estimates. See [architecture.md](../architecture.md#external-dependencies) for the providers.
- Results are cached in Postgres. There is no universal ticker master table; tickers are cached on demand.
- Option chain fetches are cached by symbol, expiry and fetch date, so screeners and other jobs that need the same chain in one window share a single fetch.
- A token-bucket rate limiter enforces provider quotas. Long jobs spread their calls over time instead of trying to evade limits.
- Provider calls are logged so quota usage is visible.

## Chain snapshots

- End-of-day option chains are snapshotted for every watchlist ticker and every open position, saved from day one. Free historical options data is scarce, so Chrysos builds its own. This history later supports lookback indicators such as IV rank, and backtesting of playbook thresholds.
- Until enough history exists, history-dependent indicators such as IV rank and IV percentile show "insufficient history".
- Expected volume is roughly 15 million option rows per year for about 20 watchlist tickers. Snapshot tables are partitioned by date.

## Watchlists

Public or private ticker groups. They decide which tickers get chain snapshots, GEX and news coverage, and are separate from the screener universe.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### Ticker
Cache populated on demand, not a maintained master list.
- `symbol` (PK)
- `name`
- `asset_type` (stock, etf, index)
- `exchange`
- `is_optionable`
- `in_universe` (bool, screener universe membership)
- `universe_source` (sp500, liquid_optionable)
- `last_refreshed_at`

### PriceBar
- `symbol` → Ticker
- `interval` (1d, 1h, …)
- `ts`
- `open`, `high`, `low`, `close`, `volume`

### EarningsEvent
- `id`
- `symbol` → Ticker
- `date`
- `timing` (before_open, after_close, unknown)
- `is_confirmed`
- `source`

### EarningsExpectation
What the market expects ahead of an earnings event. Captured more than once as the date approaches.
- `id`
- `earnings_event_id` → EarningsEvent
- `captured_at`
- `implied_move_pct` (options-implied move to the first expiry after the report)
- `chain_snapshot_id` → ChainSnapshot (nullable)
- `eps_estimate` (consensus, nullable)
- `revenue_estimate` (consensus, nullable)
- `source`

### FundamentalsSnapshot
Fundamentals for one reporting period, used by fundamentals indicators such as P/E and the health score.
- `id`
- `symbol` → Ticker
- `period_end`
- `period_type` (quarter, annual, ttm)
- `revenue`
- `revenue_growth_yoy`
- `gross_margin`, `operating_margin`, `net_margin`
- `eps`
- `pe_ratio` (at capture time)
- `other` (JSONB, further metrics the provider returns)
- `source`
- `captured_at`

### ChainSnapshot
One capture of an option chain at a point in time.
- `id`
- `symbol` → Ticker
- `captured_at`
- `kind` (eod, screener, on_demand)
- `spot_price`
- `provider`
- `is_partial` (bool, true for pruned screener fetches)

### OptionQuote
Row within a chain snapshot. Partition by date.
- `snapshot_id` → ChainSnapshot
- `expiry`
- `strike`
- `right` (call, put)
- `contract_symbol` (OCC)
- `bid`, `ask`, `last`
- `volume`
- `open_interest`
- `iv`
- `delta`, `gamma`, `theta`, `vega`

### ProviderCallLog
For quota visibility.
- `id`
- `provider`
- `endpoint`
- `called_at`
- `status`
- `latency_ms`

### Watchlist
- `id`
- `owner_id` → User
- `name`
- `description`
- `visibility` (public, private)

### WatchlistItem
- `watchlist_id` → Watchlist
- `symbol` → Ticker
- `sort_order`
- `note`
- `added_at`

## Related

- [Analytics](analytics.md), which computes indicators from this data
- [Screener](screener.md) for how the universe is fetched within rate limits
- [Users and access](users-and-access.md) for watchlist visibility
