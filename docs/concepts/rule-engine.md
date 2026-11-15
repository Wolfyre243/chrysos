# Rule engine

Chrysos has one rule format and one evaluator, shared by four features:

| Feature           | Rules used                         | Evaluated against               |
| ----------------- | ---------------------------------- | ------------------------------- |
| Screener          | Playbook entry rules               | Universe tickers                |
| Soft enforcement  | Playbook entry rules and checklist | Trade entry snapshot and plan   |
| Management alerts | Playbook management rules          | Open positions                  |
| Real-time alerts  | User alert rules                   | News events, prices, indicators |

The sections below build up from a single condition to a full rule, then cover the references that let playbook rules avoid hardcoded values, and end with a screener run that puts them together.

## Conditions

A condition compares one value against a threshold. It references either an [analytics registry](analytics.md) indicator or a known field (position state, earnings, price, news), plus an `op` and a `value`:

```json
{ "field": "earnings.days_until", "op": "<", "value": 7 }
```

Some indicators and fields need arguments, which go in `params`. Conditions combine into `all` / `any` groups, and groups can be nested:

```json
{
  "all": [
    { "field": "price", "op": ">=", "value": 20 },
    { "field": "avg_volume", "op": ">=", "value": 1000000 }
  ]
}
```

## Rules

A rule wraps one condition with the metadata the features need: which list it belongs to (`kind`), which playbook block contributed it (`source`), how serious a failure is (`severity`) and a human `description`. The full field list is in the [data model](#rule) below.

Rules have no table of their own. A [playbook version](playbooks.md#playbookversion) stores them as JSONB arrays (`entry_rules`, `management_rules`, `sizing_rules`). An [AlertRule](alerts.md#alertrule) uses the same format in its `condition` column.

Entry rules also get a derived `stage`, which the [screener](screener.md#stage-assignment) uses to save quota: `stage1` if the condition needs only snapshot-level data (price, volume, earnings dates, fundamentals), `stage2` if it needs an option chain. The stage applies to the whole rule, so a group that mixes the two kinds of data runs entirely in stage 2. Keep cheap checks in their own rule so they can still filter the universe in stage 1.

## References inside playbooks

The same edge should work with any structure and any thresholds, so playbook rules avoid hardcoding them. Two kinds of reference are resolved before evaluation:

- `$legs.<slot>`: a leg slot of the playbook's structure (such as `$legs.front`), bound to the expiry and strike the edge's selectors picked for this ticker or position. This lets one edge work on a calendar, a diagonal or a double calendar without hardcoding DTEs.
- `$params.<name>`: a named playbook parameter, so a threshold can change without rewriting the rule.

```
{ "indicator": "forward_factor", "params": { "front": "$legs.front", "back": "$legs.back" }, "op": ">", "value": "$params.ff_min" }
{ "field": "earnings.between", "params": { "from": "$legs.front.expiry", "to": "$legs.back.expiry" }, "op": "==", "value": false }
{ "field": "legs.front.dte", "op": "<=", "value": "$params.exit_front_dte" }
{ "field": "position.pnl_pct", "op": ">=", "value": "$params.take_profit_pct" }
```

The two uses of "params" are unrelated: a condition's `params` key holds arguments for its indicator or field (`front`, `back`, `from`, `to`), while `$params.<name>` points at a playbook parameter.

The screener and entry checks resolve references against the playbook's current version. Management alerts resolve them against the [version](playbooks.md#parameters-and-changes) the position was entered under. User alert rules have no playbook to resolve against, so they use literal values only.

## Example: a screener run

Here is part of an "FF calendar" playbook version with two entry rules (other columns omitted, shapes illustrative):

```json
{
  "id": 42,
  "params": { "ff_min": 0.2, "min_price": 20, "min_avg_volume": 1000000 },
  "entry_rules": [
    {
      "id": "ff_threshold",
      "kind": "entry",
      "source": "edge:forward_factor",
      "stage": "stage2",
      "severity": "critical",
      "description": "Forward factor above minimum",
      "condition": {
        "indicator": "forward_factor",
        "params": { "front": "$legs.front", "back": "$legs.back" },
        "op": ">",
        "value": "$params.ff_min"
      }
    },
    {
      "id": "underlying_liquidity",
      "kind": "entry",
      "source": "addon:liquidity",
      "stage": "stage1",
      "severity": "warning",
      "description": "Liquid underlying",
      "condition": {
        "all": [
          { "field": "price", "op": ">=", "value": "$params.min_price" },
          { "field": "avg_volume", "op": ">=", "value": "$params.min_avg_volume" }
        ]
      }
    }
  ]
}
```

A screener on this playbook has no rules of its own beyond optional `stage1_filters`. A nightly run works like this:

1. The `ScreenerRun` records `playbook_version_id = 42`, which freezes that version.
2. Stage 1 evaluates the `stage1` rules and the screener's `stage1_filters` against snapshot data for the whole universe. `$params` are resolved first, so `underlying_liquidity` becomes `price >= 20` and `avg_volume >= 1000000`.
3. Stage 2 runs only on the tickers that passed stage 1. The edge's selectors pick legs for each one (for AAPL, say, front 2026-12-18 and back 2027-01-15, both 230 calls). The engine fetches just those chains, binds `$legs.*` and evaluates the `stage2` rules. Here `forward_factor` is 0.27, which passes `> 0.2`.
4. Each ticker that passes is saved as a `ScreenerResult` with its proposed `legs`, its indicator `metrics` and a rank.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### Rule
*(value object, stored as JSONB)* Shared format used in PlaybookVersion and AlertRule.
- `id` (stable within its parent)
- `kind` (entry, management, sizing, alert)
- `condition` (indicator or field reference, params, op, value; or `all` / `any` group). Inside playbooks, params and values may reference `$legs.<slot>` and `$params.<name>`
- `source` (block that contributed it, such as `edge:forward_factor` or `addon:risk_2pct`, or `user`; playbook rules only)
- `stage` (derived for entry rules: `stage1` if it needs only snapshot-level data, `stage2` if it needs a chain)
- `description`
- `severity` (info, warning, critical)

## Related

- [Playbooks](playbooks.md), the main source of rules
- [Analytics](analytics.md) for the indicators rules can reference
- [Screener](screener.md) for how entry rules are split into stages
- Data model: [ChecklistItem](playbooks.md#checklistitem) and [AlertRule](alerts.md#alertrule), stored alongside rules
