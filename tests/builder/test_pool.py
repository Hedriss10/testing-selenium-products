# tests/test_pool.py

from unittest.mock import MagicMock, patch

import pytest

from src.builder.pool import ScrapePool
from src.models.product import Product

SIZE = 4
MOCK_COUNT_MAX = 4


@pytest.fixture
def fake_product():
    product = Product(
        title="Test Product",
        price=9.99,
        link="https://example.com/product",
        stock_status="In Stock",
        stock_quantity=10,
        total=100,
    )
    return product


@patch("src.builder.pool.PageObject")
def test_run_scraper(mock_pageobject_class, fake_product):
    mock_instance = MagicMock()
    mock_instance.scrape_products.return_value = [fake_product]
    mock_pageobject_class.return_value = mock_instance

    result = ScrapePool(size=SIZE, category="Fake Category").run_scraper()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Product)
    assert result[0].title == "Test Product"


@patch("src.builder.pool.ScrapePool.run_scraper")
def test_main_aggregates_products(mock_run_scraper, fake_product):
    mock_run_scraper.side_effect = [
        [fake_product],
        [fake_product],
        [fake_product],
        [fake_product],
    ]

    ScrapePool(size=SIZE, category="Fake Category").pool_with_threads()

    assert mock_run_scraper.call_count == MOCK_COUNT_MAX
