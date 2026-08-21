from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.ai.detector import PersonDetector
from app.ai.frame_processor import FrameProcessor
from app.ai.tracker import PersonTracker
from app.analytics.domain.dwell.dwell_orchestrator import DwellOrchestrator
from app.analytics.domain.dwell.dwell_policy import DwellPolicy
from app.analytics.domain.dwell.services.dwell_service import DwellService
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics_service import AnalyticsService
from app.services.analytics_sync import AnalyticsSyncService
from app.services.background_sync import BackgroundAnalyticsSync
from app.services.pipeline.analytics_pipeline import AnalyticsPipeline
from app.services.pipeline.display_pipeline import DisplayConfig, DisplayPipeline
from app.services.pipeline.frame_pipeline import FramePipeline
from app.services.pipeline.render_pipeline import RenderConfig, RenderPipeline


@dataclass(slots=True)
class ServiceRegistry:
    performance: Any
    processor: FrameProcessor
    detector: PersonDetector
    tracker: PersonTracker
    dwell_policy: DwellPolicy
    dwell_service: DwellService
    dwell_orchestrator: DwellOrchestrator
    repository: AnalyticsRepository | None
    storage: AnalyticsService | None
    background_sync: BackgroundAnalyticsSync
    analytics_sync: AnalyticsSyncService
    frame_pipeline: FramePipeline
    analytics_pipeline: AnalyticsPipeline
    render_pipeline: RenderPipeline
    display_pipeline: DisplayPipeline
    store_id: object | None = None
    camera_id: str | None = None
    shelves_config: dict[str, Any] | None = None
    zones_config: dict[str, Any] | None = None
    products_config: dict[str, Any] | None = None


def build_services(
    performance: Any,
    *,
    store_id: object | None = None,
    camera_id: str | None = None,
    shelves_config: dict[str, Any] | None = None,
    zones_config: dict[str, Any] | None = None,
    products_config: dict[str, Any] | None = None,
    db: Any | None = None,
    session_factory: Any | None = None,
    render_config: RenderConfig | None = None,
    display_config: DisplayConfig | None = None,
) -> ServiceRegistry:
    """Create one completely wired runtime graph.

    The CV thread never owns a request-scoped AsyncSession. Persistence is done
    by a background worker using a fresh session per job.
    """
    from app.core.database import AsyncSessionFactory

    factory = session_factory or AsyncSessionFactory
    active_shelves = shelves_config or {}
    active_zones = zones_config or {}
    active_products = products_config or {}

    detector = PersonDetector()
    tracker = PersonTracker()
    processor = FrameProcessor(
        shelves_config=active_shelves,
        zones_config=active_zones,
        products_config=active_products,
        store_id=store_id,
        camera_id=camera_id,
        detector=detector,
        tracker=tracker,
    )

    dwell_policy = DwellPolicy()
    dwell_service = DwellService(policy=dwell_policy)
    dwell_orchestrator = DwellOrchestrator(dwell_service=dwell_service)

    repository = AnalyticsRepository(db=db) if db is not None else None
    storage = AnalyticsService(db=db) if db is not None else None
    background_sync = BackgroundAnalyticsSync(session_factory=factory)
    analytics_sync = AnalyticsSyncService(background_sync=background_sync)

    frame_pipeline = FramePipeline(processor=processor, detector=detector, tracker=tracker)
    analytics_pipeline = AnalyticsPipeline(dwell_orchestrator=dwell_orchestrator)
    render_pipeline = RenderPipeline(
        tracker=tracker,
        analytics=analytics_pipeline,
        config=render_config or RenderConfig(),
    )
    display_pipeline = DisplayPipeline(config=display_config or DisplayConfig(enabled=False))

    return ServiceRegistry(
        performance=performance,
        processor=processor,
        detector=detector,
        tracker=tracker,
        dwell_policy=dwell_policy,
        dwell_service=dwell_service,
        dwell_orchestrator=dwell_orchestrator,
        repository=repository,
        storage=storage,
        background_sync=background_sync,
        analytics_sync=analytics_sync,
        frame_pipeline=frame_pipeline,
        analytics_pipeline=analytics_pipeline,
        render_pipeline=render_pipeline,
        display_pipeline=display_pipeline,
        store_id=store_id,
        camera_id=camera_id,
        shelves_config=active_shelves,
        zones_config=active_zones,
        products_config=active_products,
    )
