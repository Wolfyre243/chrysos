# Roadmap

The rough outline and plan for Chrysos, split into phases.

## Phase 0 (MVP)

- Auth (two users, CLI-seeded, session login and logout)
- Data layer (rate limiter, cache, end-of-day chain snapshots)
  - At this point in time, we will use yfinance as the primary `MarketDataProvider` while we continue experimenting with MooMoo's OpenD and enable it in Phase 1.
- Analytics registry with the starter set (forward factor, term structure, expected move, GEX, etc.)
- Rule engine and playbooks (structures, edges, add-ons, presets, parameters, user overrides, versioning, change proposals)
- Journal and trade log (plans, notes, feelings, positions, executions, entry snapshots, soft enforcement, violations)
- Ticker page (chart with trade markers and GEX levels, analytics panels)
- Weekly review

The data layer here should be done quick to prototype the entire system, but kept easily swappable behind the `MarketDataProvider` interface for flexibility.

## Phase 1

- Screeners (two-stage, nightly, calendar and vertical, hits listed in the app)
- News (configurable sources, ticker tagging, session digests read in the app, Discord alerts for high-importance public news, news markers on the ticker page)
- Preserve historical data
  - Once the integration of MooMoo's OpenD is ready, start storing data for future needs
- Backtesting
  - Run playbooks against historical data and sweep their named parameters (and swap edges or structures) to find the best configuration for each.
- Alerts (public alerts to the shared Discord server; private alerts are recorded and shown in the app)

## Future Plans

- In-app notifications for private alerts: management rule triggers, screener hits, digests, review and position reminders, user alert rules and news on held tickers or private watchlists
- Fundamentals indicators (P/E) and the health score, once a fundamentals source is confirmed
- Research notes
- Earnings analysis
- Models on the user's trades and on stored market history
- SEC filing parser that reads specific filing sections into structured data
- Automatic fill import from moomoo, with unplanned-trade detection
- Parsing pasted moomoo order confirmations for faster entry
- Sharing watchlists with specific users
- More indicators: IV rank and percentile once history exists, skew