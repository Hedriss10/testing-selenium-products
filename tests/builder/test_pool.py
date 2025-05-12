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


@pytest.mark.asyncio
def test_main_aggregates_products():
    category = "Electronics"
    mock_products = [
        Product(
            title="Test Product",
            price=99.99,
            link="https://example.com",
            stock_status="In Stock",
            stock_quantity=10,
            total=50,
        )
    ]
    with patch("src.builder.pool.PageObject") as mock_page_object:
        mock_page_object_instance = mock_page_object.return_value
        mock_page_object_instance.scrape.return_value = mock_products
        pool = ScrapePool(size=1, category=category)
        results = pool.run_scraper()
        assert results != mock_products
        mock_page_object.assert_called_once_with(category=category)
