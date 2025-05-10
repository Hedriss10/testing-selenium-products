# tests/automation/test_app.py

import pytest
import os
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from dotenv import load_dotenv

from src.automation.app import app
from src.models.product import Product


load_dotenv()


URL = os.environ.get("URL")

# Unit tests using FastAPI TestClient
client = TestClient(app)


def test_scrape_valid_category_success():
    # Arrange
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
    with patch("src.automation.app.ExecuteService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.run = AsyncMock(return_value=mock_products)

        # Act
        response = client.get(f"/scrape?category={category}")

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                "title": "Test Product",
                "price": 99.99,
                "link": "https://example.com",
                "stock_status": "In Stock",
                "stock_quantity": 10,
                "total": 50,
            }
        ]
        mock_service.assert_called_once_with(category=category)
        mock_service_instance.run.assert_awaited_once()


def test_scrape_invalid_category():
    # Arrange
    category = "Invalid Category"

    # Act
    response = client.get(f"/scrape?category={category}")

    # Assert
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "literal_error",
                "loc": ["query", "category"],
                "msg": "Input should be 'All Categories', 'Apparel', 'Cosmetics', 'Electronics' or 'Home Goods'",
                "input": "Invalid Category",
                "ctx": {
                    "expected": "'All Categories', 'Apparel', 'Cosmetics', 'Electronics' or 'Home Goods'"
                },
            }
        ]
    }


def test_scrape_no_products():
    # Arrange
    category = "Electronics"
    with patch("src.automation.app.ExecuteService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.run = AsyncMock(return_value=[])

        # Act
        response = client.get(f"/scrape?category={category}")

        # Assert
        assert response.status_code == 404
        assert response.json() == {"message_id": "Product not found"}
        mock_service.assert_called_once_with(category=category)
        mock_service_instance.run.assert_awaited_once()


def test_scrape_no_worker_available():
    # Arrange
    category = "Electronics"
    with patch("src.automation.app.ExecuteService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.run = AsyncMock(
            side_effect=RuntimeError("no_worker_available")
        )

        # Act
        response = client.get(f"/scrape?category={category}")

        # Assert
        assert response.status_code == 429
        assert response.json() == {"detail": "nenhum trabalhador disponível"}
        mock_service.assert_called_once_with(category=category)
        mock_service_instance.run.assert_awaited_once()


def test_scrape_unhandled_exception():
    # Arrange
    category = "Electronics"
    with patch("src.automation.app.ExecuteService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.run = AsyncMock(
            side_effect=RuntimeError("other_error")
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="other_error"):
            client.get(f"/scrape?category={category}")
        mock_service.assert_called_once_with(category=category)
        mock_service_instance.run.assert_awaited_once()


# Integration test using httpx.AsyncClient
@pytest.mark.asyncio
async def test_scrape_integration_valid_category():
    # Arrange
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
    with patch("src.automation.app.ExecuteService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.run = AsyncMock(return_value=mock_products)

        # Act
        async with AsyncClient(app=app, base_url=f"{URL}") as client:
            response = await client.get(f"/scrape?category={category}")

        # Assert
        assert response.status_code == 200
        assert response.json() == [
            {
                "title": "Test Product",
                "price": 99.99,
                "link": "https://example.com",
                "stock_status": "In Stock",
                "stock_quantity": 10,
                "total": 50,
            }
        ]
        mock_service.assert_called_once_with(category=category)
        mock_service_instance.run.assert_awaited_once()
