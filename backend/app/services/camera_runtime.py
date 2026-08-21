from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from threading import Lock, Thread
from uuid import UUID

from sqlalchemy import select

from app.core.database import AsyncSessionFactory
from app.models.database_models import (
    CameraModel,
    CameraShelfMappingModel,
    CameraZoneMappingModel,
    ProductMappingModel,
)
from app.services.camera_services.pipeline import CameraPipeline
from app.services.pipeline.display_pipeline import DisplayConfig

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CameraRuntime:
    camera_id: str
    pipeline: CameraPipeline
    thread: Thread


class CameraRuntimeManager:
    """Owns real camera workers started by the FastAPI camera API."""

    def __init__(self) -> None:
        self._runtimes: dict[str, CameraRuntime] = {}
        self._lock = Lock()

    def is_running(self, camera_id: str) -> bool:
        with self._lock:
            runtime = self._runtimes.get(camera_id)
            return bool(runtime and runtime.thread.is_alive())

    async def start(self, camera_id: str) -> dict:
        with self._lock:
            if camera_id in self._runtimes and self._runtimes[camera_id].thread.is_alive():
                return {"camera_id": camera_id, "status": "running", "active": True}

        async with AsyncSessionFactory() as db:
            camera = await db.get(CameraModel, camera_id)
            if camera is None or not camera.is_active:
                raise ValueError("Camera not found.")
            source = camera.video_path or camera.source_url or camera.rtsp_url
            if not source:
                raise ValueError("Camera has no source configured.")

            zones = (await db.execute(select(CameraZoneMappingModel).where(
                CameraZoneMappingModel.camera_id == camera_id,
                CameraZoneMappingModel.is_active.is_(True),
            ))).scalars().all()
            shelves = (await db.execute(select(CameraShelfMappingModel).where(
                CameraShelfMappingModel.camera_id == camera_id,
                CameraShelfMappingModel.is_active.is_(True),
            ))).scalars().all()
            products = (await db.execute(select(ProductMappingModel).where(
                ProductMappingModel.camera_id == camera_id,
                ProductMappingModel.store_id == camera.store_id,
                ProductMappingModel.is_active.is_(True),
            ))).scalars().all()

            zones_config = {row.zone_id: {"polygon": row.roi_polygon, "bbox": row.bbox} for row in zones}
            shelves_config = {row.shelf_id: {"polygon": row.roi_polygon, "bbox": row.bbox} for row in shelves}
            products_config = {row.product_id: {"polygon": row.roi_polygon, "bbox": row.bbox} for row in products}

            # Keep PostgreSQL UUID objects in the runtime mapping so persistence
            # receives correctly typed foreign-key values.
            store_id: UUID = camera.store_id
            pipeline = CameraPipeline(
                source=source,
                store_id=store_id,
                camera_id=camera_id,
                shelves_config=shelves_config,
                zones_config=zones_config,
                products_config=products_config,
                session_factory=AsyncSessionFactory,
                display_config=DisplayConfig(enabled=False),
            )

            camera.status = "processing"
            await db.commit()

        def runner() -> None:
            try:
                pipeline.run()
            except Exception:
                logger.exception("Camera worker crashed | camera=%s", camera_id)
            finally:
                with self._lock:
                    self._runtimes.pop(camera_id, None)
                asyncio.run(self._set_status(camera_id, "offline"))

        thread = Thread(target=runner, daemon=True, name=f"CameraWorker-{camera_id}")
        runtime = CameraRuntime(camera_id=camera_id, pipeline=pipeline, thread=thread)
        with self._lock:
            self._runtimes[camera_id] = runtime
        thread.start()
        return {"camera_id": camera_id, "status": "running", "active": True}

    async def stop(self, camera_id: str) -> dict:
        with self._lock:
            runtime = self._runtimes.get(camera_id)
        if runtime is not None:
            runtime.pipeline.running = False
            runtime.pipeline.stop()
            runtime.thread.join(timeout=5)
            with self._lock:
                self._runtimes.pop(camera_id, None)
        await self._set_status(camera_id, "offline")
        return {"camera_id": camera_id, "status": "offline", "active": False}

    async def _set_status(self, camera_id: str, status: str) -> None:
        try:
            async with AsyncSessionFactory() as db:
                camera = await db.get(CameraModel, camera_id)
                if camera:
                    camera.status = status
                    await db.commit()
        except Exception:
            logger.exception("Failed to update camera status | camera=%s", camera_id)


camera_runtime_manager = CameraRuntimeManager()
