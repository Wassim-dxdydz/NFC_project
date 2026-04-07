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
from django.db import models
from stock.models import StockItem

class StockItemNFCTag(models.Model):
    """"""
    Extends StockItem with a dedicated NFC UID field.
    Separate from barcode_data so both can coexist on the same item.
    """
"""
    stock_item = models.OneToOneField(
        StockItem,
        on_delete=models.CASCADE,
        related_name='nfc_tag'
        )

    uid = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        null=True,
        verbose_name="NFC Tag UID"
    )

    class Meta:
        app_label = 'nfc_inventree'

    def __str__(self):
        return f"NFC:{self.uid} -> {self.stock_item}"

from plugin import InvenTreePlugin
from plugin.mixins import BarcodeMixin, SettingsMixin

class NFCDrugPlugin(BarcodeMixin, SettingsMixin, InvenTreePlugin):
    NAME = "NFCDrugPlugin"
    SLUG = "nfc-drug"
    TITLE = "NFS Drug Plugin"
    VERSION = "0.1.0"
    AUTHOR = "ABAHRI Wassim"
    DESCRIPTION = "Plugin for NFC Drug management"
    EXTRA_INSTALLED_APPS = ['nfc_inventree']
    SETTINGS = {
        "READER_TIMEOUT": {
            "name": "Reader Timeout",
            "description": "Seconds to wait for a tag before giving up",
            "default": 30,
            "validator": int,
        }
    }

    def scan(self, barcode_data):
        """"""
        Called when POST /api/barcode/ receives data.
        Looks up StockItem via the dedicated nfc_tag.uid column.
        Returns match dict if found, None if not. 
        """"""

        from stock.models import StockItem

        uid = str(barcode_data).strip().lower()

        try:
            item =  StockItem.objects.get(barcode_data=uid)
            return {
                StockItem.barcode_model_type():{
                    "pk": item.pk,
                    "api_url": f"/api/stock/{item.pk}/",
                    "web_url": f"/stock/item/{item.pk}/",
                }
            }
        except StockItem.DoesNotExist:
            return None

"""