# Market data

Chrysos collects market data and keeps the history that is hard to get later.

## Market data

- Data comes through `MarketDataProvider`: quotes, option chains with IV and greeks, price history, earnings dates, fundamentals and consensus earnings estimates. See [architecture.md](../architecture.md#external-dependencies) for the providers.
- Results are cached in Postgres. There is no universal ticker master table; tickers are cached on demand.
- A token-bucket rate limiter enforces provider quotas. Long jobs spread their calls over time instead of trying to evade limits.
- Provider calls are logged so quota usage is visible.

## Chain snapshots

- End-of-day option chains are snapshotted for every watchlist ticker and every open position, saved from day one. Free historical options data is scarce, so Chrysos builds its own. This history later supports lookback indicators such as IV rank, and backtesting of playbook thresholds.
- Until enough history exists, history-dependent indicators such as IV rank and IV percentile show "insufficient history".
- Expected volume is roughly 15 million option rows per year for about 20 watchlist tickers. Snapshot tables are partitioned by date.

## Watchlists

Public or private ticker groups. They decide which tickers get chain snapshots, GEX and news coverage, and are separate from the screener universe.

## Related

- [Analytics](analytics.md), which computes indicators from this data
- [Screener](screener.md) for how the universe is fetched within rate limits
- [Users and access](users-and-access.md) for watchlist visibility
- Data model: [Market data](../references/data-model.md#market-data), [Watchlists](../references/data-model.md#watchlists)
