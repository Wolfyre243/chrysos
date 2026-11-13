# Chrysos architecture

Stack, deployment and external dependencies. For how the system behaves, see the [concepts](README.md#concepts); for the data model, see the index in [data-model.md](references/data-model.md).

## Stack

**Frontend**
- Typescript (pnpm)
- React Router (framework mode)
- shadcn/ui for components library base
- Redux (RTK Query) for state management and frontend caching of API calls
- TradingView `lightweight-charts` for charting

**Backend**
- Python (uv)
- FastAPI
- SQLModel as the ORM
- Alembic for migrations

**Database**
- PostgreSQL

## Deployment

- Docker Compose stack: `postgres`, `api`, `worker`, `web`, `opend`.
- OpenD has no official Docker image as far as known; community images exist. Before using one, confirm it pulls the official OpenD binary and supports headless first-login phone verification.
- During development, OpenD runs natively on Windows.
- The second user connects through Tailscale, so no ports are exposed publicly.

## External dependencies

### Adapters

This list is non-exhaustive. Every external dependency sits behind an interface so providers can be swapped.

| Interface            | Responsibility                                                                                        | First implementation                                 |
| -------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `MarketDataProvider` | Quotes, option chains, IV/greeks, price history, earnings calendar, fundamentals, consensus estimates | moomoo (OpenD); fundamentals and estimates to verify |
| `BrokerProvider`     | Positions and fills (read-only)                                                                       | None yet; interface only                             |
| `NewsSource`         | Fetch and parse news items                                                                            | Generic RSS                                          |
| `LLMProvider`        | Summaries and digests                                                                                 | OpenAI                                               |
| `Notifier`           | Deliver alerts and digests                                                                            | Discord webhook (shared server, public alerts only)  |

Broker credentials, if ever added, are read-only. Chrysos records trades and never places orders.

### Market data providers

- yfinance: the `MarketDataProvider` for Phase 0, while OpenD is evaluated (see [roadmap.md](roadmap.md)).
- moomoo OpenAPI via OpenD: the long-term `MarketDataProvider`.

#### moomoo OpenD

To verify:

- moomoo OpenAPI request limits for chain and snapshot calls.
- Whether the moomoo account is entitled to live US options quotes (OPRA).
- Whether moomoo provides fundamentals and consensus earnings estimates. If not, they need a second `MarketDataProvider` implementation.

### LLM

- OpenAI Platform, behind `LLMProvider`. Spend is capped near USD 5 a month (see [news and digests](concepts/news-and-digests.md#llm-budget)).

### Notifications

- Discord, behind `Notifier`: one webhook into a shared server, for public alerts only (see [alerts](concepts/alerts.md#delivery)). The webhook URL works as a credential, since anyone holding it can post, so it is set as an environment variable rather than stored in the database.
- In-app notifications, a second `Notifier` for private alerts, come later (see [roadmap.md](roadmap.md#future-plans)).

### News feeds

Candidate sources are CNBC, MarketWatch, Nasdaq, Fed press releases, SEC EDGAR, and per-ticker feeds from Yahoo Finance and Google News. Reuters discontinued its public RSS feeds around 2020 and needs an alternative. Avoid scraping the Unusual Whales Discord or site; replicating their calculations from raw data is the cleaner path.
