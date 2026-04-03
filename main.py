import logging
from database import Product, init_db, add_product, get_product, update_quantity, restock_product, print_product
from nfc_reader import handle_nfc_interaction, read_nfc_tag
import time


log = logging.getLogger(__name__)

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
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    init_db()
    log.info("Starting NFC reader : Please place a tag on the reader ...\n")

    last_uid = None

    try:
        while True:
            result = read_nfc_tag()

            if result and result != "WAITING":
                if result != last_uid:
                    logging.info(f"New NFC tag detected: {result}\n")
                    last_uid = result
                    handle_nfc_interaction(result)
                    logging.info("\nWaiting for next NFC tag...\n")
            elif result is None:
                time.sleep(2) # C'est pour éviter '''UN PEU''' de spammer la console avec Waiting, on peut ajuster ce délai selon les besoins

            if result == "WAITING":
                last_uid = None # Réinitialiser last_uid quand la carte est retirée, cela permet de retapper la même carte.

            time.sleep(1) # Minimiser l'utilisation du CPU

    except KeyboardInterrupt:
        logging.info("\nNFC reader stopped.")


"""    init_db()
    last_uid = None

    try:
        while True:
            result = read_nfc_tag()
            if result and result != "WAITING":
                if result != last_uid:
                    print(f"New NFC tag detected: {result}\n")
                    last_uid = result
                    handle_nfc_interaction(result)
                    print("\nWaiting for next NFC tag...\n")
            elif result is None:
                time.sleep(2) # C'est pour éviter '''UN PEU''' de spammer la console avec Waiting, on peut ajuster ce délai selon les besoins
            
            if result == "WAITING":
                last_uid = None # Réinitialiser last_uid quand la carte est retirée, cela permet de retapper la même carte.
            time.sleep(1) # Minimiser l'utilisation du CPU
    except KeyboardInterrupt:
        print("\nExiting program.")"""


"""if __name__ == "__main__":
    last_uid = None

    while True:
        result = read_nfc_tag()
        if result and result != "WAITING":
            if result != last_uid:
                print(f"New NFC tag detected: {result}\n")
                last_uid = result
        elif result is None:
            time.sleep(2) # C'est pour éviter '''UN PEU''' de spammer la console avec Waiting, on peut ajuster ce délai selon les besoins
        time.sleep(1) # Ceci est pour minimiser l'utilisation du CPU, on peut aussi ajuster ce délai selon les besoins"""
