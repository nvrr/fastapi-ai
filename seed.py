# seed.py

from app.config.database import SessionLocal
from app.models.product import Product


def seed_products():
    session = SessionLocal()

    try:
        products = []

        for i in range(1, 101):
            product = Product(
                name=f"Test Product {i}",
                description=f"Dummy Product description {i}",
                is_active=True
            )
            products.append(product)

        session.add_all(products)
        session.commit()

        print("100 campaigns inserted successfully.")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    seed_products()