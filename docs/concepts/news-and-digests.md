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

Four a day at the start of each US session (pre-market, regular, post-market, overnight). Each covers the user's relevant news, notable price moves, and open positions against their management rules. The rules produce the suggestions; the LLM only writes the summary around them. Digests are private, so they are read in the app and never posted to the shared Discord server; pushing them as notifications waits for in-app notifications (see [alerts](alerts.md#delivery)).

## LLM budget

- The monthly cap is about USD 5, covering article summaries, digests and an optional weekly summary of trade notes.
- Digests run four times a day per user, about 120 runs per user per month.
- Every LLM call logs its usage and cost. A budget guard stops non-essential calls when the cap is near.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### NewsSource
Shared across users, managed from the UI.
- `id`
- `name`
- `type` (rss, edgar, html)
- `url`
- `poll_interval_seconds`
- `priority`
- `tags`
- `parser_config` (JSONB)
- `is_enabled`
- `last_polled_at`
- `last_error`

### NewsArticle
- `id`
- `source_id` → NewsSource
- `url`
- `dedupe_hash`
- `title`
- `lead`
- `published_at`
- `fetched_at`
- `summary` (LLM, cached, nullable)
- `importance` (low, normal, high)
- `is_relevant` (bool)

### ArticleTicker
- `article_id` → NewsArticle
- `symbol` → Ticker
- `match_method` (cashtag, dictionary)

### Digest
- `id`
- `user_id` → User
- `session` (pre_market, regular, post_market, overnight)
- `session_date` (ET)
- `content`
- `llm_usage_id` → LLMUsage
- `delivered_at`

### DigestArticle
- `digest_id` → Digest
- `article_id` → NewsArticle

### LLMUsage
For the monthly budget guard.
- `id`
- `purpose` (article_summary, digest, review_summary)
- `provider`
- `model`
- `tokens_in`
- `tokens_out`
- `cost_usd`
- `called_at`

## Related

- [Alerts](alerts.md) for high-importance news alerts, digest delivery, and which alerts are public
- [Scheduling and time](scheduling-and-time.md) for news polling and digest jobs
