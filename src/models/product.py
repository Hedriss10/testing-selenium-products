# src/models/product.py
from pydantic import BaseModel


class Product(BaseModel):
    title: str
    price: float
    link: str
    stock_status: str
    stock_quantity: int
    total: int
