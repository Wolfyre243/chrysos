# Chrysos entities

Summary of entities and attributes to model in the ERD. Every table also has `created_at` / `updated_at` unless noted. All timestamps are UTC. See [features.md](features.md) for behaviour.

Items marked *(code)* are defined in code, not stored as tables, but are referenced by keys from tables.

---

## Users and access

### User
- `id`
- `username` (unique)
- `password_hash`
- `display_name`
- `timezone`
- `enforcement_enabled` (bool)
- `discord_webhook_url`
- `review_day` (day of week)
- `review_time` (local time)
- `is_active`

### AuthSession
- `id`
- `user_id` → User
- `token_hash`
- `expires_at`
- `last_seen_at`

---

## Market data

### Ticker
Cache populated on demand, not a maintained master list.
- `symbol` (PK)
- `name`
- `asset_type` (stock, etf, index)
- `exchange`
- `is_optionable`
- `in_universe` (bool, screener universe membership)
- `universe_source` (sp500, liquid_optionable)
- `last_refreshed_at`

### PriceBar
- `symbol` → Ticker
- `interval` (1d, 1h, …)
- `ts`
- `open`, `high`, `low`, `close`, `volume`

### EarningsEvent
- `id`
- `symbol` → Ticker
- `date`
- `timing` (before_open, after_close, unknown)
- `is_confirmed`
- `source`

### EarningsExpectation
What the market expects ahead of an earnings event. Captured more than once as the date approaches.
- `id`
- `earnings_event_id` → EarningsEvent
- `captured_at`
- `implied_move_pct` (options-implied move to the first expiry after the report)
- `chain_snapshot_id` → ChainSnapshot (nullable)
- `eps_estimate` (consensus, nullable)
- `revenue_estimate` (consensus, nullable)
- `source`

### FundamentalsSnapshot
Fundamentals for one reporting period, used by fundamentals indicators such as P/E and the health score.
- `id`
- `symbol` → Ticker
- `period_end`
- `period_type` (quarter, annual, ttm)
- `revenue`
- `revenue_growth_yoy`
- `gross_margin`, `operating_margin`, `net_margin`
- `eps`
- `pe_ratio` (at capture time)
- `other` (JSONB, further metrics the provider returns)
- `source`
- `captured_at`

### ChainSnapshot
One capture of an option chain at a point in time.
- `id`
- `symbol` → Ticker
- `captured_at`
- `kind` (eod, screener, on_demand)
- `spot_price`
- `provider`
- `is_partial` (bool, true for pruned screener fetches)

### OptionQuote
Row within a chain snapshot. Partition by date.
- `snapshot_id` → ChainSnapshot
- `expiry`
- `strike`
- `right` (call, put)
- `contract_symbol` (OCC)
- `bid`, `ask`, `last`
- `volume`
- `open_interest`
- `iv`
- `delta`, `gamma`, `theta`, `vega`

### ProviderCallLog
For quota visibility.
- `id`
- `provider`
- `endpoint`
- `called_at`
- `status`
- `latency_ms`

---

## Analytics

### Indicator *(code)*
- `id`
- `name`
- `version`
- `scope` (stock, option, spread)
- `requires` (chain, price_history, fundamentals)
- `params_schema`
- `output_type` (scalar, per_strike_series, term_curve)

### IndicatorResult
Cached computed values. Shared across users.
- `id`
- `symbol` → Ticker
- `indicator_id`
- `indicator_version`
- `params` (JSONB)
- `params_hash`
- `as_of`
- `snapshot_id` → ChainSnapshot (nullable)
- `fundamentals_snapshot_id` → FundamentalsSnapshot (nullable, fundamentals indicators only)
- `value` (JSONB)

P/E and the health score are indicators with `scope` stock and `requires` fundamentals, so they have no tables of their own. The health score's `value` holds `score` (0 to 100), `grade` (A to F, derived from `score`) and `components` (sub-score per factor, such as valuation, margins, revenue).

---

## Watchlists

### Watchlist
- `id`
- `owner_id` → User
- `name`
- `description`
- `visibility` (public, private)

### WatchlistItem
- `watchlist_id` → Watchlist
- `symbol` → Ticker
- `sort_order`
- `note`
- `added_at`

---

## Research

### TickerResearch
A user's research file on one ticker. Private to that user; unique on (`user_id`, `symbol`).
- `id`
- `user_id` → User
- `symbol` → Ticker
- `business_summary` (how the company makes money, its segments and competitors)
- `last_reviewed_at`

