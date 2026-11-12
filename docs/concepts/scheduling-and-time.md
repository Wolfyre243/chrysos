# Scheduling and time

- All timestamps are stored in UTC.
- All market-session logic runs in `America/New_York`, so US daylight saving changes are handled correctly.
- User-facing schedules (weekly review) use each user's own timezone.
- Scheduled jobs: end-of-day chain snapshots, nightly screener, news polling, session digests, management-rule checks, review reminders.

## Related

- [Market data](market-data.md), [screener](screener.md), [news and digests](news-and-digests.md) and [alerts](alerts.md), which own the scheduled jobs
- Data model: [JobRun](../references/data-model.md#system)
