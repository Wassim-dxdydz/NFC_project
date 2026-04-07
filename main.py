import logging
from database import Product, init_db, add_product, get_product, update_quantity, restock_product, print_product
from nfc_reader_writer import handle_nfc_interaction, read_nfc_tag
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

    start_time = time.time()
    SCAN_TIMEOUT = 30

    try:
        while True:
            if time.time() - start_time > SCAN_TIMEOUT:
                log.info("No tag detected in 30s. Exiting")
                break

            result = read_nfc_tag()

            if result and result != "WAITING":
                log.info(f"New NFC tag detected: {result}\n")
                handle_nfc_interaction(result)
                log.info("\nDone, Restart to scan another tag.\n")
                break

            time.sleep(1)

    except KeyboardInterrupt:
        log.info("\nNFC reader stopped.")

"""
wassim@debian:~/inventree$ docker compose exec inventree-server bash
root@117c105f9e44:/home/inventree# cd /home/inventree/src/backend/InvenTree
root@117c105f9e44:/home/inventree/src/backend/InvenTree# python manage.py makemigrations nfc_plugin
INVE-W3: Could not detect git information.
2026-04-07T14:55:38.813605Z [warning  ] Cannot set global setting "_MAINTENANCE_MODE" - database is not accessible [inventree]
2026-04-07 14:55:38,813 WARNING {'event': 'Cannot set global setting "_MAINTENANCE_MODE" - database is not accessible', 'timestamp': '2026-04-07T14:55:38.813605Z', 'logger': 'inventree', 'level': 'warning'}
No installed app with label 'nfc_plugin'.
""" 

"""
[metadata]
name = nfc-plugin
version = 0.1.0
description = NFC Drug Plugin for InvenTree
author = ABAHRI Wassim

[options]
py_modules = nfc_plugin
install_requires = InvenTree
"""