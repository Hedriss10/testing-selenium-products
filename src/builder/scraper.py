# src/builder/scraper.py

import logging
import os
import re

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.models.product import Product

load_dotenv()

URL_BASE = os.environ.get("URL")
HEADLES = os.environ.get("HEADLES")
NO_SANDBOX = os.environ.get("NO_SANDBOX")
DISABLE_DEV_SHM_USAGE = os.environ.get("DISABLE_DEV_SHM_USAGE")
SELENIUM_TESTING = os.environ.get("SELENIUM_TESTING")

CATEGORY_ORDER = {
    "All Categories": 0,
    "Apparel": 1,
    "Cosmetics": 2,
    "Electronics": 3,
    "Home Goods": 4,
}


MINIMUM_COLUMN_COUNT = 6


class WebdriverManager:
    def __init__(self):
        options = Options()
        options.add_argument(f"{HEADLES}")
        options.add_argument(f"{NO_SANDBOX}")
        options.add_argument(f"{DISABLE_DEV_SHM_USAGE}")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.logger = logging.getLogger(f"{SELENIUM_TESTING}")


class PageObject(WebdriverManager):
    def __init__(self, category: list):
        self.category = category
        super().__init__()

    def __visibility_of_element_located_product_rows(self):
        # Wait for product rows to be present and visible
        try:
            product_rows = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "#product-tbody tr")
                )
            )
            self.logger.info(f"Found {len(product_rows)} product rows")
            return product_rows
        except Exception as e:
            self.logger.error(f"Could not load product rows: {e}")
            return []

    def select_category(self, products: list):
        if self.category != "All Categories":
            try:
                self.logger.info(f"Selecting category {self.category}")
                dropdown = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "category-filter"))
                )
                dropdown.click()

                # Wait for dropdown to be visible
                self.wait.until(
                    EC.visibility_of_element_located(
                        (By.ID, "category-filter")
                    )
                )

                position = CATEGORY_ORDER[self.category]
                for _ in range(position):
                    ActionChains(self.driver).key_down(Keys.DOWN).pause(
                        0.5
                    ).perform()

                ActionChains(self.driver).key_down(Keys.ENTER).pause(
                    0.5
                ).perform()

                # Wait for product table to update
                self.wait.until(
                    lambda d: len(
                        d.find_elements(By.CSS_SELECTOR, "#product-tbody tr")
                    )
                    > 0
                )
                self.logger.info(f"Category '{self.category}' selected.")
            except Exception as e:
                self.logger.error(
                    f"Failed to select category '{self.category}': {e}"
                )
                return []
        try:
            expected_count = int(
                self.wait.until(
                    EC.presence_of_element_located((By.ID, "product-count"))
                ).text.strip()
            )
            if expected_count is not None and len(products) != expected_count:
                self.logger.warning(f"Expected {expected_count} products")
        except Exception:
            expected_count = None

    def total_products(self):
        # total products in category
        try:
            product_count_elem = self.wait.until(
                EC.presence_of_element_located((By.ID, "product-count"))
            )
            expected_count = int(product_count_elem.text.strip())
            return expected_count
        except Exception as e:
            self.logger.warning(f"Could not retrieve product count: {e}")
            expected_count = None

    def scrape_products(self):
        self.logger.info(f"Scraping category: {self.category}")
        self.driver.get(URL_BASE)

        products = []

        # Wait for page to load
        self.wait.until(
            EC.presence_of_element_located((By.ID, "product-count"))
        )
        self.select_category(products=products)

        product_rows = self.__visibility_of_element_located_product_rows()

        for row in product_rows:
            try:
                # Wait for row to be visible
                self.wait.until(EC.visibility_of(row))
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) < MINIMUM_COLUMN_COUNT:
                    self.logger.warning("Row does not have enough columns")
                    continue

                title = cols[1].text.strip()
                price = float(re.sub(r"[^\d.]", "", cols[3].text.strip()))
                stock_raw = cols[4].text.strip()
                stock_status = (
                    "In Stock" if "In Stock" in stock_raw else "Out of Stock"
                )
                stock_quantity = (
                    int(re.search(r"\((\d+)\)", stock_raw).group(1))
                    if "In Stock" in stock_raw
                    else 0
                )

                try:
                    link_elem = cols[5].find_element(
                        By.CLASS_NAME, "view-details-btn"
                    )
                    link = link_elem.get_attribute("href") or ""
                except AttributeError:
                    link = ""
                    self.logger.warning(f"No link found for product: {title}")

                products.append(
                    Product(
                        title=title,
                        price=price,
                        link=link,
                        stock_status=stock_status,
                        stock_quantity=stock_quantity,
                        total=self.total_products(),
                    )
                )

            except Exception as e:
                self.logger.error(f"Failed to scrape product: {e}")

        return products
