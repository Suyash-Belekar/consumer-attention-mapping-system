from __future__ import annotations

import asyncio
import logging
from queue import Empty, Queue
from threading import Event, Thread
from typing import Any

from app.analytics.domain.dwell.dwell_models import DwellRecord

logger = logging.getLogger(__name__)


class BackgroundAnalyticsSync:
    """Threaded bridge from synchronous CV processing to isolated async DB sessions.

    Every queued job opens its own AsyncSession. This prevents an AsyncSession from
    being used across event loops/threads, which is unsafe with SQLAlchemy asyncio.
    """

    def __init__(self, session_factory, queue_size: int = 2000) -> None:
        self._session_factory = session_factory
        self._queue: Queue[Any] = Queue(maxsize=queue_size)
        self._shutdown = Event()
        self._worker = Thread(target=self._run, daemon=True, name="AnalyticsSyncWorker")
        self._worker.start()
        logger.info("Background analytics worker started.")

    def enqueue(self, job: Any) -> None:
        self._queue.put(job)

    @property
    def queue_size(self) -> int:
        return self._queue.qsize()

    @property
    def is_running(self) -> bool:
        return self._worker.is_alive()

    def _run(self) -> None:
        while not self._shutdown.is_set() or not self._queue.empty():
            try:
                job = self._queue.get(timeout=0.5)
            except Empty:
                continue
            try:
                asyncio.run(self._persist(job))
            except Exception:
                logger.exception("Failed to persist analytics job.")
            finally:
                self._queue.task_done()

    async def _persist(self, job: Any) -> None:
        from app.services.analytics_service import AnalyticsService

        async with self._session_factory() as session:
            service = AnalyticsService(session)
            if isinstance(job, DwellRecord):
                await service.save_session(job)
            elif isinstance(job, list):
                await service.save_tracking_points(job)
            else:
                raise TypeError(f"Unsupported analytics job: {type(job)!r}")
            await session.commit()

    def wait_until_empty(self) -> None:
        self._queue.join()

    def stop(self) -> None:
        logger.info("Stopping background analytics worker...")
        self._shutdown.set()
        self.wait_until_empty()
        self._worker.join(timeout=10)
        logger.info("Background analytics worker stopped.")

    def status(self) -> dict[str, int | bool]:
        return {"running": self.is_running, "queue_size": self.queue_size}
