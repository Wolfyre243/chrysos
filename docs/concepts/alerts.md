# Alerts

One alert system for everything that needs the user's attention.

- Alert types: high-importance news (8-K filings, halts, earnings, keyword matches), management rule triggers, screener hits, reminders such as closing a position or the weekly review, and user-defined rules. All use the shared [rule format](rule-engine.md).
- Each alert rule has a cooldown to avoid repeated alerts.
- Screener hits are batched: each nightly screener run sends one alert listing its top hits, rather than one alert per hit.

## Public and private alerts

Every alert is either public or private, following the [data ownership](users-and-access.md) rules:

- Public: about shared data only. High-importance news on tickers in public watchlists and from macro sources, and hits from public screeners (see [screener](screener.md#public-and-private-screeners)).
- Private: about anything a user owns. Management rule triggers (positions), hits from private screeners, session digests, review and position reminders, user-defined alert rules, and news on held tickers or private watchlists.

## Delivery

- Discord comes first: one webhook into a shared server, carrying public alerts only. Nothing private is ever posted there.
- In-app notifications come later as a second `Notifier` channel, and carry private alerts. Until then, private alerts are recorded but not pushed; the user sees them in the app (screener results, digests, the review page, position rule status).
- Every delivery is logged with status and errors.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### AlertRule
- `id`
- `user_id` → User
- `name`
- `condition` (JSONB, shared rule format)
- `scope_type` (ticker, watchlist, positions, all)
- `scope_ref` (symbol or watchlist id, nullable)
- `cooldown_seconds`
- `is_enabled`
- `last_triggered_at`

### AlertEvent
- `id`
- `visibility` (public, private)
- `user_id` → User (required when private; null when public)
- `kind` (news, alert_rule, management_rule, screener_hit, review_reminder)
- `alert_rule_id` → AlertRule (nullable)
- `position_id` → Position (nullable)
- `article_id` → NewsArticle (nullable)
- `screener_run_id` → ScreenerRun (nullable; one batched alert per run)
- `payload` (JSONB)
- `triggered_at`

### NotificationDelivery
- `id`
- `user_id` → User (null for posts to the shared Discord server)
- `channel` (discord, in_app; discord carries public alerts only, in_app carries private ones)
- `alert_event_id` → AlertEvent (nullable)
- `digest_id` → Digest (nullable)
- `status` (pending, sent, failed)
- `sent_at`
- `error`

## Related

- [News and digests](news-and-digests.md) for news alerts and session digests (private, so delivered in-app)
- [Users and access](users-and-access.md) for what is private and what is shared
- [Screener](screener.md) and [playbooks](playbooks.md) (management rules), the main alert sources
