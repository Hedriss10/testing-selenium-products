# tests/builder/test_scraper.py
import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from dotenv import load_dotenv

from src.builder.scraper import PageObject

load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(os.path.dirname(__file__)), ".env"
    )
)

URL_BASE = os.environ.get("URL")
TOTAL_PRODUCTS = 10
KEY_DOWN_COUNT = 1


@pytest.fixture
def mock_webdriver():
    with patch("src.builder.scraper.webdriver.Remote") as mock_remote:
        mock_driver = MagicMock()
        mock_wait = MagicMock()
        mock_logger = MagicMock()

        mock_remote.return_value = mock_driver

        # WebDriverWait também é chamado com driver
        with patch(
            "src.builder.scraper.WebDriverWait", return_value=mock_wait
        ):
            yield mock_driver, mock_wait, mock_logger


@pytest.fixture
def page_object(mock_webdriver):
    driver, wait, logger = mock_webdriver
    category = "Home Goods"
    page_object = PageObject(category=category)
    page_object.wait = wait
    return page_object


def test_page_object_initialization(mock_webdriver):
    mock_driver, mock_wait, mock_logger = mock_webdriver
    with patch(
        "src.builder.scraper.logging.getLogger", return_value=mock_logger
    ):
        page_object = PageObject(category="Home Goods")
        assert page_object.category == "Home Goods"
        assert page_object.driver is mock_driver
        assert page_object.wait is mock_webdriver[1]
        assert page_object.logger is mock_logger


def test_select_category_all_categories(page_object, mock_webdriver, caplog):
    driver, wait, logger = mock_webdriver
    page_object.category = "All Categories"

    # Mock para product-count
    mock_product_count = Mock(text="10")
    wait.until.return_value = mock_product_count

    with caplog.at_level("WARNING"):
        page_object.select_category(products=[])

    assert not driver.find_element.called
    assert "Expected 10 products" in caplog.text


def test_select_category_specific(page_object, mock_webdriver):
    driver, wait, logger = mock_webdriver
    page_object.category = "Home Goods"

    # Mock para dropdown e product-count
    mock_dropdown = Mock()
    mock_product_count = Mock(text="5")
    driver.find_elements.return_value = [Mock()]
    wait.until.side_effect = [
        mock_dropdown,
        mock_dropdown,
        [Mock()],
        mock_product_count,
    ]

    # Mock para ActionChains
    with patch("src.builder.scraper.ActionChains") as mock_action_chains:
        mock_action = Mock()
        mock_action_chains.return_value = mock_action
        mock_action.key_down.return_value = mock_action
        mock_action.pause.return_value = mock_action
        mock_action.perform.return_value = None

        page_object.select_category(products=[])

    # Verifica interações com dropdown
    assert mock_dropdown.click.called
    assert mock_action.key_down.call_count >= KEY_DOWN_COUNT


def test_total_products(page_object, mock_webdriver):
    driver, wait, logger = mock_webdriver
    mock_product_count = Mock(text="10")
    wait.until.return_value = mock_product_count

    result = page_object.total_products()

    assert result == TOTAL_PRODUCTS


def test_scrape_products(page_object, mock_webdriver):
    driver, wait, logger = mock_webdriver

    with patch("src.builder.scraper.URL_BASE", URL_BASE):
        # Mock para product-count, dropdown, e product rows
        mock_product_count = Mock(text="2")
        mock_dropdown = Mock()
        mock_row = Mock()
        mock_cols = [
            Mock(text="ID"),
            Mock(text="Product Title"),
            Mock(text="Category"),
            Mock(text="$19.99"),
            Mock(text="In Stock (5)"),
            Mock(spec=["find_element"]),
        ]
        mock_cols[5].find_element.return_value = Mock(
            get_attribute=Mock(return_value=f"{URL_BASE}/product")
        )
        mock_row.find_elements.return_value = mock_cols

        # Mock para find_elements no lambda de select_category
        driver.find_elements.return_value = [
            Mock()
        ]  # Simulando uma linha na tabela

        # Define side_effect para todas as chamadas de wait.until
        wait.until.side_effect = [
            mock_product_count,
            mock_dropdown,
            mock_dropdown,
            [mock_row],
            mock_product_count,
            [mock_row],
            mock_row,
        ]

        # Mock para ActionChains em select_category
        with patch("src.builder.scraper.ActionChains") as mock_action_chains:
            mock_action = Mock()
            mock_action_chains.return_value = mock_action
            mock_action.key_down.return_value = mock_action
            mock_action.pause.return_value = mock_action
            mock_action.perform.return_value = None

            page_object.scrape_products()
