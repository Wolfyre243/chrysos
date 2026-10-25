# Chrysos features

Chrysos is a personal trading platform for stocks and options. Its main job is to make every trade follow a written playbook and get reviewed afterwards, so trading stays consistent and rule driven. The rest of the system feeds that loop by finding candidates, computing numbers brokers don't show, and watching open positions. Chrysos records trades; it never places orders.

It is meant to replace paid tools such as Unusual Whales at close to zero cost. It also knows the user's own trades and results, which those tools can't, and that history is used to tune the rules.

See [architecture.md](architecture.md) for the stack, providers and scheduling, and [entities.md](entities.md) for the data model.

## Principles

1. Playbooks drive everything. One strategy definition feeds the screener, the trade checklist, management alerts and the weekly review.
2. One rule engine. Screener filters, entry checks, management rules and alerts share the same rule format and evaluator.
3. Process over outcome. Reviews grade how closely a trade followed its plan, separately from whether it made money.
4. Record data from day one. Option chain history and entry snapshots can't be bought cheaply later, so Chrysos collects them before it needs them.
5. Zero budget first. Use free data and keep LLM spend near USD 5 a month. Pay for more only where a need is proven.

## Playbooks

A playbook is one strategy written as rules. Each part is read by a different layer:

- Entry criteria: conditions a trade must meet, such as FF > 0.2 or no earnings between expirations. The screener uses them as filters, and each new trade is checked against them.
- Pre-trade checklist: questions to answer before entering, such as thesis, max loss and planned exit.
- Management rules: when to take profit or close, such as +25% or 7 DTE before front expiry. The alerts engine checks open positions against them.
- Sizing rules: limits such as the maximum share of the account per trade. Every entry is checked against them, and sizing over time is charted to show trading habits.
- Leg template: the trade's structure, used to pre-fill entry.

Each user starts from a built-in template (calendar, vertical) and overrides thresholds; template updates still reach fields the user hasn't changed. Every change creates a new version, and each trade records the version it was entered under. Threshold tweaks apply immediately. Structural changes, such as adding or removing a rule, wait for the weekly review so rules don't get rewritten in the middle of a trade.

## Data

Collects market data and keeps the history that is hard to get later.

- Market data: quotes, option chains with IV and greeks, price history and earnings dates, cached locally.
- Chain snapshots: end-of-day option chains for every watchlist ticker and open position, saved from day one. Free historical options data is scarce, so Chrysos builds its own. This history later supports lookback indicators such as IV rank, and backtesting of playbook thresholds.
- News: sources managed from the UI (RSS, SEC EDGAR, scrapers). Articles are deduplicated and tagged with tickers without an LLM. Each relevant article is summarised once by the LLM, and that summary is shared across users.
- Watchlists: public or private ticker groups. They decide which tickers get chain snapshots, GEX and news coverage, and are separate from the screener universe.

## Analytics

Numbers and research that brokerage platforms don't provide.

- Indicator registry: every calculator is a plugin. Once registered, it appears on the ticker page, as a screener filter, in entry snapshots and as a rule condition, with no other changes. Plugins are versioned so values are only compared within the same formula.
- Starter indicators: forward factor, IV term structure, expected move, and gamma exposure (per-strike GEX, call and put walls, gamma flip). GEX runs end of day because open interest only updates daily.
- Fundamentals indicators: P/E and other fundamentals metrics are registry indicators like the rest, so they can be screener filters and rule conditions. They are added once a fundamentals source is confirmed.
- Health score: an in-house grade of a stock's overall health and profitability, built from fundamentals such as P/E, margins and revenue. It is a registry indicator too, so a playbook can filter on it.
- Research notes: a structured record of observations about a stock, how its business works, and outside factors that could help or hurt it.
- Earnings analysis: gathers what the market expects from a company's upcoming earnings, so trades around the report can be weighed against what is already priced in.
- Ticker page: everything about one ticker in one view. The price chart overlays news, the user's own entries and exits, and GEX levels. Below it sit the analytics panels, research notes, recent news, and open positions with their rule status.

