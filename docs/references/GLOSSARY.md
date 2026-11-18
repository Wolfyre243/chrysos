# Glossary

**Playbook version**: a snapshot of a playbook written by one save. Positions record the version they were entered under and are managed under it until they close. See [playbooks](../concepts/playbooks.md#parameters-and-changes).

**Public playbook**: a playbook its owner has shared with all users. Anyone can journal trades against it; only the owner edits it. The trades made with it stay private. See [playbooks](../concepts/playbooks.md#public-playbooks).

**Public screener**: the one screener a public playbook may have, run by the playbook's owner. Its hits are shared and posted to the Discord server. See [screener](../concepts/screener.md#public-and-private-screeners).

**Block update**: a playbook version written automatically when a deploy bumps the version of a structure, edge or add-on the playbook uses. One per playbook per deploy.

**Orphaned override**: a user override whose rule a block update removed or renamed. Kept and flagged, never dropped silently.

**Note**: markdown text the trader writes, either a thesis or a journal note. Private to its author. See [journal and trade log](../concepts/journal-and-trade-log.md#notes). Avoid: *hunch*, *idea*, *research note*.

**Thesis**: a note holding a trade idea, written whenever it comes up (watching the news, on the go). Most never become trades. A thesis can be linked to any number of positions, for example when re-entering on the same idea; a position doesn't need one.

**Journal note**: a note about one position, written while the trade plays out.

**Mention**: a cashtag (`$AAPL`) in a note's text that resolves to a ticker. Mentions link notes and tickers both ways. Only tickers can be mentioned. Avoid: *subject*.

**Feeling**: the trader's emotional state at a fill (opening, adjusting, rolling or closing), picked from a fixed list with an intensity, so it can be compared with results.

**Suggestion**: a finding from self-analytics or a model about a playbook, shown in the weekly review. It never changes the playbook; the user acts on it by hand. See [weekly review](../concepts/weekly-review.md#suggestions). Avoid: *change proposal* (removed, see [ADR 0001](../adr/0001-public-playbooks-without-change-proposals.md)).

**Comparison**: one value checked against another, such as forward factor above the playbook's minimum. The smallest part of a condition. See [rule engine](../concepts/rule-engine.md).

**Condition**: a true/false expression built from comparisons joined with *and*, *or* and *not*, which can be nested.

**Rule**: a named condition with one purpose, such as one of a playbook's entry, sizing or management rules, one of a screener's custom rules, or one of an alert's rules. Avoid: *criteria*, *filter*, *check*.

**Disabled rule**: a rule the user has switched off. It stays in its playbook and version history but is skipped during evaluation. See [ADR 0002](../adr/0002-rules-without-severity.md).

**Unknown result**: what a comparison gives when a value couldn't be found, such as after a failed chain fetch. It is neither true nor false, and differs from a value that doesn't exist, such as an earnings date that hasn't been announced. See [rule engine](../concepts/rule-engine.md).

**Rule set**: the rules one owner keeps for one purpose, such as a playbook version's entry rules, a screener's custom rules or an alert's rules. There are no standalone rules outside a rule set.

**Requirement**: a rule read together with the rest of its rule set, all of which must be true. The screener and soft enforcement read rules this way. The feature decides how a rule is read; the rule itself only states a fact.

**Trigger**: a rule read on its own, whose true result makes Chrysos act, such as a management rule raising an alert event. Management triggers and alerts read rules this way.

**Custom rule**: a screener's own rule, added to its playbook's entry rules to narrow that screener's results. Never read by soft enforcement or management triggers. Avoid: *add-on*, *extra rule*, *filter*.

**Field**: a named value a rule can read about a ticker, a trade's legs or a position, such as price or days to expiry. Stored by Chrysos, supplied as is by a provider, or simple arithmetic with only one possible definition; anything with a formula of Chrysos's own is an indicator. See [rule engine](../concepts/rule-engine.md#fields).

**Indicator**: a value Chrysos calculates with its own versioned formula, such as forward factor or P/E. Any calculation a rule needs is an indicator. See [analytics](../concepts/analytics.md#indicator-registry).

**Alert**: a user's standing watch: a scope, a cooldown and rules each read as a trigger. Avoid: *alert rule*.

**Alert event**: one thing the user is told about, raised by an alert, a management trigger, high-importance news, a screener run or a reminder. Public or private.