### ResearchNote
One entry in a research file.
- `id`
- `research_id` → TickerResearch
- `kind` (observation, outside_factor)
- `title`
- `body`
- `impact` (positive, negative, mixed; outside factors only, nullable)
- `is_active` (false once the factor no longer applies)
- `observed_at`

---

## Playbooks and rules

### PlaybookTemplate *(code)*
- `key` (calendar, vertical, …)
- `version`
- `name`
- `strategy_type`
- `leg_template`
- default entry rules, checklist, management rules, sizing rules

### Playbook
A user's copy of a template.
- `id`
- `user_id` → User
- `template_key`
- `name`
- `strategy_type`
- `current_version_id` → PlaybookVersion
- `is_active`

### PlaybookVersion
Immutable snapshot of the effective rules at a point in time.
- `id`
- `playbook_id` → Playbook
- `version_number`
- `template_version`
- `overrides` (JSONB, user changes on top of the template)
- `entry_rules` (JSONB, resolved)
- `checklist` (JSONB, resolved)
- `management_rules` (JSONB, resolved)
- `sizing_rules` (JSONB, resolved)
- `leg_template` (JSONB)
- `change_type` (initial, threshold, structural)
- `created_from_review_id` → WeeklyReview (nullable)

### Rule *(value object, stored as JSONB)*
Shared format used in PlaybookVersion and AlertRule.
- `id` (stable within its parent)
- `kind` (entry, management, sizing, alert)
- `condition` (indicator or field reference, params, op, value; or `all` / `any` group)
- `description`
- `severity` (info, warning, critical)

### ChecklistItem *(value object, stored as JSONB)*
- `id`
- `prompt`
- `answer_type` (text, bool, number)
- `required`

### PlaybookChangeProposal
Structural changes queued for the weekly review.
- `id`
- `playbook_id` → Playbook
- `user_id` → User
- `proposed_change` (JSONB)
- `reason`
- `source` (user, self_analytics, model)
- `status` (pending, applied, rejected)
- `resolved_in_review_id` → WeeklyReview (nullable)
- `resolved_at`

---

## Journal

The trader's plan and thinking around a position.

### TradePlan
- `id`
- `position_id` → Position (one-to-one)
- `thesis` (what the trader expects to happen)
- `entry_reason` (why enter now)
- `checklist_answers` (JSONB)
- `planned_size`
- `max_loss`
- `profit_target`
- `planned_exit`
- `is_complete` (bool)

### JournalNote
- `id`
- `position_id` → Position
- `user_id` → User
- `body`

### TradeFeeling
How the trader felt at a point in the trade. Kept apart from journal notes so self-analytics can compare feelings with results.
- `id`
- `position_id` → Position
- `execution_id` → Execution (nullable; null when recorded while planning or holding)
- `body`
- `recorded_at`

---

## Trade log

The record of what happened in each trade.

### Position
One trade idea from plan to close. Created with the plan, in status `planned`.
- `id`
- `user_id` → User
- `playbook_id` → Playbook
- `playbook_version_id` → PlaybookVersion
- `symbol` → Ticker
- `strategy_type`
- `status` (planned, open, closed, cancelled)
- `is_planned` (bool, plan existed before first execution)
- `opened_at`
- `closed_at`
- `realized_pnl`
- `fees_total`
- `screener_result_id` → ScreenerResult (nullable, origin)
- `tags`

### Execution
- `id`
- `position_id` → Position
- `type` (open, adjust, roll, close)
- `executed_at`
- `net_amount` (debit negative, credit positive)
- `fees`
- `notes`

### ExecutionLeg
- `id`
- `execution_id` → Execution
- `instrument_type` (stock, option)
- `symbol` → Ticker
- `expiry` (options only)
- `strike` (options only)
- `right` (options only)
- `side` (buy, sell)
- `position_effect` (open, close)
- `quantity`
- `price`
- `multiplier`

### EntrySnapshot
Indicator values captured at an execution.
- `id`
- `position_id` → Position
- `execution_id` → Execution
- `captured_at`
- `spot_price`
- `values` (JSONB: indicator id → version, params, value)
- `chain_snapshot_id` → ChainSnapshot (nullable)

