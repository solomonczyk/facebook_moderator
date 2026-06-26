"""Worker service: bridges the watcher with the runtime agent for event processing."""

from sqlalchemy.orm import Session

from ..runtime_agent.agent_core import RuntimeAgent
from .config import WorkerConfig
from .own_group_watcher import OwnGroupWatcher
from .worker_models import WorkerRunResult


class WorkerService:
    def __init__(self, db: Session, config: WorkerConfig | None = None):
        self.config = config or WorkerConfig()
        self.config.load_from_env()
        self.watcher = OwnGroupWatcher(self.config)
        self._agent: RuntimeAgent | None = None
        self._db = db

    @property
    def agent(self) -> RuntimeAgent:
        if self._agent is None:
            self._agent = RuntimeAgent(self._db)
        return self._agent

    def sync_config(self) -> None:
        """Propagate config changes to the watcher."""
        self.watcher.config = self.config

    def start(self) -> tuple[bool, str]:
        self.sync_config()
        return self.watcher.start()

    def stop(self) -> None:
        self.watcher.stop()

    def pause(self) -> None:
        self.watcher.pause()

    def resume(self) -> None:
        self.watcher.resume()

    def emergency_stop(self, reason: str = "") -> None:
        self.watcher.emergency_stop(reason)

    def run_once(self, dry_run: bool = False) -> WorkerRunResult:
        return self.watcher.run_once(dry_run=dry_run)

    def process_and_queue(self, events: list) -> int:
        """Send captured events to runtime agent. Returns count of processed events."""
        count = 0
        for event in events:
            result = self.agent.process_event(event)
            if result.get("success"):
                count += 1
        return count

    def get_status(self) -> dict:
        status = self.watcher.get_status()
        status["config"] = self.config.to_dict()
        return status
