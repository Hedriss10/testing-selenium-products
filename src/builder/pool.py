# src/builder/pool.py

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

from dotenv import load_dotenv

from src.builder.scraper import PageObject
from src.models.product import Product

logging.basicConfig(level=logging.INFO)

load_dotenv()


CATEGORIES = [
    "All Categories",
    "Apparel",
    "Cosmetics",
    "Electronics",
    "Home Goods",
]

WORK_THREAD = os.environ.get("WORK_THREAD")


def run_scraper(category: str) -> List[Product]:
    logging.info(f"Start scraper: {category}")
    scraper = PageObject(category=category)
    products = scraper.scrape_products()
    logging.info(f"Success scraper: {category} with {len(products)}")
    return products


def pool_with_threads(size: int = int(WORK_THREAD)):
    with ThreadPoolExecutor(size) as executor:
        futures = [
            executor.submit(run_scraper, category) for category in CATEGORIES
        ]

        all_products = []
        for future in futures:
            try:
                products = future.result()
                all_products.extend(products)
            except Exception as e:
                logging.error(f"Erro there is an error: {e}")

    logging.info(f"Total of products: {len(all_products)}")
