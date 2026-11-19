# Analytics

Numbers and research that brokerage platforms don't provide.

## Indicator registry

Every indicator or calculator is a plugin registered in code. Once registered, it appears on the ticker page, in entry snapshots and in [rules](rule-engine.md#indicators) (and so in screeners, soft enforcement and alerts), with no other changes. An indicator is any formula Chrysos owns; a value the provider supplies as is, or plain arithmetic with one possible definition, is a [field](rule-engine.md#fields) instead. Each plugin declares:

| Field        | Meaning                                                                                                   |
| ------------ | --------------------------------------------------------------------------------------------------------- |
| `id`, `name` | Identifier and display name                                                                               |
| `version`    | Bumped whenever the formula changes                                                                       |
| `scope`      | `stock`, `option` or `spread` (may be dropped; see [OQ-003](../open-questions.md#oq-003)) |
| `requires`   | Data needed, from the shared set: `quote`, `price_history`, `earnings`, `fundamentals`, `chain`           |
| `args`       | Argument schema, such as the two legs forward factor compares                                             |
| `output`     | `scalar`, `per_strike_series` or `term_curve`                                                             |
| `scalars`    | For non-scalar outputs, the named scalar values rules can use, such as GEX's `call_wall`                  |

The output type selects the visualisation on the ticker page. Scalar outputs, and the named scalars of other outputs, can be used in rules. "Params" is never used for indicator arguments; it only means [playbook parameters](rule-engine.md#thresholds-and-params). Snapshots store the indicator version, so historical values are only compared within the same formula version. New stock or option indicators can be added without changes elsewhere.

## Starter indicators

Forward factor, IV term structure, expected move, and gamma exposure (per-strike GEX, call and put walls, gamma flip). GEX runs end of day because open interest only updates daily.

## Fundamentals indicators and health score

- P/E and other fundamentals metrics are registry indicators like the rest (`scope` stock, `requires` fundamentals), so rules can use them. Rules read P/E only through this indicator; the provider's `pe_ratio` stored on [FundamentalsSnapshot](market-data.md#fundamentalssnapshot) is an input, not a field rules can read, since it goes stale as soon as the price moves.
- The health score is an in-house grade of a stock's overall health and profitability, built from fundamentals such as P/E, margins and revenue. It is a registry indicator too, so a playbook can filter on it.

Both wait on confirming a fundamentals source (see the moomoo "To verify" list in [architecture.md](../architecture.md#moomoo-opend)).

## Research files

A user's file on one stock: a summary of how its business works, plus every [note](journal-and-trade-log.md#notes) that mentions the ticker. Observations and outside factors that could help or hurt the stock are ordinary notes, tagged with hashtags such as `#risk` or `#tailwind`.

## Earnings analysis

Gathers what the market expects from a company's upcoming earnings, so trades around the report can be weighed against what is already priced in.

## Ticker page

Everything about one ticker in one view. The price chart overlays news, the user's own entries and exits, and GEX levels. Below it sit the analytics panels, the user's notes on the ticker (notes that mention it and notes linked to positions on it), recent news, and open positions with their rule status.

## Data model

Table conventions and the index of all entities are in [data-model.md](../references/data-model.md).

### Indicator
*(code)*
- `id`
- `name`
- `version`
- `scope` (stock, option, spread)
- `requires` (quote, price_history, earnings, fundamentals, chain)
- `args_schema`
- `output_type` (scalar, per_strike_series, term_curve)
- `scalars` (named scalar outputs, for non-scalar output types)

### IndicatorResult
Cached computed values. Shared across users.
- `id`
- `symbol` → Ticker
- `indicator_id`
- `indicator_version`
- `args` (JSONB)
- `args_hash`
- `as_of`
- `snapshot_id` → ChainSnapshot (nullable)
- `fundamentals_snapshot_id` → FundamentalsSnapshot (nullable, fundamentals indicators only)
- `value` (JSONB)

P/E and the health score are indicators with `scope` stock and `requires` fundamentals, so they have no tables of their own. The health score's `value` holds `score` (0 to 100), `grade` (A to F, derived from `score`) and `components` (sub-score per factor, such as valuation, margins, revenue).

### TickerResearch
A user's research file on one ticker. Private to that user; unique on (`user_id`, `symbol`). The file's entries are the user's notes that mention the ticker (see [NoteTicker](journal-and-trade-log.md#noteticker)); they aren't stored here.
- `id`
- `user_id` → User
- `symbol` → Ticker
- `business_summary` (how the company makes money, its segments and competitors)
- `last_reviewed_at`

## Related

- [Market data](market-data.md), the inputs to every indicator
- [Rule engine](rule-engine.md) for using indicators as rule conditions
- [EarningsEvent](market-data.md#earningsevent), [EarningsExpectation](market-data.md#earningsexpectation) and [FundamentalsSnapshot](market-data.md#fundamentalssnapshot), the stored inputs to earnings analysis and fundamentals indicators
