# Alerts

One system for everything that needs the user's attention. Each thing the user is told about is an alert event.

- Alert event kinds: high-importance news (8-K filings, halts, earnings, keyword matches), management triggers, screener hits, reminders such as closing a position or the weekly review, and the user's own alerts.
- Screener hits are batched: each nightly screener run raises one alert event listing its top hits, rather than one per hit.

## Alerts

An alert is a user's standing watch: a scope, a cooldown, and a [rule set](rule-engine.md#rules-and-rule-sets) whose rules are each read as a [trigger](rule-engine.md#how-features-read-results). One alert can hold several triggers that share its scope and cooldown, each firing on its own:

```json
{
  "id": 12,
  "user_id": 2,
  "name": "AAPL levels",
  "scope_type": "ticker",
  "scope_ref": "AAPL",
  "cooldown_seconds": 86400,
  "is_enabled": true,
  "rules": [
    {
      "key": "below_200",
      "label": "Below $200",
      "enabled": true,
      "condition": {
        "op": "lt",
        "left": { "kind": "field", "id": "ticker.price" },
        "right": 200
      }
    },
    {
      "key": "above_250",
      "label": "Above $250",
      "enabled": true,
      "condition": {
        "op": "gt",
        "left": { "kind": "field", "id": "ticker.price" },
        "right": 250
      }
    }
  ]
}
```

- The scope decides what each rule is checked against: one ticker, every ticker in a watchlist, the user's open positions, or all.
- An alert has no playbook, so its rules use literals only: no params and no leg slots.
- Switching the alert off (`is_enabled`) stops all its rules; disabling one rule stops only that trigger.

## Triggers

Management triggers (a playbook's management rules, checked against each open position) and alerts both raise alert events from triggers, following [ADR 0005](../adr/0005-triggers-fire-on-becoming-true.md):

- A trigger fires when its result goes from false to true for one subject, such as one ticker or one position.
- It can't fire again until it has been false and the cooldown since its last firing has passed.
- Unknown results neither fire nor count as false, so a data outage between two true results doesn't raise a second alert event.
- The cooldown belongs to whatever raises the event, never to the rule: an alert's `cooldown_seconds`, or for management triggers the system-wide `management_trigger_cooldown` [setting](../references/data-model.md#appsetting), one day by default.
- Alert events report changes. Whether a rule is still true is shown as current rule status, on the position page and in session digests.

Other firing modes, such as on every evaluation while true, at most once a day, or once only, are future options.

## Public and private alert events

Every alert event is either public or private, following the [data ownership](users-and-access.md) rules:

- Public: about shared data only. High-importance news on tickers in public watchlists and from macro sources, and hits from public screeners (see [screener](screener.md#public-and-private-screeners)).
- Private: about anything a user owns. Management triggers (positions), hits from private screeners, session digests, review and position reminders, the user's own alerts, and news on held tickers or private watchlists.

## Delivery

- Discord comes first: one webhook into a shared server, carrying public alert events only. Nothing private is ever posted there.
- In-app notifications come later as a second `Notifier` channel, and carry private alert events. Until then, private alert events are recorded but not pushed; the user sees them in the app (screener results, digests, the review page, position rule status).
- Every delivery is logged with status and errors.

## Open questions

- Where trigger state is stored. Each trigger has to remember, per subject, whether it has been false since it last fired. One alert has many triggers (one per rule for each ticker in its scope), and an open position has one per management rule, so the state can't be a single column on Alert or Position. Two options:
  - A `TriggerState` table keyed by owner (an alert, or none for a position's management rules), subject (a ticker or a position) and rule key, holding only whether the trigger is armed. Each alert event a trigger raises points at its row, so the last firing time is derived from the events.
  - A `RuleSet` table that alerts, screeners and playbook versions all reference, with trigger state keyed by rule set, rule key and subject. This depends on how playbook versions store rules, so it is decided with the [playbook design](playbooks.md#open-questions).
- How an alert event records which trigger raised it. This follows from the choice above.
- Proposed but not yet confirmed: a new trigger starts armed, so a condition already true the first time it is checked fires once; and a trigger that becomes false during its cooldown fires on the first true result after the cooldown ends.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### Alert
A user's standing watch. Private to its owner.
- `id`
- `user_id` → User
- `name`
- `scope_type` (ticker, watchlist, positions, all)
- `scope_ref` (symbol or watchlist id, nullable)
- `cooldown_seconds`
- `is_enabled`
- `rules` (JSONB, a rule set; each rule is read as a trigger)

Trigger state isn't modelled yet (see open questions); it replaces the old `last_triggered_at`.

### AlertEvent
One thing the user is told about.
- `id`
- `visibility` (public, private)
- `user_id` → User (required when private; null when public)
- `kind` (news, alert, management_trigger, screener_hit, review_reminder)
- `alert_id` → Alert (nullable)
- `position_id` → Position (nullable)
- `article_id` → NewsArticle (nullable)
- `screener_run_id` → ScreenerRun (nullable; one batched event per run)
- `payload` (JSONB)
- `triggered_at`

### NotificationDelivery
- `id`
- `user_id` → User (null for posts to the shared Discord server)
- `channel` (discord, in_app; discord carries public alert events only, in_app carries private ones)
- `alert_event_id` → AlertEvent (nullable)
- `digest_id` → Digest (nullable)
- `status` (pending, sent, failed)
- `sent_at`
- `error`

## Related

- [Rule engine](rule-engine.md) for the rule format and how triggers are read
- [News and digests](news-and-digests.md) for news alert events and session digests (private, so delivered in-app)
- [Users and access](users-and-access.md) for what is private and what is shared
- [Screener](screener.md) and [playbooks](playbooks.md) (management rules), the main sources of alert events
