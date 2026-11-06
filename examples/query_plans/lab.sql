\set ON_ERROR_STOP on
SET statement_timeout = '60s';
SET lock_timeout = '3s';
SET max_parallel_workers_per_gather = 0;
SET jit = off;
CREATE TEMP TABLE kb_plan_orders (
    id integer PRIMARY KEY,
    customer_id integer NOT NULL,
    created_at timestamptz NOT NULL,
    payload text NOT NULL
);
INSERT INTO kb_plan_orders
SELECT g,
       CASE WHEN g <= 160000 THEN 1 ELSE (g % 1000) + 2 END,
       TIMESTAMPTZ '2026-10-01 00:00:00+00' + g * INTERVAL '1 second',
       repeat('payload-', 25)
FROM generate_series(1, 200000) AS g;
CREATE TEMP TABLE kb_plan_results (name text PRIMARY KEY, plan jsonb);
CREATE TEMP TABLE kb_plan_digests (stage text PRIMARY KEY, ids jsonb);
CREATE FUNCTION pg_temp.record_plan(label text, query text) RETURNS void LANGUAGE plpgsql AS $$
DECLARE captured jsonb;
BEGIN
    EXECUTE 'EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) ' || query INTO captured;
    INSERT INTO kb_plan_results VALUES (label, captured);
END $$;
CREATE FUNCTION pg_temp.record_ids(label text) RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO kb_plan_digests
    SELECT label, jsonb_agg(id ORDER BY created_at DESC, id DESC)
    FROM (SELECT id, created_at FROM kb_plan_orders
          WHERE customer_id = 42 AND created_at >= TIMESTAMPTZ '2026-10-01 00:00:00+00'
          ORDER BY created_at DESC, id DESC LIMIT 20) AS picked;
END $$;
VACUUM (ANALYZE) kb_plan_orders;
SELECT pg_temp.record_plan('before_index', $q$
    SELECT id, created_at FROM kb_plan_orders
    WHERE customer_id = 42 AND created_at >= TIMESTAMPTZ '2026-10-01 00:00:00+00'
    ORDER BY created_at DESC, id DESC LIMIT 20$q$);
SELECT pg_temp.record_ids('before_index');
CREATE INDEX kb_orders_customer_created_id ON kb_plan_orders (customer_id, created_at, id);
VACUUM (ANALYZE) kb_plan_orders;
SELECT pg_temp.record_plan('after_index', $q$
    SELECT id, created_at FROM kb_plan_orders
    WHERE customer_id = 42 AND created_at >= TIMESTAMPTZ '2026-10-01 00:00:00+00'
    ORDER BY created_at DESC, id DESC LIMIT 20$q$);
SELECT pg_temp.record_ids('after_index');
SELECT pg_temp.record_plan('broad_filter_with_index', $q$
    SELECT sum(length(payload)) FROM kb_plan_orders WHERE customer_id = 1$q$);
UPDATE kb_plan_orders SET payload = payload || 'x' WHERE customer_id = 42;
SELECT pg_temp.record_plan('after_heap_update', $q$
    SELECT id, created_at FROM kb_plan_orders
    WHERE customer_id = 42 AND created_at >= TIMESTAMPTZ '2026-10-01 00:00:00+00'
    ORDER BY created_at DESC, id DESC LIMIT 20$q$);
SELECT pg_temp.record_ids('after_heap_update');
VACUUM (VERBOSE, ANALYZE) kb_plan_orders;
SELECT pg_temp.record_plan('after_default_vacuum', $q$
    SELECT id, created_at FROM kb_plan_orders
    WHERE customer_id = 42 AND created_at >= TIMESTAMPTZ '2026-10-01 00:00:00+00'
    ORDER BY created_at DESC, id DESC LIMIT 20$q$);
SELECT pg_temp.record_ids('after_default_vacuum');
VACUUM (VERBOSE, ANALYZE, INDEX_CLEANUP ON) kb_plan_orders;
SELECT pg_temp.record_plan('after_cleanup_vacuum', $q$
    SELECT id, created_at FROM kb_plan_orders
    WHERE customer_id = 42 AND created_at >= TIMESTAMPTZ '2026-10-01 00:00:00+00'
    ORDER BY created_at DESC, id DESC LIMIT 20$q$);
SELECT pg_temp.record_ids('after_cleanup_vacuum');
\echo KB_PLAN_REPORT_BEGIN
SELECT jsonb_build_object(
    'server_version', version(),
    'server_version_num', current_setting('server_version_num')::integer,
    'settings', jsonb_build_object(
        'random_page_cost', current_setting('random_page_cost'),
        'seq_page_cost', current_setting('seq_page_cost'),
        'enable_seqscan', current_setting('enable_seqscan'),
        'enable_indexscan', current_setting('enable_indexscan'),
        'enable_indexonlyscan', current_setting('enable_indexonlyscan'),
        'max_parallel_workers_per_gather', current_setting('max_parallel_workers_per_gather'),
        'jit', current_setting('jit'), 'block_size', current_setting('block_size')),
    'data', jsonb_build_object('rows', (SELECT count(*) FROM kb_plan_orders),
        'rare_rows', (SELECT count(*) FROM kb_plan_orders WHERE customer_id = 42),
        'broad_rows', (SELECT count(*) FROM kb_plan_orders WHERE customer_id = 1)),
    'cases', (SELECT jsonb_object_agg(name, plan) FROM kb_plan_results),
    'result_ids', (SELECT jsonb_object_agg(stage, ids) FROM kb_plan_digests)
);
\echo KB_PLAN_REPORT_END
