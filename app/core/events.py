import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import Settings
from .logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    container = getattr(app.state, 'container', None)
    if container is None:
        raise RuntimeError('App container not initialized')
    settings: Settings = container.settings
    configure_logging(settings)
    
    base_url = settings.external_base_url or f"http://{settings.app_host}:{settings.app_port}"
    logger = logging.getLogger("fastapi.llm_query")
    logger.info(
        "\n\nLLM Query Service\n------------------\n- Service live at %s%s \n- Docs: %s/docs\n\n",
        base_url,
        settings.api_prefix,
        base_url,
    )
    yield
    await asyncio.sleep(0)
