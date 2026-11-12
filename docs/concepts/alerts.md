# Alerts

One alert system for everything that needs the user's attention.

- Alert types: high-importance news on held or watched tickers (8-K filings, halts, earnings, keyword matches), management rule triggers, screener hits, reminders such as closing a position, and user-defined rules. All use the shared [rule format](rule-engine.md).
- Each alert rule has a cooldown to avoid repeated alerts.
- Screener hits are batched: each nightly screener run sends one alert listing its top hits, rather than one alert per hit.
- The weekly review reminder is a Discord message linking to the review.

## Delivery

- Discord webhook first; each user has their own.
- In-app notifications come later as a second `Notifier` channel.
- Every delivery is logged with status and errors.

## Related

- [News and digests](news-and-digests.md) for session digests, which are delivered the same way
- [Screener](screener.md) and [playbooks](playbooks.md) (management rules), the main alert sources
- Data model: [Alerts and notifications](../references/data-model.md#alerts-and-notifications)
