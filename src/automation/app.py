# src/automation/app.py

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Scraper", description="Scraper automation api.", version="0.0.1"
)


CATEGORIES = [
    "All Categories",
    "Apparel",
    "Cosmetics",
    "ElectronicsHome Goods",
]


@app.get("/scrape", tags=["scrape"])
async def scraper_products(category: str):
    if category.lower() not in CATEGORIES:
        return JSONResponse(
            content=jsonable_encoder({"message_id": "Category not found"}),
            status_code=404,
        )
    return True


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
