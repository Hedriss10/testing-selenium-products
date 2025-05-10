import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execute.service import ExecuteService, SCRAPER_SEMAPHORE
from src.models.product import Product


@pytest.mark.asyncio
async def test_execute_service_initialization():
    # Arrange
    category = "electronics"
    with patch.dict(os.environ, {"WORK_THREAD": "4"}):
        # Act
        service = ExecuteService(category=category)

        # Assert
        assert service.category == category
        assert service.size == 4
        assert service.pool.category == category
        assert service.pool.size == 4


@pytest.mark.asyncio
async def test_execute_service_initialization_invalid_work_thread():
    # Arrange
    category = "electronics"
    with patch.dict(os.environ, {"WORK_THREAD": "invalid"}):
        # Act & Assert
        with pytest.raises(ValueError):
            ExecuteService(category=category)


@pytest.mark.asyncio
async def test_execute_service_run_success():
    # Arrange
    category = "electronics"
    mock_products = [Product(name="Product1"), Product(name="Product2")]
    with patch.dict(os.environ, {"WORK_THREAD": "4"}):
        service = ExecuteService(category=category)
        service.pool.pool_with_threads = MagicMock(return_value=mock_products)

        # Mock semaphore acquire and release
        with patch(
            "src.execute.service.SCRAPER_SEMAPHORE.acquire",
            AsyncMock(return_value=True),
        ):
            with patch(
                "src.execute.service.SCRAPER_SEMAPHORE.release", MagicMock()
            ) as mock_release:
                # Mock ThreadPoolExecutor
                with patch(
                    "concurrent.futures.ThreadPoolExecutor",
                    MagicMock(spec=ThreadPoolExecutor),
                ) as mock_executor:
                    # Act
                    result = await service.run()

                    # Assert
                    assert result == mock_products
                    service.pool.pool_with_threads.assert_called_once()
                    mock_executor.assert_called_once_with(4)
                    mock_release.assert_called_once()


@pytest.mark.asyncio
async def test_execute_service_run_no_worker_available(caplog):
    # Arrange
    category = "electronics"
    with patch.dict(os.environ, {"WORK_THREAD": "4"}):
        service = ExecuteService(category=category)

        # Mock semaphore acquire to raise TimeoutError
        with patch(
            "src.execute.service.SCRAPER_SEMAPHORE.acquire",
            AsyncMock(side_effect=asyncio.TimeoutError),
        ):
            # Capture logging
            caplog.set_level(logging.INFO)

            # Act & Assert
            with pytest.raises(RuntimeError, match="no_worker_available"):
                await service.run()

            # Assert logging
            assert "Error no worker available" in caplog.text


@pytest.mark.asyncio
async def test_execute_service_run_releases_semaphore_on_failure():
    # Arrange
    category = "electronics"
    with patch.dict(os.environ, {"WORK_THREAD": "4"}):
        service = ExecuteService(category=category)
        service.pool.pool_with_threads = MagicMock(
            side_effect=Exception("Test error")
        )

        # Mock semaphore acquire and release
        with patch(
            "src.execute.service.SCRAPER_SEMAPHORE.acquire",
            AsyncMock(return_value=True),
        ):
            with patch(
                "src.execute.service.SCRAPER_SEMAPHORE.release", MagicMock()
            ) as mock_release:
                # Mock ThreadPoolExecutor
                with patch(
                    "concurrent.futures.ThreadPoolExecutor",
                    MagicMock(spec=ThreadPoolExecutor),
                ):
                    # Act & Assert
                    with pytest.raises(Exception, match="Test error"):
                        await service.run()
                    mock_release.assert_called_once()


@pytest.mark.asyncio
async def test_execute_service_run_executor_setup():
    # Arrange
    category = "electronics"
    mock_products = [Product(name="Product3")]
    with patch.dict(os.environ, {"WORK_THREAD": "2"}):
        service = ExecuteService(category=category)
        service.pool.pool_with_threads = MagicMock(return_value=mock_products)

        # Mock semaphore and asyncio loop
        with patch(
            "src.execute.service.SCRAPER_SEMAPHORE.acquire",
            AsyncMock(return_value=True),
        ):
            with patch(
                "src.execute.service.SCRAPER_SEMAPHORE.release", MagicMock()
            ):
                with patch("asyncio.get_event_loop", MagicMock()) as mock_loop:
                    mock_loop.return_value.run_in_executor = AsyncMock(
                        return_value=mock_products
                    )
                    with patch(
                        "concurrent.futures.ThreadPoolExecutor",
                        MagicMock(spec=ThreadPoolExecutor),
                    ) as mock_executor:
                        # Act
                        result = await service.run()

                        # Assert
                        assert result == mock_products
                        mock_loop.return_value.run_in_executor.assert_called_once()
                        mock_executor.assert_called_once_with(2)
