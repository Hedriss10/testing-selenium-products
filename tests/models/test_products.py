# tests/models/test_products.py

from src.models.product import Product  

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
    assert product.price == 9.99
    assert product.link == "https://example.com/product"
    assert product.stock_status == "In Stock"
    assert product.stock_quantity == 10
    assert product.total == 100
