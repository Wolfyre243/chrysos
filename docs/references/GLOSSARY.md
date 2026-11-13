# Glossary

**Playbook version**: a snapshot of a playbook written by one save. Positions record the version they were entered under and are managed under it until they close. See [playbooks](../concepts/playbooks.md#parameters-and-changes).

**Public playbook**: a playbook its owner has shared with all users. Anyone can journal trades against it; only the owner edits it. The trades made with it stay private. See [playbooks](../concepts/playbooks.md#public-playbooks).

**Public screener**: the one screener a public playbook may have, run by the playbook's owner. Its hits are shared and posted to the Discord server. See [screener](../concepts/screener.md#public-and-private-screeners).

**Block update**: a playbook version written automatically when a deploy bumps the version of a structure, edge or add-on the playbook uses. One per playbook per deploy.

**Orphaned override**: a user override whose rule a block update removed or renamed. Kept and flagged, never dropped silently.

**Suggestion**: a finding from self-analytics or a model about a playbook, shown in the weekly review. It never changes the playbook; the user acts on it by hand. See [weekly review](../concepts/weekly-review.md#suggestions). Avoid: *change proposal* (removed, see [ADR 0001](../adr/0001-public-playbooks-without-change-proposals.md)).
