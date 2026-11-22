---
name: supabase-postgres-best-practices
description: "Postgres best practices maintained by Supabase, for Postgres running anywhere. Load this skill BEFORE writing or changing anything that lives in a Postgres database: creating or altering tables and columns (including choosing column types), schema design, migrations and declarative schema files, RLS policies and the tests that verify them, indexes, triggers, database functions, queues and scheduled jobs (pg_cron, pgmq), vector/semantic search (pgvector), and restoring dumps (pg_restore) or importing data. Also load it when diagnosing slow queries, high CPU, timeouts, EXPLAIN plans, connection exhaustion, locking, bloat, or rows visible to the wrong user or tenant. This is not just a performance guide — schema, migration, security, and SQL authoring tasks need these rules too, even for a one-column change or a single query."
license: MIT
compatibility: opencode
metadata:
  author: supabase
  version: "1.1.1"
  organization: Supabase
  source: https://github.com/supabase/agent-skills
---
# Supabase Postgres Best Practices

Comprehensive performance, schema, migration, and security guide for Postgres, maintained by Supabase. Contains rules across 8 categories, prioritized by impact to guide automated query optimization and schema design.

## When to Apply

Reference these guidelines when:
- Writing SQL queries or designing schemas and migrations
- Implementing indexes or query optimization (`EXPLAIN ANALYZE`)
- Reviewing database performance issues, bloat, or locking
- Configuring connection pooling (Supavisor / PgBouncer) or scaling
- Optimizing for Postgres-specific features (`pgvector`, `pg_cron`, `pgmq`, JSONB, full-text search)
- Working with Row-Level Security (RLS) policies and multi-tenant isolation

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|---|---|---|---|
| 1 | Query Performance | CRITICAL | `query-` |
| 2 | Connection Management | CRITICAL | `conn-` |
| 3 | Security & RLS | CRITICAL | `security-` |
| 4 | Schema Design | HIGH | `schema-` |
| 5 | Concurrency & Locking | MEDIUM-HIGH | `lock-` |
| 6 | Data Access Patterns | MEDIUM | `data-` |
| 7 | Monitoring & Diagnostics | LOW-MEDIUM | `monitor-` |
| 8 | Advanced Features | LOW | `advanced-` |

## Core Non-Negotiable Rules

### 1. Query Performance (`query-`)
- **Index every FK and filter/sort column:** Postgres does NOT auto-index foreign keys. Add indexes on every FK, `WHERE`, `JOIN`, and `ORDER BY` column.
- **Composite index column order:** Equality columns first, range/sort columns last — e.g. `(tenant_id, created_at desc)` for `WHERE tenant_id = $1 ORDER BY created_at DESC`.
- **Partial & covering indexes:** Use `WHERE deleted_at IS NULL` or `INCLUDE (...)` for hot filtered queries to enable Index-Only Scans.
- **Verify with `EXPLAIN (ANALYZE, BUFFERS)`:** Flag unexpected `Seq Scan` on large tables, high buffer reads, or disk sorts.

### 2. Connection Management (`conn-`)
- **Pool serverless connections:** Use Transaction mode pooling (Supavisor / PgBouncer) for serverless/edge runtimes; disable prepared statements when incompatible with transaction pooling.
- **Keep transactions short:** Never hold an open DB transaction across external HTTP calls, file uploads, or user waits.
- **Set `statement_timeout` & `idle_in_transaction_session_timeout`:** Protect the database from runaway queries and leaked sessions.

### 3. Security & RLS (`security-`)
- **Enable RLS on every public-schema table:** Never expose a table to PostgREST/anon/authenticated roles without explicit RLS policies.
- **Index RLS columns:** Every column referenced in an RLS policy (`user_id`, `org_id`, `tenant_id`) MUST be indexed.
- **Wrap auth calls in `(select auth.uid())`:** In RLS policies, use `(select auth.uid()) = user_id` instead of raw `auth.uid() = user_id` so Postgres evaluates it once per statement (initPlan) rather than once per row.
- **Never expose `service_role` keys to clients:** Keep privileged operations in server-side routes/functions with explicit authorization checks.
- **Lock `search_path` on `SECURITY DEFINER` functions:** Always declare `set search_path = ''` and schema-qualify all table references.

### 4. Schema Design (`schema-`)
- **Primary keys:** Prefer `bigint generated always as identity primary key` for sequential IDs, or time-ordered **UUIDv7** (`uuid_generate_v7()`) for distributed IDs to avoid B-tree page fragmentation from random UUIDv4.
- **Idempotent constraints in migrations:** Guard constraint additions with `DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '...') THEN ALTER TABLE ...; END IF; END $$;`.
- **Use native Postgres types:** `timestamptz` (never `timestamp` without time zone), `text` (not `varchar(n)` unless enforcing a domain constraint), `numeric` for money (never `float`/`double`), `jsonb` (never `json`).

### 5. Concurrency & Locking (`lock-`)
- **Non-blocking DDL in production:** Use `CREATE INDEX CONCURRENTLY` (outside a transaction) on large live tables, and `ADD CONSTRAINT ... NOT VALID` followed by `VALIDATE CONSTRAINT`.
- **Consistent lock ordering:** Update rows in deterministic primary-key order to prevent deadlocks; use `FOR UPDATE SKIP LOCKED` for job queues.

### 6. Data Access Patterns (`data-`)
- **Keyset (cursor) pagination over `OFFSET`:** Order by `(created_at desc, id desc)` with a cursor filter instead of deep `OFFSET`.
- **Select only needed columns:** Avoid `SELECT *` on wide tables or JSONB/text blobs.
- **Batch writes & upserts:** Use multi-row `INSERT ... ON CONFLICT DO UPDATE` or `unnest()` instead of per-row loops (eliminate N+1).

### 7. Monitoring & Diagnostics (`monitor-`)
- Inspect `pg_stat_statements`, `pg_stat_user_tables` (dead tuples / autovacuum health), and `pg_stat_user_indexes` (unused indexes) before adding or dropping indexes.

### 8. Advanced Features (`advanced-`)
- **Full-text search:** Generated `tsvector` column + GIN index.
- **Vector search (`pgvector`):** Use HNSW indexes (`m`, `ef_construction`) with appropriate distance operator class (`vector_cosine_ops`, `vector_ip_ops`).
- **Queues & cron:** Use `pgmq` / `pg_cron` cleanly with idempotent handlers and bounded retries.

## Full Upstream References Sync

Run `scripts/sync-skills.ps1` (Windows) or `scripts/sync-skills.sh` (Linux/macOS) to pull all individual `references/*.md` rule files from `https://github.com/supabase/agent-skills`.

## References
- https://www.postgresql.org/docs/current/
- https://supabase.com/docs
- https://supabase.com/docs/guides/auth/row-level-security
