-- Clean-room PostgreSQL contract. Run only in a disposable local database.
CREATE TABLE synthetic_task_runs (
    run_id uuid NOT NULL,
    pipeline_name text NOT NULL,
    task_name text NOT NULL,
    failed_at timestamptz NOT NULL,
    status text NOT NULL CHECK (status IN ('failed', 'success')),
    error_class text,
    safe_error_message text,
    raw_log text
);

CREATE VIEW assistant_task_failures AS
SELECT
    run_id,
    pipeline_name,
    task_name,
    failed_at,
    error_class,
    left(safe_error_message, 500) AS error_excerpt
FROM synthetic_task_runs
WHERE status = 'failed';

CREATE ROLE incident_gateway NOLOGIN;
REVOKE ALL ON synthetic_task_runs FROM incident_gateway;
GRANT SELECT ON assistant_task_failures TO incident_gateway;