## Screener

Finds trade candidates that match a playbook.

- Each screener runs one playbook's entry criteria every night across the S&P 500 plus liquid optionable names. The first two cover calendar spreads and vertical spreads.
- It screens in two stages to stay within rate limits. A cheap pass on price, volume and earnings dates cuts about 600 tickers to 50 to 100, and only those get chain fetches and the full rule check.
- A hit becomes a trade plan in one click, pre-filled with the playbook, legs and the indicator values at screening time.

## Journal

Every trade gets a written plan before entry, and the trader's thinking is recorded as the trade plays out.

- Plan: choose a playbook, state why you're entering, answer the checklist, and set max loss, target and planned exit.
- Notes: free-form notes on a trade at any point, from planning to close.
- Feelings: the journal records how the trader felt about the trade, so emotional state can be compared with results later.

## Trade log

The record of what actually happened in each trade. Reviews, alerts and models read from it.

- Positions: one position is one trade idea from plan to close. It holds executions (open, adjust, roll, close), and P&L is tracked across all of them, so a rolled calendar stays one position. Covers stocks and options, single legs and spreads.
- Fast entry: picking a playbook pre-fills the legs, and entering a strike fetches the current mark for the user to correct to the real fill. Fills are entered by hand for now, so entry has to be quick or it won't be done consistently.
- Entry snapshot: when a trade opens, Chrysos saves every relevant indicator value. Self-analytics depends on these.
- Soft enforcement: Chrysos always records violations (no plan, incomplete checklist, failed entry criteria, off-plan exit, sizing breach). A per-user toggle only controls whether the UI warns about them, so review statistics stay complete either way. Trades opened without a plan are flagged as unplanned.

## Alerts

One alert system for everything that needs the user's attention.

- Alert types: high-importance news on held or watched tickers (8-K filings, halts, earnings, keyword matches), management rule triggers, screener hits, reminders such as closing a position, and user-defined rules. All use the shared rule format, and each rule has a cooldown.
- Screener hits: each nightly screener run sends one alert listing its top hits, rather than one alert per hit.
- Session digests: four a day at the start of each US session (pre-market, regular, post-market, overnight). Each covers the user's relevant news, notable price moves, and open positions against their management rules. The rules produce the suggestions; the LLM only writes the summary around them, within a monthly budget cap.
- Delivery: a Discord webhook per user, with in-app notifications later.

## Review and self-analytics

Learning from the user's own trades.

- Weekly review: scheduled, mostly generated, and about 15 minutes long. It shows results and rule adherence by playbook, then the user grades each closed trade's process from A to F. Grades are crossed with outcome: a good process with a loss counts as variance, and a bad process with a win is flagged hardest. The review also checks open positions against their plans, takes a short reflection, applies or rejects pending playbook changes, and ends with one commitment that the next review checks. Reviews lock on submission, completed reviews build a streak, and monthly and quarterly views roll up from them.
- Self-analytics: once enough trades exist, outcomes are compared against entry conditions. For example, do calendar spreads entered with FF > 0.3 do better than those entered with FF > 0.2? This works because every trade carries its entry snapshot and playbook version. Sizing history is charted here too.

## Models (later)

Once enough data exists, two kinds of model can build on it:

- On the user's trades: an ML model or LLM that reads the trade log (entry snapshots, playbook versions and outcomes) and finds which entry conditions go with good results, extending self-analytics.
- On market history: a custom model trained on stored chain snapshots and backtests that recognises past patterns when they show up again.

Findings reach the user as playbook change proposals in the weekly review, where they are applied or rejected like any other proposal.

## Later

- SEC filing parser that reads specific filing sections into structured data
- Automatic fill import from moomoo, with unplanned-trade detection
- Parsing pasted moomoo order confirmations for faster entry
- Sharing watchlists with specific users
- More indicators: IV rank and percentile once history exists, skew
