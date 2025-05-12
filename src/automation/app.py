# src/automation/app.py

from typing import Literal

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.execute.service import ExecuteService

app = FastAPI(
    title="Scraper", description="Scraper automation api.", version="0.0.1"
)

FILTER_ARGUMENTS_SCRAPE = [
    "All Categories",
    "Apparel",
    "Cosmetics",
    "Electronics",
    "Home Goods",
]


@app.get(
    "/scrape",
    tags=["scrape"],
    responses={
        status.HTTP_200_OK: {
            "description": "List of scraped products",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "title": "Example Title Product",
                            "price": 0.0,
                            "link": "https://example.com",
                            "stock_status": "In Stock",
                            "stock_quantity": 30,
                            "total": 50,
                        }
                    ]
                }
            },
        },
        404: {
            "messages": [
                {"message_id": "Category not found"},
                {"message_id": "Product not found"},
            ]
        },
        429: {"description": "No worker available"},
    },
)
async def scraper_products(
    category: Literal[
        "All Categories", "Apparel", "Cosmetics", "Electronics", "Home Goods"
    ],
):
    """Get products from category"""

    if category not in FILTER_ARGUMENTS_SCRAPE:
        return JSONResponse(
            content=jsonable_encoder({"message_id": "Category not found"}),
            status_code=404,
        )

    service = ExecuteService(category=category)

    try:
        products = await service.run()

        if not products:
            return JSONResponse(
                content=jsonable_encoder({"message_id": "Product not found"}),
                status_code=404,
            )

        return JSONResponse(content=jsonable_encoder(products))
    except RuntimeError as e:
        if str(e) == "no_worker_available":
            return JSONResponse(
                content={"detail": "no worker available"},
                status_code=429,
            )
        raise e

    finally:
        service.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
