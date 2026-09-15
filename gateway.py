"""Clean-room core for a read-only incident-triage MCP gateway.

The module intentionally has no database driver or MCP dependency. It makes the
security contract executable and testable; a transport adapter can call it later.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


MAX_ERROR_CHARS = 500
MAX_DEPENDENCY_DEPTH = 2


@dataclass(frozen=True)
class TaskFailure:
    run_id: UUID
    task_name: str
    failed_at: datetime
    error_class: str
    safe_error_message: str
    raw_log: str


class IncidentGateway:
    """Expose only bounded, read-only incident data to an LLM adapter."""

    def __init__(self, failures: tuple[TaskFailure, ...]) -> None:
        self._failures = failures

    def failed_tasks_for_run(self, run_id: UUID | str) -> list[dict[str, str]]:
        parsed_run_id = self._parse_run_id(run_id)
        return [
            {
                "task_name": failure.task_name,
                "failed_at": failure.failed_at.isoformat(),
                "error_class": failure.error_class,
                "error_excerpt": failure.safe_error_message[:MAX_ERROR_CHARS],
            }
            for failure in self._failures
            if failure.run_id == parsed_run_id
        ]

    def downstream_impact(self, task_name: str, depth: int) -> list[str]:
        if not task_name:
            raise ValueError("task_name must not be empty")
        if not 1 <= depth <= MAX_DEPENDENCY_DEPTH:
            raise ValueError(f"depth must be between 1 and {MAX_DEPENDENCY_DEPTH}")
        return []

    @staticmethod
    def _parse_run_id(run_id: UUID | str) -> UUID:
        if isinstance(run_id, UUID):
            return run_id
        try:
            return UUID(run_id)
        except (TypeError, ValueError) as error:
            raise ValueError("run_id must be a UUID") from error
