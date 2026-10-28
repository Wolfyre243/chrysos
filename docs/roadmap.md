# Roadmap

The rough outline and plan for Chrysos, split into phases.

## Phase 0 (MVP)

- Auth (two users, CLI-seeded, session login and logout)
- Data layer (rate limiter, cache, end-of-day chain snapshots)
  - At this point in time, we will use yfinance as the primary `MarketDataProvider` while we continue experimenting with MooMoo's OpenD and enable it in Phase 1.
- Analytics registry with the starter set (forward factor, term structure, expected move, GEX, etc.)
- Rule engine and playbooks (templates, user overrides, versioning, change proposals)
- Journal and trade log (plans, notes, feelings, positions, executions, entry snapshots, soft enforcement, violations)
- Ticker page (chart with trade markers and GEX levels, analytics panels)
- Weekly review

The data layer here should be done quick to prototype the entire system, but kept easily swappable behind the `MarketDataProvider` interface for flexibility.

## Phase 1

- Screeners (two-stage, nightly, calendar and vertical, one Discord alert per run with the top hits)
- News (configurable sources, ticker tagging, session digests, rule-based Discord alerts, news markers on the ticker page)
- Preserve historical data
  - Once the integration of MooMoo's OpenD is ready, start storing data for future needs
- Backtesting
  - Find a flexible way to slot in playbooks and run them against historical data to experiment on the best configurations for each.
- Alerts

## Future Plans

- Fundamentals indicators (P/E) and the health score, once a fundamentals source is confirmed
- Research notes
- Earnings analysis
- Models on the user's trades and on stored market history