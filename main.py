from database import Product, init_db, add_product, get_product, update_quantity, restock_product, print_product
from nfc_reader import read_nfc_tag
import time

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
    print_product(p)

    update_quantity("TEST001",10)
    print_product(get_product("TEST001"))

    restock_product("TEST001", 15)
    print_product(get_product("TEST001"))    

    print_product(get_product("GTEST001"))

if __name__ == "__main__":
    last_uid = None

    while True:
        result = read_nfc_tag()
        if result and result != "WAITING":
            if result != last_uid:
                print(f"New NFC tag detected: {result}\n")
                last_uid = result
        elif result is None:
            time.sleep(2)
        time.sleep(1)