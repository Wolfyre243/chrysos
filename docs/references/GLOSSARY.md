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
