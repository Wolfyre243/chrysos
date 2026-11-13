# Chrysos docs

Design documentation for Chrysos. Start with the [overview](../README.md#overview) in the root README.

## Concepts

How Chrysos works and why.

- [Users and access](concepts/users-and-access.md): CLI-created users, sessions, what is private, public or shared
- [Playbooks](concepts/playbooks.md): structures, edges, add-ons, presets, parameters, versioning and public playbooks
- [Rule engine](concepts/rule-engine.md): the shared rule format and its `$legs` / `$params` references
- [Market data](concepts/market-data.md): caching, rate limiting, chain snapshots and watchlists
- [Analytics](concepts/analytics.md): indicator registry, fundamentals, health score, research notes, earnings analysis, ticker page
- [Screener](concepts/screener.md): the two-stage nightly pipeline
- [Journal and trade log](concepts/journal-and-trade-log.md): plans, notes, feelings, positions, entry snapshots, soft enforcement
- [News and digests](concepts/news-and-digests.md): sources, ingestion, session digests and the LLM budget
- [Alerts](concepts/alerts.md): alert types, cooldowns and delivery
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

## Other

- [Architecture](architecture.md): stack, deployment and external dependencies
- [Roadmap](roadmap.md): phase scope (Phase 0 MVP, Phase 1, future plans)
- [Diagrams](diagrams/): draw.io design diagrams
- [Agents](agents/): conventions for coding agents (issue tracker, triage labels, domain docs)
