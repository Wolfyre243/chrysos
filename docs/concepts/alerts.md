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
- A new trigger starts ready to fire, so a condition that is already true when an alert is created fires on the first check.
- A trigger that goes false during its cooldown fires on the first true check after the cooldown ends.
- The cooldown belongs to whatever raises the event, never to the rule: an alert's `cooldown_seconds`, or for management triggers the system-wide `management_trigger_cooldown` [setting](../references/data-model.md#appsetting), one day by default.
- Alert events report changes. Whether a rule is still true is shown as current rule status, on the position page and in session digests.

Each trigger keeps one [TriggerState](#triggerstate) row per subject, recording whether it is armed (ready to fire). Its last firing time isn't stored; it is the latest alert event raised from that row.

Other firing modes, such as on every evaluation while true, at most once a day, or once only, are future options.

## Public and private alert events

Every alert event is either public or private, following the [data ownership](users-and-access.md) rules:

- Public: about shared data only. High-importance news on tickers in public watchlists and from macro sources, and hits from public screeners (see [screener](screener.md#public-and-private-screeners)).
- Private: about anything a user owns. Management triggers (positions), hits from private screeners, session digests, review and position reminders, the user's own alerts, and news on held tickers or private watchlists.

## Delivery

- Discord comes first: one webhook into a shared server, carrying public alert events only. Nothing private is ever posted there.
- In-app notifications come later as a second `Notifier` channel, and carry private alert events. Until then, private alert events are recorded but not pushed; the user sees them in the app (screener results, digests, the review page, position rule status).
- Every delivery is logged with status and errors.

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

### TriggerState
One trigger watching one subject: a rule of an alert, or a management rule of an open position, checked against one ticker or one position. Replaces the old `AlertRule.last_triggered_at`, which couldn't track an alert scoped to many tickers.
- `id`
- `alert_id` → Alert (nullable; null for a position's management triggers, whose rules come from the playbook version the position was entered under)
- `position_id` → Position (nullable; set when the subject is a position)
- `symbol` → Ticker (nullable; set when the subject is a ticker)
- `rule_key` (the rule's key in the alert, or its ref in the position's playbook version)
- `armed` (true when created, false once it fires, true again after a false result)

Exactly one of `position_id` and `symbol` is set, and a row without an `alert_id` has a `position_id`. Unique on (`alert_id`, `position_id`, `symbol`, `rule_key`), with nulls treated as equal (`NULLS NOT DISTINCT`). The last firing time is derived from the latest AlertEvent pointing at the row.

### AlertEvent
One thing the user is told about.
- `id`
- `visibility` (public, private)
- `user_id` → User (required when private; null when public)
- `kind` (news, alert, management_trigger, screener_hit, review_reminder)
- `trigger_state_id` → TriggerState (nullable; set for alert and management_trigger events, and through it the alert or position and the rule that fired)
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

## Alternative: a RuleSet table

A viable alternative to TriggerState's owner column, to weigh together with the [playbook design](playbooks.md#open-questions): rule sets become a table of their own, and every owner points at one.

- `Alert`, `Screener` (custom rules) and `PlaybookVersion` (entry, sizing and management rules) each reference `RuleSet` rows holding the rules.
- Trigger state is then keyed by rule set, rule key and subject, so it no longer names each kind of owner; a position's management triggers point at the rule set of the version it was entered under.
- `RuleViolation` could point at a rule set and rule key the same way, instead of a ref string.
- It isn't adopted yet because it changes how playbook versions store rules. If the playbook design moves to rule set rows, `TriggerState.alert_id` becomes a `rule_set_id`.

Owners can't instead hold a single `trigger_id` pointing at their state: each alert has one trigger state per rule per ticker in scope, and each position one per management rule, so the foreign key has to sit on TriggerState.

## Related

- [Rule engine](rule-engine.md) for the rule format and how triggers are read
- [News and digests](news-and-digests.md) for news alert events and session digests (private, so delivered in-app)
- [Users and access](users-and-access.md) for what is private and what is shared
- [Screener](screener.md) and [playbooks](playbooks.md) (management rules), the main sources of alert events
