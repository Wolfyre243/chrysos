# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository state

This repo is in the design phase: it holds only design docs, no application code yet, so there are no build, lint or test commands. The design lives in:

- `docs/features.md`: what Chrysos does and the principles behind it
- `docs/architecture.md`: stack, deployment, adapters, pipelines, scheduling
- `docs/entities.md`: the data model (ERD source of truth)
- `docs/roadmap.md`: phase scope (Phase 0 MVP, Phase 1, later)
- `docs/diagrams.drawio`: overall design diagram

The docs cross-reference each other. When a change touches behaviour, the data model and the architecture, update all affected docs so they stay consistent (e.g. a new entity in `entities.md` should match the feature in `features.md` and any job, adapter or pipeline in `architecture.md`).

Prototype calculators and indicators are built in the sibling repo `chrysos-lab` (Python, uv, yfinance), kept apart from data fetching and UI before they move into Chrysos.

## What Chrysos is

A personal command center for stocks and options trading for two users. It records trades and never places orders. Everything revolves around playbooks: one strategy definition drives the screener, the pre-trade checklist, management alerts and the weekly review.

## Planned stack

React Router + shadcn/ui frontend, TradingView `lightweight-charts`, FastAPI backend, Postgres, Docker Compose (`postgres`, `api`, `worker`, `web`, `opend`). Market data is moomoo OpenAPI via OpenD long term; Phase 0 uses yfinance as the `MarketDataProvider` while OpenD is evaluated. LLM is OpenAI, notifications are Discord webhooks.

## Core design ideas (read before designing or implementing anything)

- **Adapters for every external dependency**: `MarketDataProvider`, `BrokerProvider` (read-only, interface only), `NewsSource`, `LLMProvider`, `Notifier`. Providers must stay swappable.
- **Analytics registry**: every indicator is a code plugin declaring `id`, `version`, `scope` (stock/option/spread), `requires`, `params`, `output` (scalar/per_strike_series/term_curve). Registering one makes it available on the ticker page, as a screener filter, in entry snapshots and as a rule condition with no other changes. Bump `version` whenever a formula changes; stored values are only compared within one version.
- **One rule engine**: a single JSON rule format (indicator or field reference, `op`, `value`, nestable `all`/`any` groups) and one evaluator serve the screener, soft enforcement, management alerts and user alert rules.
- **Playbook versioning**: templates are hardcoded and versioned in code; user playbooks store overrides on top so template updates still reach unoverridden fields. Every change creates an immutable `PlaybookVersion`. Threshold changes apply immediately; structural changes become `PlaybookChangeProposal`s resolved in the weekly review. Each position records the version it was entered under.
- **Soft enforcement**: rule violations are always recorded; the per-user toggle only controls UI warnings.
- **Record data from day one**: end-of-day chain snapshots (partitioned by date) and entry snapshots are collected before they are needed, for IV rank, backtesting and self-analytics.
- **Zero budget**: respect provider quotas with a token-bucket rate limiter (spread work out, never evade limits); the screener is two-stage (cheap filter on the whole universe, chain fetches only for survivors). LLM spend is capped near USD 5/month with a budget guard; the LLM never reads raw articles, only headline + lead, and summaries are cached and shared across users.
- **Time**: store UTC; market-session logic runs in `America/New_York`; user schedules use each user's timezone.
- **Data ownership**: journals, positions, playbooks, reviews, alerts, screeners and digests are private per user; watchlists are public or private; market data, chain snapshots, news and summaries are shared.
