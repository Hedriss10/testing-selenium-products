# tests/automation/test_app.py

import os
from unittest.mock import AsyncMock, patch

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.automation.app import app
from src.models.product import Product

load_dotenv()


URL = os.environ.get("URL")

# Unit tests using FastAPI TestClient
client = TestClient(app)


STATUS_CODE_OK = 200
STATUS_INVALID_CATEGORY = 422
STATUS_NO_WORKER_AVAILABLE = 429
STATUS_NOT_FOUND = 404


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
        assert response.status_code == STATUS_CODE_OK
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
    assert response.status_code == STATUS_INVALID_CATEGORY
    body = response.json()
    assert body["detail"][0]["type"] == "literal_error"
    assert body["detail"][0]["loc"] == ["query", "category"]
    assert body["detail"][0]["input"] == "Invalid Category"
    assert "All Categories" in body["detail"][0]["msg"]
    assert "Apparel" in body["detail"][0]["msg"]


def test_scrape_no_products():
    # Arrange
    category = "Electronics"
    with patch("src.automation.app.ExecuteService") as mock_service:
        mock_service_instance = mock_service.return_value
        mock_service_instance.run = AsyncMock(return_value=[])

        # Act
        response = client.get(f"/scrape?category={category}")

        # Assert
        assert response.status_code == STATUS_NOT_FOUND
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
        assert response.status_code == STATUS_NO_WORKER_AVAILABLE
        body = response.json()
        assert "detail" in body
        assert "no worker available" in body["detail"].lower()
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
        assert response.status_code == STATUS_CODE_OK
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
