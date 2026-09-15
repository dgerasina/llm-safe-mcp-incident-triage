"""Tests for the clean-room, read-only incident-triage gateway."""

from datetime import datetime, timezone
from unittest import TestCase
from uuid import UUID, uuid4

from gateway import IncidentGateway, TaskFailure


class IncidentGatewayTests(TestCase):
    def setUp(self) -> None:
        self.run_id = uuid4()
        self.other_run_id = uuid4()
        self.gateway = IncidentGateway(
            failures=(
                TaskFailure(
                    run_id=self.run_id,
                    task_name="load_events",
                    failed_at=datetime(2026, 9, 15, 8, 0, tzinfo=timezone.utc),
                    error_class="ConnectionTimeout",
                    safe_error_message="upstream did not answer",
                    raw_log="Authorization: Bearer should-never-leave-the-store",
                ),
                TaskFailure(
                    run_id=self.other_run_id,
                    task_name="refresh_catalog",
                    failed_at=datetime(2026, 9, 15, 9, 0, tzinfo=timezone.utc),
                    error_class="ValueError",
                    safe_error_message="bad input",
                    raw_log="customer_email=private@example.test",
                ),
            )
        )

    def test_returns_only_failures_for_requested_run(self) -> None:
        result = self.gateway.failed_tasks_for_run(str(self.run_id))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["task_name"], "load_events")
        self.assertEqual(result[0]["error_class"], "ConnectionTimeout")

    def test_rejects_an_invalid_run_id(self) -> None:
        with self.assertRaisesRegex(ValueError, "run_id"):
            self.gateway.failed_tasks_for_run("not-a-uuid")

    def test_never_returns_raw_logs_or_unknown_fields(self) -> None:
        result = self.gateway.failed_tasks_for_run(self.run_id)

        self.assertEqual(
            set(result[0]),
            {"task_name", "failed_at", "error_class", "error_excerpt"},
        )
        self.assertNotIn("Bearer", str(result))
        self.assertNotIn("private@example.test", str(result))

    def test_truncates_error_excerpt_to_a_fixed_limit(self) -> None:
        long_error = "x" * 600
        gateway = IncidentGateway(
            failures=(
                TaskFailure(
                    run_id=self.run_id,
                    task_name="load_events",
                    failed_at=datetime(2026, 9, 15, 8, 0, tzinfo=timezone.utc),
                    error_class="ConnectionTimeout",
                    safe_error_message=long_error,
                    raw_log="raw",
                ),
            )
        )

        result = gateway.failed_tasks_for_run(self.run_id)

        self.assertEqual(len(result[0]["error_excerpt"]), 500)

    def test_rejects_unbounded_dependency_depth(self) -> None:
        with self.assertRaisesRegex(ValueError, "depth"):
            self.gateway.downstream_impact("load_events", depth=3)

    def test_does_not_accept_sql_as_an_argument(self) -> None:
        with self.assertRaises(TypeError):
            self.gateway.failed_tasks_for_run(self.run_id, sql="SELECT * FROM raw_logs")
