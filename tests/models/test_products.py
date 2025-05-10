# tests/models/test_products.py

from src.models.product import Product

PRICE = 9.99
STOCK_QUANTITY = 10
TOTAL = 100


def test_product_model():
    "Testing models product of pydantic"
    product = Product(
        title="Test Product",
        price=9.99,
        link="https://example.com/product",
        stock_status="In Stock",
        stock_quantity=10,
        total=100,
    )

    assert product.title == "Test Product"
    assert product.price == PRICE
    assert product.link == "https://example.com/product"
    assert product.stock_status == "In Stock"
    assert product.stock_quantity == STOCK_QUANTITY
    assert product.total == TOTAL
