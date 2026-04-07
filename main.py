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
2026-04-07 14:11:19 - INFO - Starting NFC reader : Please place a tag on the reader ...

2026-04-07 14:11:25 - INFO - NFC tag UID read: 047037BA591D90
2026-04-07 14:11:26 - INFO - New NFC tag detected: 047037BA591D90


Checking Tag : 047037BA591D90 ...

This NFC is unknown
Do you want to add this product to the database ? (y/n)
Traceback (most recent call last):
  File "/home/wassim/nfc_project/nfc_reader_writer.py", line 88, in input_with_timeout
    result = q.get(timeout=timeout)
  File "/usr/lib/python3.13/queue.py", line 212, in get
    raise Empty
_queue.Empty

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/wassim/nfc_project/main.py", line 55, in <module>
    handle_nfc_interaction(result)
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^
  File "/home/wassim/nfc_project/nfc_reader_writer.py", line 147, in handle_nfc_interaction
    choice = input_with_timeout(
        "Do you want to add this product to the database ? (y/n)\n", timeout=30
    )
  File "/home/wassim/nfc_project/nfc_reader_writer.py", line 90, in input_with_timeout
    except queue.Empty():
    ...<2 lines>...
        return
TypeError: catching classes that do not inherit from BaseException is not allowed
"""