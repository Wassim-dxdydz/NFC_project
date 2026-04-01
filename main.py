from database import Product, init_db, add_product, get_product

def test():
    init_db()

    p = Product(
        nfc_tag="TEST001",
        name="Test",
        description="test de l'ajout d'un produit",
        production_date="2026-03-31",
        expiration_date="2028-03-31",
        other_infos="Lot: A123",
        quantity=10
    )

    add_product(p)
    print(get_product("TEST001"))

    print(get_product("TEST001"))

    print(get_product("GTEST001"))

if __name__ == "__main__":
    test()