# Scheduling and time

- All timestamps are stored in UTC.
- All market-session logic runs in `America/New_York`, so US daylight saving changes are handled correctly.
- User-facing schedules (weekly review) use each user's own timezone.
- Scheduled jobs: end-of-day chain snapshots, nightly screener, news polling, session digests, management-rule checks, review reminders, earnings expectation captures, fundamentals refreshes.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### JobRun
- `id`
- `job_name` (eod_snapshot, screener, news_poll, digest, management_check, review_reminder, earnings_capture, fundamentals_refresh)
- `started_at`
- `finished_at`
- `status`
- `error`

## Related

- [Market data](market-data.md), [analytics](analytics.md), [screener](screener.md), [news and digests](news-and-digests.md) and [alerts](alerts.md), which own the scheduled jobs
