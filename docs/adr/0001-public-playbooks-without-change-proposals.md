# 0001: Public playbooks, without change proposals or forks

- Status: accepted
- Date: 2026-11-14

## Context

Chrysos is used by a small group who often trade the same strategies. Playbooks and screeners were private per user, so the same playbook had to be built once per user, and two users screening the same strategy fetched the same chains twice each night.

Structural playbook changes were queued as `PlaybookChangeProposal` rows and applied or rejected in the weekly review. That queue existed so rules wouldn't change in the middle of a trade. A shared playbook made it awkward: whose review resolves a proposal, and how would one user's self-analytics avoid leaking into another user's playbook?

## Decision

- Playbooks get a `visibility` flag, like watchlists. Anyone can journal against a public playbook; only its owner edits it. A public playbook can't go private or be deleted once another user has a position on it; it is archived instead.
- No forks and no follow links. A user who wants other settings builds their own playbook from the same preset.
- A public playbook can have one public screener, owned by the playbook's owner, whose hits are shared and posted to the Discord server. Stage 2 chain fetches are cached across all screeners.
- Open positions are managed under the playbook version they were entered under. This keeps trades in progress safe from edits without a queue.
- `PlaybookChangeProposal` is removed. Every save applies immediately as one version, which stores a diff (`source`, `changes`, `note`). An unreferenced latest version is amended in place. Block updates from deploys apply automatically, batched into one version per playbook per deploy, and orphaned overrides are flagged.
- Self-analytics and model findings become `PlaybookSuggestion` rows shown in the weekly review, built only from the reviewing user's own trades. The user acts on them by hand; there is no apply action.

## Consequences

- One fewer entity and workflow in the MVP. Pinning positions to their entry version gives the same safety the proposal queue gave.
- Lost: the forced weekly cooling-off before structural changes. The weekly review still lists what changed. If impulsive edits become a problem, an optional cooling-off period can be added later.
- Owner edits to a public playbook reach every user immediately for new entries, so owners should note why they changed it.
- Deferred: one-click apply for suggestions, following a public playbook with personal overrides, per-user notification settings.
