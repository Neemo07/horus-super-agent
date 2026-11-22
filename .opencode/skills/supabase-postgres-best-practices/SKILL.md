---
name: supabase-postgres-best-practices
description: Postgres performance optimization and best practices from Supabase. Use when writing, reviewing, or optimizing SQL queries, schema design, indexes, connection management, row level security (RLS) policies, locking, or any Supabase/Postgres database work.
license: MIT
compatibility: opencode
metadata:
  source: supabase/agent-skills (supabase-postgres-best-practices)
  edition: condensed-offline
---
# Supabase Postgres Best Practices

> Provenance: offline condensed edition organised by the upstream priority categories; wording is re-authored. Run `python scripts/sync_upstream.py --only supabase-postgres-best-practices` to replace this folder with the verbatim upstream skill and its reference files.

Apply by priority. Verify with evidence (`EXPLAIN (ANALYZE, BUFFERS)`, advisors, query counts) rather than intuition. Schema changes go through migration files, never dashboard-only edits.

## 1. Query performance - CRITICAL
- Index every foreign key (Postgres does not) and every column in frequent `WHERE`, `JOIN`, `ORDER BY`.
- Composite index order = equality columns first, then range/sort: `(user_id, created_at desc)` serves `where user_id = ? order by created_at desc`.
- Use partial indexes for hot subsets (`where status = 'pending'`) and covering indexes (`include (...)`) for index-only scans.
- Pick the index type for the operator: B-tree default, GIN for `jsonb`/arrays/full-text, BRIN for huge append-only time series, GiST for ranges/geometry.
- Avoid `select *` on wide rows; avoid functions on indexed columns in predicates (`lower(email)` needs an expression index); avoid leading-wildcard `LIKE`.
- Kill N+1: one JOIN / nested select / `where id = any($1)` batch instead of a query per row.
- Read plans: `Seq Scan` on a large table, `Rows Removed by Filter` in the millions, or a large estimate-vs-actual gap means a missing index or stale stats (`analyze`).

## 2. Connection management - CRITICAL
- Use a pooler for serverless/edge and many short-lived clients (Supavisor/PgBouncer, transaction mode); keep app pool size small (roughly CPU cores x 2-4 per instance) and total below `max_connections`.
- In transaction pooling, do not rely on session state (session-level `SET`, advisory session locks, `LISTEN`, unnamed-prepared-statement assumptions).
- Always release connections; set statement and idle-in-transaction timeouts so a stuck client cannot hold locks.

## 3. Security and RLS - CRITICAL
- Enable RLS on every table in an exposed schema; no policy means no access, which is the safe default.
- Write policies per operation and role (`select`, `insert`, `update`, `delete`; `to authenticated`); `update` needs both `using` and `with check`.
- Wrap auth helpers so they evaluate once per statement: `(select auth.uid()) = user_id`, not `auth.uid() = user_id`.
- Index every column a policy reads (`user_id`, `org_id`, membership joins); move heavy membership checks into a `security definer` function in a non-exposed schema with a fixed `search_path`.
- Never ship the `service_role` key to a browser/mobile client; never trust `user_metadata` for authorisation (use `app_metadata` or a roles table).
- Views run with the owner's rights; use `security_invoker = true` (Postgres 15+) when RLS must apply.

## 4. Schema design - HIGH
- Primary key on every table; prefer `bigint generated always as identity` or `uuid` (time-ordered when insert locality matters).
- Match FK and referenced column types exactly; define `on delete` behaviour deliberately; add `not null`, `check`, and `unique` constraints in the database, not only in app code.
- Use `timestamptz`, `numeric` for money, `text` over `varchar(n)` unless a limit is a real rule; `jsonb` for genuinely sparse data, columns for anything filtered/joined.
- Normalise by default; denormalise only with a measured reason and a single writer.
- Partition very large time-series tables by range once they approach hundreds of millions of rows.

## 5. Concurrency and locking - MEDIUM-HIGH
- Keep transactions short; no network calls or user waits inside a transaction.
- Lock rows in a consistent order to avoid deadlocks; use `select ... for update skip locked` for job queues.
- Prefer atomic statements (`insert ... on conflict do update`, `update ... set n = n + 1`) over read-modify-write.
- Migrations: `create index concurrently` on live tables (outside a transaction); add columns nullable or with a constant default, backfill in batches, then add constraints (`not valid` then `validate constraint`).

## 6. Data access patterns - MEDIUM
- Batch inserts/updates (multi-row `values`, `copy`, `unnest`) instead of row-by-row loops.
- Keyset pagination for large/infinite lists (`where (created_at, id) < ($1, $2) order by created_at desc, id desc limit 20`); offset only for small admin tables; avoid exact `count(*)` per page view on big tables.
- Cache rarely-changing reads at the app/CDN layer, never user-specific data in shared caches.

## 7. Monitoring and diagnostics - LOW-MEDIUM
- Enable `pg_stat_statements`; sort by total time, then by mean time x calls.
- Check `pg_stat_user_tables` for seq-scan-heavy tables and dead tuples; confirm autovacuum keeps up; run `analyze` after bulk loads.
- Use Supabase Performance/Security advisors; treat unindexed-FK and RLS-initplan warnings as defects.

## 8. Advanced features - LOW
- Full-text search: `tsvector` generated column + GIN index; trigram (`pg_trgm`) GIN for fuzzy/`ilike`.
- `jsonb_path_ops` GIN for containment queries; materialised views (with `refresh ... concurrently`) for heavy aggregates.

## Review output
`# | Category | Finding | file:line (migration/query) | Impact | Fix (SQL)`. Ask before schema changes beyond additive indexes or running anything against production.

## Pairing
Sizing and caching trade-offs: `speed-engineer`. React/Next data-fetching structure: `vercel-react-best-practices`.
