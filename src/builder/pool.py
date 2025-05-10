# src/builder/pool.py

import logging
import os
from concurrent.futures import ThreadPoolExecutor

from src.builder.scraper import PageObject

logging.basicConfig(level=logging.INFO)


WORK_THREAD = os.environ.get("WORK_THREAD")


class ScrapePool:
    def __init__(self, size: int, category: str):
        self.size = size
        self.category = category
        self.page_object = PageObject(category=category)

    def run_scraper(self):
        logging.info(f"Start scraper: {self.category}")
        products = self.page_object.scrape_products()
        logging.info(f"Success scraper: {self.category} with {len(products)}")
        return products

    def pool_with_threads(self):
        with ThreadPoolExecutor(self.size) as executor:
            futures = [
                executor.submit(self.run_scraper) for _ in range(self.size)
            ]
            all_products = []
            for future in futures:
                try:
                    products = future.result()
                    all_products.extend(products)
                except Exception as e:
                    logging.error(f"Erro there is an error: {e}")
            return all_products

        logging.info(f"Total of products: {len(all_products)}")
