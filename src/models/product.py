# src/models/product.py

from pydantic import BaseModel

CATEGORY_ORDER = {
    "All Categories": 0,
    "Apparel": 1,
    "Cosmetics": 2,
    "Electronics": 3,
    "Home Goods": 4,
}


class Product(BaseModel):
    title: str
    price: float
    link: str
    stock_status: str
    stock_quantity: int
    total: int
