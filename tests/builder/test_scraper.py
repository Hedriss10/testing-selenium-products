# tests/builder/test_scraper.py
import logging
import os
from unittest.mock import Mock, patch

import pytest
from dotenv import load_dotenv

from src.builder.scraper import PageObject
from src.models.product import Product

# Carrega o .env do diretório src/
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", ".env"))

# Obtém URL_BASE do .env com fallback
URL_BASE = os.environ.get("URL", "http://example.com")


@pytest.fixture
def mock_webdriver():
    """Fixture para criar um WebDriver simulado."""
    with patch("src.builder.scraper.webdriver.Chrome") as mock_chrome, patch(
        "src.builder.scraper.logging.getLogger"
    ) as mock_logger:
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_wait = Mock()
        mock_driver.wait = mock_wait
        mock_logger.return_value = Mock(spec=logging.Logger)
        yield mock_driver, mock_wait, mock_logger.return_value


@pytest.fixture
def page_object(mock_webdriver):
    """Fixture para criar uma instância de PageObject com WebDriver simulado."""
    driver, wait, logger = mock_webdriver
    category = "Home Goods"
    products = []
    page_object = PageObject(category=category, products=products)
    page_object.wait = wait
    return page_object


def test_page_object_initialization(page_object, mock_webdriver):
    """Testa a inicialização da classe PageObject."""
    driver, wait, logger = mock_webdriver
    assert page_object.category == "Home Goods"
    assert page_object.products == []
    assert page_object.logger is logger
    assert page_object.driver is driver


def test_select_category_all_categories(page_object, mock_webdriver):
    """Testa select_category quando a categoria é 'All Categories'."""
    driver, wait, logger = mock_webdriver
    page_object.category = "All Categories"

    # Mock para product-count
    mock_product_count = Mock(text="10")
    wait.until.return_value = mock_product_count

    page_object.select_category()

    # Verifica que dropdown não foi chamado
    assert not driver.find_element.called
    assert logger.warning.called


def test_select_category_specific(page_object, mock_webdriver):
    """Testa select_category para uma categoria específica."""
    driver, wait, logger = mock_webdriver
    page_object.category = "Home Goods"

    # Mock para dropdown e product-count
    mock_dropdown = Mock()
    mock_product_count = Mock(text="5")
    driver.find_elements.return_value = [Mock()]  # Para lambda
    wait.until.side_effect = [mock_dropdown, mock_dropdown, [Mock()], mock_product_count]

    # Mock para ActionChains
    with patch("src.builder.scraper.ActionChains") as mock_action_chains:
        mock_action = Mock()
        mock_action_chains.return_value = mock_action
        mock_action.key_down.return_value = mock_action
        mock_action.pause.return_value = mock_action
        mock_action.perform.return_value = None

        page_object.select_category()

    # Verifica interações com dropdown
    assert mock_dropdown.click.called
    assert mock_action.key_down.call_count >= 1
    assert logger.info.called


def test_total_products(page_object, mock_webdriver):
    """Testa o método total_products."""
    driver, wait, logger = mock_webdriver
    mock_product_count = Mock(text="10")
    wait.until.return_value = mock_product_count

    result = page_object.total_products()

    assert result == 10
    assert logger.info.called


def test_scrape_products(page_object, mock_webdriver):
    """Testa o método scrape_products."""
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
        driver.find_elements.return_value = [Mock()]  # Simula uma linha na tabela

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

            products = page_object.scrape_products()

    # Verifica o resultado