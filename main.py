from fastapi import FastAPI
from models import Product

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

products = []

@app.post("/products")
def add_product(product: Product):
    products.append(product)
    return {"message": "Product added"}

@app.get("/products")
def get_products():
    return products

