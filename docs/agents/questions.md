# Open questions and deferred decisions

**Lifecycle:** `open` or `blocked` → resolved.

**Promotion rule:** if a question already has concrete options and trade-offs,
write a `Proposed` ADR instead and link it from the entry.

**Size rule:** an entry longer than ~10 lines should become a `Proposed` ADR.

- All unresolved or deferred questions go in `docs/open-questions.md`, using
  the template there. Use the next ID after `Last ID used`, then update that
  counter and the Index table.
- Never write open questions, "TBD"s or "?" sections inside other docs
  (concepts, references, architecture, roadmap). Instead, add a single line at
  the relevant spot: `> Open: see [OQ-XXX](../open-questions.md#oq-xxx)`.
- If a question already has clear options and trade-offs, propose an ADR
  (status: Proposed) instead, and link it from the OQ entry.
- Every entry needs a concrete "Revisit when" trigger. If the user hasn't given
  one, propose one and ask.
- At the start of a design or planning session, read `docs/open-questions.md`
  and surface any question whose "Revisit when" condition now applies, or whose
  "Raised" date is more than ~60 days old. For each, ask the user to decide,
  drop, or re-defer it.
- Don't answer or decide an open question yourself; raise it with the user.

## When a question is resolved
1. Write the ADR. Its Context section must capture the question and the
   reasoning, since the OQ entry is about to be deleted.
2. Delete the OQ entry and its Index row from `docs/open-questions.md`.
3. In every doc that has an inline `> Open: see [OQ-XXX]` link, replace it
   with a link to the ADR (or remove it if the doc's content already reflects
   the decision).
4. Never reuse the removed ID, and don't lower `Last ID used`.
5. If a question is dropped rather than decided, delete it the same way and
   tell the user so they can decide whether it deserves a short ADR.

## Template (copy for each new entry)

### OQ-XXX: <question phrased as a question?>

- **Status:** open | blocked
- **Raised:** YYYY-MM-DD
- **Area:** [concept-doc](concepts/xxx.md), [other-doc](concepts/yyy.md)
- **Context:** 1-3 sentences on why this came up
- **Why deferred:** what makes it safe to wait
- **Revisit when:** a concrete trigger (a milestone, "before X is built", or a date)
- **Options considered:** A) ... B) ... (or "none yet")
- **Proposed ADR:** _(link, if one has been drafted)_