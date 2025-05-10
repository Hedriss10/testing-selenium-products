# src/executor/service.py
import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

from dotenv import load_dotenv

from src.builder.pool import ScrapePool
from src.models.product import Product

load_dotenv()

WORK_THREAD = int(os.environ.get("WORK_THREAD"))

SCRAPER_SEMAPHORE = asyncio.Semaphore(value=WORK_THREAD)


logging.basicConfig(level=logging.INFO)


class ExecuteService:
    def __init__(self, category: str):
        self.category = category
        self.size = int(os.environ.get("WORK_THREAD"))
        self.pool = ScrapePool(size=self.size, category=self.category)

    async def run(self) -> List[Product]:
        try:
            await asyncio.wait_for(SCRAPER_SEMAPHORE.acquire(), timeout=0.1)
        except asyncio.TimeoutError:
            logging.info("Error no worker available")
            raise RuntimeError("no_worker_available")
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(self.size) as executor:
                return await loop.run_in_executor(
                    executor, self.pool.pool_with_threads
                )
        finally:
            SCRAPER_SEMAPHORE.release()
