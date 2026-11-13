# Rule engine

A single rule format and evaluator serves four features:

| Feature           | Rules used                         | Evaluated against               |
| ----------------- | ---------------------------------- | ------------------------------- |
| Screener          | Playbook entry rules               | Universe tickers                |
| Soft enforcement  | Playbook entry rules and checklist | Trade entry snapshot and plan   |
| Management alerts | Playbook management rules          | Open positions                  |
| Real-time alerts  | User alert rules                   | News events, prices, indicators |

A rule references either an analytics registry indicator or a known field (position state, earnings, price, news). Rules can be combined with `all` / `any` groups.

## References inside playbooks

Inside a playbook, rules can also use two kinds of reference, resolved before evaluation:

- `$legs.<slot>`: a leg slot of the playbook's structure (such as `$legs.front`), bound to the expiry and strike the edge's selectors picked for this ticker or position. This lets one edge work on a calendar, a diagonal or a double calendar without hardcoding DTEs.
- `$params.<name>`: a named playbook parameter, so a threshold can change without rewriting the rule.

Management alerts resolve these against the [playbook version](playbooks.md#parameters-and-changes) a position was entered under, not the playbook's current version. Entry checks and the screener use the current version.

```
{ "indicator": "forward_factor", "params": { "front": "$legs.front", "back": "$legs.back" }, "op": ">", "value": "$params.ff_min" }
{ "field": "earnings.between", "params": { "from": "$legs.front.expiry", "to": "$legs.back.expiry" }, "op": "==", "value": false }
{ "field": "legs.front.dte", "op": "<=", "value": "$params.exit_front_dte" }
{ "field": "position.pnl_pct", "op": ">=", "value": "$params.take_profit_pct" }
{ "field": "earnings.days_until", "op": "<", "value": 7 }
```

User alert rules use the same format with literal values, since they have no playbook to resolve references against.

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
