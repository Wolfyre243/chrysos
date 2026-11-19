# Open Questions

Single source of truth for deferred decisions and unresolved questions.
Only **live** questions are kept here. Never reuse IDs; Pick the next number above the highest ever used
(see `Last ID used`), even after entries are removed.

**Last ID used:** OQ-007

## Index

| ID                 | Question                                                         | Area        | Status | Revisit when                                       |
| ------------------ | ---------------------------------------------------------------- | ----------- | ------ | -------------------------------------------------- |
| [OQ-001](#oq-001) | What is a rule evaluated against?                                | rule-engine | open   | Before the rule engine is implemented              |
| [OQ-002](#oq-002) | Should "trade" mean only a ticker plus legs?                     | rule-engine | open   | Together with OQ-001                               |
| [OQ-003](#oq-003) | Do indicators still need a `scope`?                              | analytics   | open   | Once OQ-001 is settled, before the registry is built |
| [OQ-004](#oq-004) | Where do sizing rules get the account's value from?              | rule-engine | open   | Before sizing rules and `risk_2pct` are built      |
| [OQ-005](#oq-005) | Where does soft enforcement record an unknown result?            | journal     | open   | Before soft enforcement and `RuleViolation` are built |
| [OQ-006](#oq-006) | Does moomoo OpenD meet Chrysos's data needs?                     | market-data | open   | Before OpenD replaces yfinance in Phase 1          |
| [OQ-007](#oq-007) | Which news sources replace Reuters, and what is the final list?  | news        | open   | Before news is built in Phase 1                    |

---

## Entries

<!-- newest at the bottom; keep the Index table and Last ID used in sync -->

<a id="oq-001"></a>

### OQ-001: What is a rule evaluated against?

- **Status:** open
- **Raised:** 2026-11-17
- **Area:** [rule-engine](concepts/rule-engine.md#evaluation), [screener](concepts/screener.md), [alerts](concepts/alerts.md), [journal](concepts/journal-and-trade-log.md#soft-enforcement)
- **Context:** The evaluation subject says what a rule is about. The screener, soft enforcement, management triggers and alerts each have to build one and read from it in code. Field groups and `EvalContext.subject` already assume one.
- **Why deferred:** The rule format and evaluator semantics are settled without it. Only the code that builds subjects depends on it, and none exists yet.
- **Revisit when:** Before the rule engine is implemented. The session should produce a worked example of each feature in code.
- **Options considered:** A) The working draft has three nested subjects: `ticker` (one underlying), `trade` (a ticker plus legs, proposed by selectors or filled) and `position` (a trade's current open legs plus its executions and P&L). A subject identifies what a rule is about, and field and indicator values are read from the data layer on demand.
- **Proposed ADR:** _none yet_

<a id="oq-002"></a>

### OQ-002: Should "trade" mean only a ticker plus legs?

- **Status:** open
- **Raised:** 2026-11-17
- **Area:** [rule-engine](concepts/rule-engine.md#fields), [GLOSSARY](references/GLOSSARY.md), [weekly-review](concepts/weekly-review.md)
- **Context:** The draft subjects in OQ-001 use "trade" for a ticker plus legs. About 15 places in the docs use "trade" for what is really a position (closed trades, trades in progress, journaling trades against a playbook), and `TradeGrade` grades a position.
- **Why deferred:** It is a naming question that depends on how OQ-001 settles.
- **Revisit when:** Together with OQ-001.
- **Options considered:** A) Narrow "trade" to a ticker plus legs and reword the docs that mean a position. B) Keep the loose usage and pick another name for the subject.
- **Proposed ADR:** _none yet_

<a id="oq-003"></a>

### OQ-003: Do indicators still need a `scope`?

- **Status:** open
- **Raised:** 2026-11-18
- **Area:** [analytics](concepts/analytics.md#indicator-registry), [rule-engine](concepts/rule-engine.md#evaluation)
- **Context:** Indicators declare a `scope` (stock, option, spread). Once evaluation subjects exist, every subject has a ticker, and legs reach an indicator as args, so `scope` may say nothing new.
- **Why deferred:** It depends on OQ-001.
- **Revisit when:** Once OQ-001 is settled, before the analytics registry is built.
- **Options considered:** A) Drop `scope`. B) Keep it, for example to filter which indicators the ticker page shows.
- **Proposed ADR:** _none yet_

<a id="oq-004"></a>

### OQ-004: Where do sizing rules get the account's value from?

- **Status:** open
- **Raised:** 2026-11-18
- **Area:** [rule-engine](concepts/rule-engine.md#fields), [playbooks](concepts/playbooks.md), [ADR 0007](adr/0007-rules-dont-do-arithmetic.md)
- **Context:** Sizing rules such as "max loss at most 2% of the account" compare a field such as `trade.max_loss_account_ratio` with 0.02 (ADR 0007). Computing that field needs the account's value, and nothing in the data model holds it yet.
- **Why deferred:** Sizing rules can be designed and stored without it. Only their evaluation needs the value.
- **Revisit when:** Before sizing rules and the `risk_2pct` add-on are built.
- **Options considered:** none yet
- **Proposed ADR:** _none yet_

<a id="oq-005"></a>

### OQ-005: Where does soft enforcement record an unknown result?

- **Status:** open
- **Raised:** 2026-11-18
- **Area:** [rule-engine](concepts/rule-engine.md#unknown-and-null), [journal](concepts/journal-and-trade-log.md#soft-enforcement)
- **Context:** A rule whose result is unknown, such as after a failed chain fetch, isn't a violation. It is recorded as unevaluated, so it counts neither for nor against adherence, but no entity holds that record yet.
- **Why deferred:** It only affects the soft enforcement tables, which aren't built yet.
- **Revisit when:** Before soft enforcement and `RuleViolation` are built.
- **Options considered:** none yet
- **Proposed ADR:** _none yet_

<a id="oq-006"></a>

### OQ-006: Does moomoo OpenD meet Chrysos's data needs?

- **Status:** open
- **Raised:** 2026-10-21
- **Area:** [architecture](architecture.md#moomoo-opend), [market-data](concepts/market-data.md), [roadmap](roadmap.md)
- **Context:** OpenD is the long-term `MarketDataProvider`. Three things are unverified: its request limits for chain and snapshot calls, whether the account is entitled to live US options quotes (OPRA), and whether it provides fundamentals and consensus earnings estimates. If not, those need a second `MarketDataProvider` implementation.
- **Why deferred:** Phase 0 uses yfinance while OpenD is evaluated.
- **Revisit when:** Before OpenD replaces yfinance in Phase 1.
- **Options considered:** none yet
- **Proposed ADR:** _none yet_

<a id="oq-007"></a>

### OQ-007: Which news sources replace Reuters, and what is the final list?

- **Status:** open
- **Raised:** 2026-10-21
- **Area:** [architecture](architecture.md#news-feeds), [news-and-digests](concepts/news-and-digests.md)
- **Context:** The candidate sources are CNBC, MarketWatch, Nasdaq, Fed press releases, SEC EDGAR, and per-ticker feeds from Yahoo Finance and Google News. Reuters discontinued its public RSS feeds around 2020 and needs an alternative.
- **Why deferred:** News is Phase 1.
- **Revisit when:** Before news is built in Phase 1.
- **Options considered:** none yet
- **Proposed ADR:** _none yet_
