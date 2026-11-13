# Chrysos

Chrysos is a command center built for traders, specifically in the stocks and options world. 

It's key philosophy is to abide by playbooks and historical patterns. Hence, every trade recorded, every screener set up, are all based off the rules inside a strategy's playbook.

See [docs/README.md](docs/README.md) for the design documentation.

## Overview

Chrysos is a personal trading platform for stocks and options. Its main job is to make every trade follow a written playbook and get reviewed afterwards, so trading stays consistent and rule driven. The rest of the system feeds that loop by finding candidates, computing numbers brokers don't show, and watching open positions. Chrysos records trades; it never places orders.

It is meant to replace paid tools such as Unusual Whales at close to zero cost. It also knows the user's own trades and results, which those tools can't, and that history is used to tune the rules.

### Principles

1. Playbooks drive everything. One strategy definition feeds the screener, the trade checklist, management alerts and the weekly review.
2. One rule engine. Screener filters, entry checks, management rules and alerts share the same rule format and evaluator.
3. Process over outcome. Reviews grade how closely a trade followed its plan, separately from whether it made money.
4. Record data from day one. Option chain history and entry snapshots can't be bought cheaply later, so Chrysos collects them before it needs them.
5. Zero budget first. Use free data and keep LLM spend near USD 5 a month. Pay for more only where a need is proven.

### How the parts fit

- [Playbooks](docs/concepts/playbooks.md) define each strategy as rules, evaluated by the [rule engine](docs/concepts/rule-engine.md).
- [Market data](docs/concepts/market-data.md) and [analytics](docs/concepts/analytics.md) supply the numbers those rules read.
- The [screener](docs/concepts/screener.md) finds candidates that match a playbook.
- The [journal and trade log](docs/concepts/journal-and-trade-log.md) record the plan and what actually happened in each trade.
- [News and digests](docs/concepts/news-and-digests.md) and [alerts](docs/concepts/alerts.md) watch for things that need the user's attention.
- The [weekly review](docs/concepts/weekly-review.md) grades each trade's process and turns findings into suggestions for the user to apply to their playbooks.
- [Users and access](docs/concepts/users-and-access.md) and [scheduling and time](docs/concepts/scheduling-and-time.md) cover the cross-cutting rules.

See [architecture.md](./docs/architecture.md) for the stack, deployment and external dependencies, and [data-model.md](./docs/references/data-model.md) for the index of entities (each concept page holds its own).