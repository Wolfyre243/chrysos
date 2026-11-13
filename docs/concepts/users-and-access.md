# Users and access

- For private, self-hosted use. There is no signup UI; users are created with a CLI script.
- Simple session-based login and logout.
- Private per user: journals, positions, trade records, playbooks, reviews, research files, alert rules, private alerts and their notifications, screeners, digests.
- Watchlists: public (visible to all Chrysos users) or private (owner only).
- Shared globally: market data cache, chain snapshots, news sources, articles and their summaries, and public alerts (posted to the shared Discord server; see [alerts](alerts.md#public-and-private-alerts)).

User settings cover timezone, the soft enforcement toggle, and the weekly review day and time. There is no per-user Discord setting: Discord is one shared server for public alerts only.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### User
- `id`
- `username` (unique)
- `password_hash`
- `display_name`
- `timezone`
- `enforcement_enabled` (bool)
- `review_day` (day of week)
- `review_time` (local time)
- `is_active`

### AuthSession
- `id`
- `user_id` → User
- `token_hash`
- `expires_at`
- `last_seen_at`

## Related

- [Scheduling and time](scheduling-and-time.md) for how user timezones are used
- [Alerts](alerts.md#public-and-private-alerts) for which alerts are public and which are private
