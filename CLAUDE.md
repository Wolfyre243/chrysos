# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository state

Chrysos is mostly design docs plus a freshly scaffolded backend. `server/` holds a FastAPI app with only a healthcheck route; there is no frontend, database, test suite or Docker setup yet. The design is the source of truth for what gets built:

- `docs/README.md`: index of all docs
- `docs/concepts/`: what Chrysos does and how each part works (playbooks, rule engine, screener, journal, news, alerts, review, …), each ending with a "Data model" section listing the entities it owns; start with the "Overview" section of the root `README.md`
- `docs/guides/`: short how-to tutorials for housekeeping tasks
- `docs/references/`: lookup material, including `data-model.md` (table conventions, index of entities and their relationships) and `GLOSSARY.md`
- `docs/architecture.md`: stack, deployment and external dependencies (adapters, providers, news feeds)
- `docs/roadmap.md`: phase scope (Phase 0 MVP, Phase 1, later)
- `docs/diagrams/*.drawio`: design diagrams

The docs cross-reference each other. When a change touches behaviour, the data model and the architecture, update all affected docs so they stay consistent (e.g. a new entity goes in the "Data model" section of the concept page that owns it and in the index and relationships diagram in `references/data-model.md`, and any new adapter or provider should appear in `architecture.md`). Add new docs to `docs/README.md`. Check `roadmap.md` before building something, so Phase 1 or later work isn't pulled into the MVP.

Prototype calculators and indicators are built first in the sibling repo `chrysos-lab` (Python, uv, yfinance), as plain typed modules kept apart from data fetching and UI, before they move into Chrysos as analytics plugins.

## Commands

Backend, run from `server/` (Python via uv):

```bash
uv sync                      # install deps, including the dev group (ruff)
uv run fastapi dev main.py   # dev server with reload
uv run ruff check .          # lint
uv run ruff format .         # format
```

Code style is set in `server/ruff.toml`: 80-column lines, double quotes, 2-space indents.

`server/.claude/skills/fastapi` (and its `.agents/skills` twin) is a symlink into `.venv`, managed by Library Skills, so it is broken until `uv sync` has run. Repair managed skill links with `uvx library-skills --claude` rather than editing them by hand.

## What Chrysos is

A self-hosted personal command center for stocks and options trading, for a small number of users created from a CLI script. It records trades and never places orders. Everything revolves around playbooks: one strategy definition drives the screener, the pre-trade checklist, management alerts and the weekly review.

## Planned stack

- Frontend: TypeScript (pnpm), React Router (framework mode), shadcn/ui, Redux Toolkit with RTK Query, TradingView `lightweight-charts`.
- Backend: Python (uv), FastAPI, SQLModel, Alembic migrations, PostgreSQL.
- Docker Compose services: `postgres`, `api`, `worker`, `web`, `opend`. During development OpenD runs natively on Windows.
- Market data: moomoo OpenAPI via OpenD long term; Phase 0 uses yfinance as the `MarketDataProvider` while OpenD is evaluated. LLM is OpenAI; notifications go to one shared Discord server by webhook, for public alerts only. Private alerts wait for an in-app `Notifier` channel (later).

## Core design ideas (read before designing or implementing anything)

- **Adapters for every external dependency**: `MarketDataProvider`, `BrokerProvider` (read-only, interface only), `NewsSource`, `LLMProvider`, `Notifier`. Providers must stay swappable.
- **Analytics registry**: every indicator is a code plugin declaring `id`, `version`, `scope` (stock/option/spread), `requires`, `params`, `output` (scalar/per_strike_series/term_curve). Registering one makes it available on the ticker page, as a screener filter, in entry snapshots and as a rule condition with no other changes. Bump `version` whenever a formula changes; stored values are only compared within one version.
- **One rule engine**: a single JSON rule format (indicator or field reference, `op`, `value`, nestable `all`/`any` groups) and one evaluator serve the screener, soft enforcement, management alerts and user alert rules.
- **Composable playbooks**: a playbook is one *structure* (what is traded: legs, P&L maths, rolls, e.g. calendar, vertical, iron condor), exactly one *edge* (why: rules, checklist, leg selectors and named parameters, e.g. `forward_factor`, `earnings_iv_crush`) and any number of *add-ons* (cross-cutting rule packs such as liquidity or sizing). Structures, edges, add-ons and presets (named combinations like "FF calendar") are defined and versioned in code. Only the edge picks legs; add-ons only add rules. Playbook rules reference `$legs.<slot>` and `$params.<name>` instead of hardcoded DTEs and thresholds.
- **Playbook versioning**: user playbooks store overrides on top of their blocks, so block updates still reach unoverridden fields. Every save applies immediately as one `PlaybookVersion` recording each block's version and a diff (`source`, `changes`, `note`); an unreferenced latest version is amended in place. Block updates from deploys auto-apply as one `block_update` version per playbook. There are no change proposals: self-analytics and model findings are `PlaybookSuggestion`s the user acts on by hand. Each position records the version it was entered under (and is managed under it until close), plus its structure and edge for grouping. See `docs/adr/0001-*`.
- **Soft enforcement**: rule violations are always recorded; the per-user toggle only controls UI warnings.
- **Record data from day one**: end-of-day chain snapshots (partitioned by date) and entry snapshots are collected before they are needed, for IV rank, backtesting and self-analytics.
- **Zero budget**: respect provider quotas with a token-bucket rate limiter (spread work out, never evade limits); the screener is two-stage (cheap filter on the whole universe, chain fetches only for survivors). LLM spend is capped near USD 5/month with a budget guard; the LLM never reads raw articles, only headline + lead, and summaries are cached and shared across users.
- **Time**: store UTC; market-session logic runs in `America/New_York`; user schedules use each user's timezone.
- **Data ownership**: journals, positions, reviews and suggestions, research files, alert rules, private alerts and digests are private per user; watchlists and playbooks are public or private (a public playbook is edited only by its owner, and trades on it stay private); a screener follows its playbook's visibility, with at most one public screener per public playbook; market data, chain snapshots, news, summaries and public alerts are shared. Never post anything private to the shared Discord server.

## Agent skills

### Issue tracker

Issues live in GitHub Issues for Wolfyre243/chrysos (gh CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary: needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `docs/references/GLOSSARY.md` plus `docs/adr/`. See `docs/agents/domain.md`.
