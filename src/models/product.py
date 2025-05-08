from pydantic import BaseModel


class Products(BaseModel):
    title : str
    price : float
    link : str