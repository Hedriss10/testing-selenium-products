# src/automation/app.py
from typing import Union

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Scraper", description="Scraper automation api.", version="0.0.1"
)


@app.get("/users", tags=["users"])
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}", tags=["items"])
def read_item(item_id: int, q: Union[str, None] = None):
    if isinstance(item_id, int):
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({"item_id": item_id, "q": q}),
        )
    else:
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder({"item_id": item_id, "q": q}),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
