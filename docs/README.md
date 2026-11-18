# Chrysos docs

Design documentation for Chrysos. Start with the [overview](../README.md#overview) in the root README.

## Concepts

How Chrysos works and why.

- [Users and access](concepts/users-and-access.md): CLI-created users, sessions, what is private, public or shared
- [Playbooks](concepts/playbooks.md): structures, edges, add-ons, presets, parameters, versioning and public playbooks
- [Rule engine](concepts/rule-engine.md): fields, indicators, operands, conditions, rules and rule sets, and how features read results
- [Market data](concepts/market-data.md): caching, rate limiting, chain snapshots and watchlists
- [Analytics](concepts/analytics.md): indicator registry, fundamentals, health score, research files, earnings analysis, ticker page
- [Screener](concepts/screener.md): the two-stage nightly pipeline and custom rules
- [Journal and trade log](concepts/journal-and-trade-log.md): notes (theses and journal notes, with ticker mentions), plans, feelings, positions, entry snapshots, soft enforcement
- [News and digests](concepts/news-and-digests.md): sources, ingestion, session digests and the LLM budget
- [Alerts](concepts/alerts.md): alerts, triggers and cooldowns, alert events and delivery
- [Weekly review](concepts/weekly-review.md): process grading, self-analytics and later models
- [Scheduling and time](concepts/scheduling-and-time.md): timezones and scheduled jobs

## Guides

Short how-to tutorials for housekeeping tasks. None yet.

## References

Lookup material.

- [Glossary](references/GLOSSARY.md): domain terms
- [Data model](references/data-model.md): table conventions, index of entities and cross-page relationships (each concept page holds its own entities)

## Decisions

Architecture decision records: why the design is the way it is.

- [0001: Public playbooks, without change proposals or forks](adr/0001-public-playbooks-without-change-proposals.md)
- [0002: Rules have no severity; users disable them instead](adr/0002-rules-without-severity.md)
- [0003: Rules don't pin indicator versions](adr/0003-rules-dont-pin-indicator-versions.md)
- [0004: Rules are written and stored as JSON only](adr/0004-rules-are-json-only.md)
- [0005: Triggers fire when they become true, with a cooldown](adr/0005-triggers-fire-on-becoming-true.md)
- [0006: Per-leg checks use summary fields on the trade](adr/0006-per-leg-checks-use-trade-summary-fields.md)
- [0007: Rules don't do arithmetic](adr/0007-rules-dont-do-arithmetic.md)

## Other

- [Architecture](architecture.md): stack, deployment and external dependencies
- [Roadmap](roadmap.md): phase scope (Phase 0 MVP, Phase 1, future plans)
- [Diagrams](diagrams/): draw.io design diagrams
- [Agents](agents/): conventions for coding agents (issue tracker, triage labels, domain docs)
