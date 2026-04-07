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
from plugin import InvenTreePlugin
from plugin.mixins import BarcodeMixin, SettingsMixin, AppMixin

class NFCDrugPlugin(AppMixin, BarcodeMixin, SettingsMixin, InvenTreePlugin):
    NAME = "NFCDrugPlugin"
    SLUG = "nfc-drug"
    TITLE = "NFC Drug Plugin"
    VERSION = "0.1.0"
    AUTHOR = "ABAHRI Wassim"
    DESCRIPTION = "Plugin for NFC Drug management"
    SETTINGS = {
        "READER_TIMEOUT": {
            "name": "Reader Timeout",
            "description": "Seconds to wait for a tag before giving up",
            "default": 30,
            "validator": int,
        }
    }

    def scan(self, barcode_data):
        """
        Called when POST /api/barcode/ receives data.
        Looks up StockItem via the dedicated nfc_tag.uid column.
        Returns match dict if found, None if not. 
        """

        from nfc_plugin.models import StockItemNFCTag
        from stock.models import StockItem

        uid = str(barcode_data).strip().upper()

        try:
            nfc = StockItemNFCTag.objects.get(uid=uid)
            item =  nfc.stock_item
            return {
                StockItem.barcode_model_type():{
                    "pk": item.pk,
                    "api_url": f"/api/stock/{item.pk}/",
                    "web_url": f"/stock/item/{item.pk}/",
                }
            }
        except StockItemNFCTag.DoesNotExist:
            return None
"""