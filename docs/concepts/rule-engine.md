# Rule engine

Chrysos has one rule format and one evaluator. Rules are written, stored and exported as JSON only ([ADR 0004](../adr/0004-rules-are-json-only.md)): Pydantic models parse the JSON into a tree of conditions, which is checked when it is saved and evaluated when a feature runs.

| Feature | Evaluates | Rules stored on | Reads results as |
| --- | --- | --- | --- |
| [Screener](screener.md) | Its playbook's entry rules, plus its own custom rules | Playbook version; screener | Requirements |
| [Soft enforcement](journal-and-trade-log.md#soft-enforcement) | The playbook's entry and sizing rules | The playbook version the position is entered under | Requirements |
| Management triggers | The playbook's management rules | The playbook version the position was entered under | Triggers |
| [Alerts](alerts.md) | The alert's own rules | Alert | Triggers |

News, screener-hit and reminder alert events evaluate no rules.

The sections below build up from what a rule can read (fields and indicators), to operands and conditions, to rules and rule sets. They then cover how features read results, unknown values, evaluation and validation, and end with a screener run that puts it together.

## Fields and indicators

Rules read two kinds of value, both declared in code. Neither is defined inside a rule; rules combine them.

### Fields

A field is a value Chrysos stores or the provider supplies as is, or plain arithmetic with only one possible definition, such as days to expiry or P&L. Fields take no arguments and have no version. They are declared in groups, like the columns of a table:

```python
class TickerFields(FieldGroup, prefix="ticker", subject=Subject.TICKER):
  price = Field(
    Type.NUMBER,
    Unit.USD,
    requires={Requires.QUOTE},
    description="Latest price",
  )
  next_earnings_date = Field(
    Type.DATE,
    nullable=True,
    requires={Requires.EARNINGS},
    description="Date of the next scheduled earnings report",
  )
```

A field's id is its group's `prefix` plus its name, such as `ticker.price`, so it is never typed twice and never depends on a class name. Group classes end in `Fields` so they don't clash with table classes such as `Ticker` and `Position`.

| Group | Subject | Example fields |
| --- | --- | --- |
| `ticker` | ticker | `price`, `avg_volume_20d`, `option_volume_20d`, `next_earnings_date` |
| `leg` | trade, once per leg | `expiry`, `dte`, `strike`, `right`, `side`, `mark`, `iv`, `delta`, `open_interest` |
| `trade` | trade | `net_debit`, `max_loss`, `quantity`, `min_leg_open_interest`, `max_leg_spread_ratio` |
| `position` | position | `pnl`, `pnl_ratio`, `days_held` |

Each field declares:

- `type`: `number`, `integer`, `bool`, `date` or `enum` (a value from a declared list).
- `unit`, with one convention everywhere: ratios and percentages are fractions (`0.25` is 25%, and the UI shows 25%); durations, DTE included, are whole calendar days; money is USD; dates are ISO trading dates in `America/New_York`.
- `nullable`: whether the value can legitimately be missing, such as an earnings date that hasn't been announced (see [unknown and null](#unknown-and-null)).
- `requires`: the kinds of provider call the value needs (see [below](#requires)).
- `per_leg`: a leg field needs a leg slot, such as the front leg's DTE.
- `description`.

Field names are snake_case. A lookback window is a suffix (`_20d`), dates end in `_date`, and ratios end in `_ratio` and are fractions, never `_pct`, so nobody wonders whether 25 means 25% or 2500%.

Rules that apply across structures, such as an add-on's, can't name leg slots. Per-leg checks read summary fields on the trade that cover every leg instead, such as `trade.min_leg_open_interest` ([ADR 0006](../adr/0006-per-leg-checks-use-trade-summary-fields.md)).

### Indicators

An indicator is a formula Chrysos owns that could reasonably be defined differently, or might change: forward factor, expected move, GEX, IV rank, P/E, the health score. Indicators come from the [analytics registry](analytics.md#indicator-registry). Each is versioned and declares its arguments (`args`) with types, and a rule passes it arguments that are themselves operands.

What makes a value a field or an indicator is whose formula it is, not how cheap it is. P/E needs only fundamentals but is an indicator, because trailing or forward and which EPS are formula choices. A leg's `iv` needs a chain but is a field, because the provider supplies it as is.

An indicator whose output isn't a single value (`per_strike_series` or `term_curve`) declares named scalar outputs, such as GEX's `call_wall`, `put_wall` and `flip`, and a rule picks one with `output`.

Rules don't pin indicator versions. Evaluation always uses the current version, and stored results record the version they were computed with ([ADR 0003](../adr/0003-rules-dont-pin-indicator-versions.md)).

### Requires

`requires` lists the kinds of provider call a field or indicator needs, from a fixed set:

| `requires` | Data | Screener stage |
| --- | --- | --- |
| `quote` | Latest price and volume | 1 |
| `price_history` | Daily bars | 1 |
| `earnings` | Earnings dates | 1 |
| `fundamentals` | Reported financials | 1 |
| `chain` | An option chain, one call per expiry | 2 |
| (nothing) | Data Chrysos already holds: legs, positions, executions | 1, except legs |

The screener derives each rule's stage from these: a rule runs in stage 2 if anything in it requires `chain` or reads a leg, because legs are only picked in stage 2. Every other rule runs in stage 1. The stage is never stored on a rule. Outside the screener, `requires` tells a job what to fetch.

## Operands

An operand is a value a comparison reads. It is either a bare JSON literal or an object whose `kind` names it:

| Kind | JSON | Value comes from |
| --- | --- | --- |
| Literal | `0.2`, `true`, `"2026-12-18"` | The rule itself |
| `param` | `{ "kind": "param", "name": "ff_min" }` | The playbook version's params |
| `field` | `{ "kind": "field", "id": "ticker.price" }` | The field catalog, read from the data layer |
| `field` on a leg | `{ "kind": "field", "id": "leg.dte", "leg": "front" }` | The same, for one leg slot |
| `leg` | `{ "kind": "leg", "slot": "front" }` | The subject's leg in that slot, passed whole to an indicator |
| `indicator` | `{ "kind": "indicator", "id": "forward_factor", "args": { … } }` | The analytics registry, computed from its resolved args |
| `indicator` with `output` | `{ "kind": "indicator", "id": "gex", "output": "call_wall" }` | One named scalar of a non-scalar indicator |

A leg slot is always its own property, never part of a string, so a misspelt slot fails when the rule is saved. Leg slots come from a playbook's structure, so playbook rules and a screener's [custom rules](screener.md#custom-rules) can use them and alerts can't. Params also come from the playbook, but only playbook rules use them: custom rules and alerts use literals.

## Conditions

A condition is a tree. Each node is an object whose `op` names it. Operator names and argument order follow Drizzle ORM, in snake_case:

| Ops | JSON |
| --- | --- |
| `eq`, `ne`, `gt`, `gte`, `lt`, `lte` | `{ "op": "gt", "left": …, "right": … }` |
| `between`, `not_between` (inclusive) | `{ "op": "between", "left": …, "min": …, "max": … }` |
| `in_array`, `not_in_array` | `{ "op": "in_array", "left": …, "values": [ … ] }` |
| `is_null`, `is_not_null` | `{ "op": "is_null", "operand": … }` |
| `and`, `or` | `{ "op": "and", "conditions": [ … ] }` |
| `not` | `{ "op": "not", "condition": … }` |

Either side of a comparison can be any operand, so a rule can compare front IV with back IV, or the price with the GEX call wall. Rules don't do arithmetic: any calculation is an indicator or a field instead ([ADR 0007](../adr/0007-rules-dont-do-arithmetic.md)).

For example, "no earnings between the legs", treating an unannounced earnings date as no earnings:

```json
{
  "op": "or",
  "conditions": [
    {
      "op": "is_null",
      "operand": { "kind": "field", "id": "ticker.next_earnings_date" }
    },
    {
      "op": "not_between",
      "left": { "kind": "field", "id": "ticker.next_earnings_date" },
      "min": { "kind": "field", "id": "leg.expiry", "leg": "front" },
      "max": { "kind": "field", "id": "leg.expiry", "leg": "back" }
    }
  ]
}
```

## Rules and rule sets

A rule is a named condition with exactly four properties:

```json
{
  "key": "ff_above_min",
  "label": "Forward factor above minimum",
  "enabled": true,
  "condition": {
    "op": "gt",
    "left": {
      "kind": "indicator",
      "id": "forward_factor",
      "args": {
        "front": { "kind": "leg", "slot": "front" },
        "back": { "kind": "leg", "slot": "back" }
      }
    },
    "right": { "kind": "param", "name": "ff_min" }
  }
}
```

- `key`: snake_case (`^[a-z][a-z0-9_]*$`), unique within its owner, and never renamed or reused once shipped; a rename counts as a removal plus an addition. A key states the fact that holds when the condition is true (`ff_above_min`, `profit_target_reached`), so it reads naturally however a feature uses the rule.
- `label`: shown in the UI.
- `enabled`: a disabled rule stays in place, in version history and diffs, but evaluation skips it ([ADR 0002](../adr/0002-rules-without-severity.md)).
- `condition`.

Nothing else is stored on a rule. The rule set it sits in says what it is for, its owner is part of its ref, its screener stage is derived, and there is no severity.

A rule set is the rules one owner keeps for one purpose: a playbook version's entry, sizing and management rules, a screener's custom rules, an alert's rules. Rules only exist inside a rule set; there is no registry of standalone rules. Edges and add-ons are [playbook blocks](playbooks.md#building-blocks) that own their default rules.

A playbook rule is referred to elsewhere, such as in a rule violation, by its ref, `<owner>/<key>`. The owner is the block the rule came from or `user`: `edge:forward_factor/ff_above_min`, `addon:liquidity_baseline/price_above_min`, `user/no_meme_stocks`. Checklist items use the same refs. How a playbook version records each rule's owner is an [open question for playbooks](playbooks.md#open-questions).

### Thresholds and params

A playbook rule names its thresholds as params (`{ "kind": "param", "name": "ff_min" }`) instead of writing the number in. The value lives once in the playbook version's `params` (`"ff_min": 0.2`). Every playbook on the same edge sets its own value, a change shows in the version diff as `ff_min: 0.2 → 0.25`, one value can feed several rules, and backtests can sweep it without touching any rule. How blocks declare params, and whether users can declare their own, are [open questions for playbooks](playbooks.md#open-questions).

## How features read results

A rule only states a fact: it comes out true, false or unknown. The feature decides what that means, in one of two ways:

- Requirements: the rule set is read together, and every enabled rule must be true, like one `and` over all of them. The screener keeps a ticker only if all pass. Soft enforcement records a violation for each rule that is false.
- Triggers: each rule is read on its own, and a true result makes Chrysos act. Management triggers and alerts raise one alert event per rule that fires, with its own message, and none waits on the others. There is no overall verdict, because which rule fired matters: taking profit and exiting on DTE lead to different messages.

A trigger fires when it becomes true, can't fire again until it has been false and its cooldown has passed, and ignores unknown results ([ADR 0005](../adr/0005-triggers-fire-on-becoming-true.md)). The cooldown belongs to whatever raises the alert event, never to the rule (see [alerts](alerts.md#triggers)).

## Unknown and null

A comparison whose value can't be found, such as after a failed chain fetch, is unknown, not false. Results follow SQL's NULL rules:

| `and` | true | false | unknown |
| --- | --- | --- | --- |
| **true** | true | false | unknown |
| **false** | false | false | false |
| **unknown** | unknown | false | unknown |

| `or` | true | false | unknown |
| --- | --- | --- | --- |
| **true** | true | true | true |
| **false** | true | false | unknown |
| **unknown** | true | unknown | unknown |

`not` swaps true and false; unknown stays unknown.

Null is different: the value genuinely doesn't exist, such as an earnings date that hasn't been announced. Comparing null with anything gives unknown, as in SQL, but `is_null` and `is_not_null` test for it explicitly. A failed read stays unknown, even inside `is_null`.

What each feature does with unknown:

- Screener: the ticker doesn't pass.
- Soft enforcement: it isn't a violation. It is recorded as unevaluated, so it counts neither for nor against adherence; where it is recorded is an [open question](#open-questions).
- Triggers: unknown never fires and doesn't count as false.

## Evaluation

`evaluate(condition, ctx)` walks the tree and returns an outcome: true, false or unknown. The context carries the subject the rule is about, the params and access to the data layer:

```python
@dataclass(frozen=True)
class EvalContext:
  subject: Subject  # what the rule is about (see open questions)
  params: dict[str, Value]  # the playbook version's params; {} otherwise
  data: MarketData  # cached quotes, chains, earnings, positions
```

Each operand is resolved as listed under [operands](#operands): a param from `ctx.params`, a field through the field catalog, an indicator by computing it from its resolved args. `and` and `or` stop as soon as the result is decided, so a failing cheap check means a chain is never fetched.

The three-valued helpers are `and_`, `or_` and `not_` in `chrysos/rules/outcome.py`. SQLModel exports SQLAlchemy's `and_`, `or_` and `not_` for building queries, and the standard library's `operator` module has its own, so these are always called through their module (`outcome.and_(...)`) and never imported by name.

## Validation

Rules are checked when they are saved, and every block's rules are checked at startup and in tests. Each error names its path in the rule, such as `entry_rules[0].condition.left.args.front`:

1. Every node has a known `op` or `kind` and the properties that go with it.
2. Every field exists in the catalog and is available on the rule set's subject.
3. Every indicator exists in the registry, its args match its declared args, and it gives a scalar: a scalar indicator has no `output`, and any other names one of its declared scalars.
4. Every param exists in the playbook's params. Custom rules and alerts can't use params.
5. Every leg slot exists on the playbook's structure. Add-on rules can't use leg slots unless the add-on declares its structures, and alerts can't use them at all.
6. Each operator fits the types and units of its operands: no `gt` on a bool, no comparing a ratio with days, and `in_array` values match the left side's type.

## Example: a screener run

Alice owns the public "FF calendar" playbook. Its version 42 has these entry rules:

| Ref | Condition | Stage |
| --- | --- | --- |
| `addon:liquidity_baseline/price_above_min` | `ticker.price` ≥ `min_price` (20) | 1 |
| `addon:liquidity_baseline/volume_above_min` | `ticker.avg_volume_20d` ≥ `min_avg_volume` (1,000,000) | 1 |
| `edge:forward_factor/no_earnings_between_legs` | Next earnings date not between the two expiries | 2 (reads legs) |
| `edge:forward_factor/ff_above_min` | Forward factor > `ff_min` (0.2) | 2 (needs a chain) |

Bob has a private screener on her playbook with two custom rules: `price_below_300` (stage 1) and `ff_above_0_3`, forward factor above 0.3 (stage 2). A nightly run of Bob's screener works like this:

1. The `ScreenerRun` records `playbook_version_id = 42` and a copy of Bob's custom rules, which freezes both for this run.
2. Stage 1 evaluates the stage 1 rules for the whole universe: Alice's price and volume rules and Bob's price rule. 600 tickers become 80.
3. Stage 2 runs only on those 80. The edge's selectors pick legs for each one (for AMZN, say, front 2026-12-18 and back 2027-01-15, both 210 calls). The engine fetches just those chains and evaluates the stage 2 rules. AMZN's forward factor is 0.34, which passes both `> 0.2` and `> 0.3`; AAPL's 0.27 passes Alice's rule but not Bob's.
4. Each ticker that passes every rule is saved as a `ScreenerResult` with its proposed legs, its indicator metrics and a rank.

## Open questions

These are deferred to their own design session:

- Evaluation subjects: what a rule is evaluated against, and how the screener, soft enforcement, management triggers and alerts each build one and read from it in code. Working draft: three nested subjects, `ticker` (one underlying), `trade` (a ticker plus legs, proposed by selectors or filled) and `position` (a trade's current open legs plus its executions and P&L). A subject identifies what a rule is about (the symbol, the legs, the position); field and indicator values are read from the data layer when a rule asks for them. The session should produce a worked example of each feature in code.
- Whether "trade" is narrowed to mean a ticker plus legs. About 15 places in the docs use "trade" for what is really a position (closed trades, trades in progress, journaling trades against a playbook), and `TradeGrade` grades a position.
- Whether indicators still need a `scope` (stock, option, spread) once subjects are settled, since every subject has a ticker and legs reach an indicator as args.
- Where sizing rules such as "at most 2% of the account" get the account's value from, for a field such as `trade.max_loss_account_ratio` ([ADR 0007](../adr/0007-rules-dont-do-arithmetic.md)). Nothing in the data model holds it yet.
- Where soft enforcement records a rule whose result was unknown, since it isn't a violation.

How trigger state is stored is an open question on the [alerts](alerts.md#open-questions) page.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### Rule
*(value object, stored as JSONB)* One named condition inside a rule set. Rule sets are stored on PlaybookVersion (`entry_rules`, `sizing_rules`, `management_rules`), Screener and ScreenerRun (`custom_rules`) and Alert (`rules`).
- `key` (snake_case, unique within its owner, never renamed or reused)
- `label`
- `enabled`
- `condition` (a condition node; see [conditions](#conditions) and [operands](#operands))

### Field
*(code)* A value rules can read, declared in a field group.
- `id` (`<prefix>.<name>`, such as `ticker.price`)
- `subject` (ticker, trade or position; a working draft, see open questions)
- `per_leg`
- `type` (number, integer, bool, date, enum)
- `unit`
- `nullable`
- `requires` (quote, price_history, earnings, fundamentals, chain)
- `description`

## Related

- [Playbooks](playbooks.md), the main owner of rule sets
- [Analytics](analytics.md) for the indicators rules can call
- [Screener](screener.md) for stages and custom rules
- [Alerts](alerts.md) for alerts, triggers and cooldowns
- [Journal and trade log](journal-and-trade-log.md#soft-enforcement) for how violations are recorded
- ADRs [0002](../adr/0002-rules-without-severity.md) to [0007](../adr/0007-rules-dont-do-arithmetic.md) for the decisions behind this page