### RuleViolation
Always recorded, regardless of the enforcement toggle.
- `id`
- `position_id` → Position
- `execution_id` → Execution (nullable)
- `playbook_version_id` → PlaybookVersion
- `rule_ref` (rule or checklist item id)
- `violation_type` (no_plan, incomplete_checklist, entry_rule_failed, off_plan_exit, sizing_breach)
- `expected` (JSONB)
- `actual` (JSONB)
- `detected_at`
- `acknowledged` (bool)

---

## Weekly review

### WeeklyReview
- `id`
- `user_id` → User
- `week_start`
- `week_end`
- `status` (draft, submitted)
- `submitted_at`
- `stats` (JSONB, auto-generated numbers by playbook)
- `adherence_score`
- `went_well`
- `biggest_mistake`
- `do_differently`
- `commitment` (focus for next week)
- `previous_commitment_kept` (bool)
- `llm_summary` (nullable)

### TradeGrade
- `id`
- `review_id` → WeeklyReview
- `position_id` → Position
- `process_grade` (A–F)
- `outcome` (win, loss, scratch)
- `quadrant` (repeat, variance, dangerous, lesson)
- `comment`

---

## Screeners

### Screener
- `id`
- `user_id` → User
- `playbook_id` → Playbook
- `name`
- `stage1_filters` (JSONB)
- `schedule`
- `is_enabled`

### ScreenerRun
- `id`
- `screener_id` → Screener
- `playbook_version_id` → PlaybookVersion
- `started_at`
- `finished_at`
- `status` (running, succeeded, failed)
- `universe_count`
- `stage1_count`
- `stage2_count`
- `error`

### ScreenerResult
- `id`
- `run_id` → ScreenerRun
- `symbol` → Ticker
- `legs` (JSONB, proposed structure)
- `metrics` (JSONB, indicator values)
- `rank`

---

## News and digests

### NewsSource
Shared across users, managed from the UI.
- `id`
- `name`
- `type` (rss, edgar, html)
- `url`
- `poll_interval_seconds`
- `priority`
- `tags`
- `parser_config` (JSONB)
- `is_enabled`
- `last_polled_at`
- `last_error`

### NewsArticle
- `id`
- `source_id` → NewsSource
- `url`
- `dedupe_hash`
- `title`
- `lead`
- `published_at`
- `fetched_at`
- `summary` (LLM, cached, nullable)
- `importance` (low, normal, high)
- `is_relevant` (bool)

### ArticleTicker
- `article_id` → NewsArticle
- `symbol` → Ticker
- `match_method` (cashtag, dictionary)

### Digest
- `id`
- `user_id` → User
- `session` (pre_market, regular, post_market, overnight)
- `session_date` (ET)
- `content`
- `llm_usage_id` → LLMUsage
- `delivered_at`

### DigestArticle
- `digest_id` → Digest
- `article_id` → NewsArticle

---

## Alerts and notifications

### AlertRule
- `id`
- `user_id` → User
- `name`
- `condition` (JSONB, shared rule format)
- `scope_type` (ticker, watchlist, positions, all)
- `scope_ref` (symbol or watchlist id, nullable)
- `cooldown_seconds`
- `is_enabled`
- `last_triggered_at`

### AlertEvent
- `id`
- `user_id` → User
- `kind` (news, alert_rule, management_rule, screener_hit, review_reminder)
- `alert_rule_id` → AlertRule (nullable)
- `position_id` → Position (nullable)
- `article_id` → NewsArticle (nullable)
- `screener_run_id` → ScreenerRun (nullable; one batched alert per run)
- `payload` (JSONB)
- `triggered_at`

### NotificationDelivery
- `id`
- `user_id` → User
- `channel` (discord, in_app)
- `alert_event_id` → AlertEvent (nullable)
- `digest_id` → Digest (nullable)
- `status` (pending, sent, failed)
- `sent_at`
- `error`

---

## System

### LLMUsage
For the monthly budget guard.
- `id`
- `purpose` (article_summary, digest, review_summary)
- `provider`
- `model`
- `tokens_in`
- `tokens_out`
- `cost_usd`
- `called_at`

### JobRun
- `id`
- `job_name` (eod_snapshot, screener, news_poll, digest, management_check, review_reminder, earnings_capture, fundamentals_refresh)
- `started_at`
- `finished_at`
- `status`
- `error`

### AppSetting
Global key/value settings.
- `key`
- `value` (JSONB)

Example keys: `llm_monthly_budget_usd`, `universe_refresh_schedule`.
