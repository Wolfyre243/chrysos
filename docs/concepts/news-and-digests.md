# News and digests

## Sources

Sources are managed from the UI (add, remove, enable, disable, poll interval, priority). Source types are RSS (a generic parser covers most), SEC EDGAR Atom feeds, and HTML scrapers where needed. See [architecture.md](../architecture.md#news-feeds) for the candidate feeds.

## Ingestion

Articles are deduplicated and tagged with tickers without an LLM. The LLM never reads raw articles. Ingestion runs in five steps:

1. Poll sources and deduplicate by URL or title hash.
2. Tag tickers deterministically (cashtags plus a ticker and company-name dictionary).
3. Filter for relevance: open positions, watchlists, screener universe, macro sources.
4. Summarise each relevant article once (headline plus lead paragraph) and cache the summary. Summaries are shared across users and digests.
5. Build digests from cached summaries plus price moves and position state.

## Session digests

Four a day at the start of each US session (pre-market, regular, post-market, overnight). Each covers the user's relevant news, notable price moves, and open positions against their management rules. The rules produce the suggestions; the LLM only writes the summary around them.

## LLM budget

- The monthly cap is about USD 5, covering article summaries, digests and an optional weekly summary of trade notes.
- Digests run four times a day per user, about 120 runs per user per month.
- Every LLM call logs its usage and cost. A budget guard stops non-essential calls when the cap is near.

## Related

- [Alerts](alerts.md) for high-importance news alerts and digest delivery
- [Scheduling and time](scheduling-and-time.md) for news polling and digest jobs
- Data model: [News and digests](../references/data-model.md#news-and-digests), [LLMUsage](../references/data-model.md#system)
