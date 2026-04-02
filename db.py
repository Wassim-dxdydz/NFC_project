
from contextlib import contextmanager
import datetime
from logging import log
import sqlite3
from database import Product

DB_NAME = "nfc_products.db"

@contextmanager
def _get_connection():
    '''
    Context manager for database connection. It ensures that the connection is properly closed after use.
    '''

    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

def init_db():
    '''
    Initializes the database and creates the products table if it doesn't exist.
    '''

    with _get_connection() as connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nfc_tag TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                production_date TEXT,
                expiration_date TEXT,
                other_infos TEXT,
                quantity INTEGER DEFAULT 0,
                is_out INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL
            )'''
        )

    log.info("Database initialized.\n")

def add_product(product : Product):
    '''
    Adds a new product to the database.
    If a product with the same NFC tag already exists, it will not be added.
    '''

    now = datetime.now().isoformat()
    try:
        with _get_connection() as connection:
            connection.execute('''
                INSERT INTO products (nfc_tag, name, description, production_date, expiration_date,
                other_infos, quantity, is_out, created_at, modified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)''',
                (product.nfc_tag, product.name, product.description, product.production_date,
                 product.expiration_date, product.other_infos, product.quantity, now, now)
            )
        log.info("Product added.\n")
    except sqlite3.IntegrityError:
        log.warning("A product with this NFC tag already exists.\n")

def get_product(nfc_tag: str) -> Product:
    '''
    Retrieves a product from the database by its NFC tag.
    Returns a Product object if found, otherwise returns None.
    '''

    with _get_connection() as connection:
        row =  connection.execute('SELECT * FROM products WHERE nfc_tag = ?', (nfc_tag,)).fetchone()

    if row is None:
        return None

    return Product(
        nfc_tag=row['nfc_tag'],
        name=row['name'],
        description=row['description'],
        production_date=row['production_date'],
        expiration_date=row['expiration_date'],
        other_infos=row['other_infos'],
        quantity=row['quantity'],
        is_out=row['is_out']
    )

def update_quantity(nfc_tag: str, quantity: int):
    '''
    UPdates the quantity of a product when it is picked.
    If the product reaches 0 stock, it is marked as out of stock.
    Returns True if the update was successful, False otherwise.
    '''

    Product = get_product(nfc_tag)

    if Product is None:
        log.warning("Product not found.\n")
        return False

    if Product.is_out == 1:
        log.warning(f"Product '{Product.name}' is out of stock.\n")
        return False

    log.info(f"Product found : {Product.name}")
    new_quantity = Product.quantity - quantity

    if new_quantity < 0:
        log.warning(f"Not enough stock. Available : {Product.quantity}\n")
        return False

    is_out = 1 if new_quantity == 0 else 0
    now = datetime.now().isoformat()
    log.info(f"Picking {quantity} from '{Product.name}'...\n")

    with _get_connection() as connection:
        connection.execute('''
            UPDATE products
            SET quantity = ?, is_out = ?, modified_at = ?
            WHERE nfc_tag = ?''',
            (new_quantity, is_out, now, nfc_tag)
        )

    if is_out == 1:
        log.info(f"Stock is now empty. Product '{Product.name}' is marked as out of stock.\n")
    else :
        log.info(f"Stock updated. Remaining : {new_quantity}.\n")
    return True

def restock_product(nfc_tag: str, quantity: int) -> bool:
    '''
    Restocks a product by adding the specified quantity to the existing stock.
    If the product was previously marked as out of stock, it will be marked as in stock after restocking.
    Returns True if the update was successful, False otherwise.
    '''

    product = get_product(nfc_tag)

    if product is None:
        log.warning("Product not found.\n")
        return False
    
    log.info(f"Product found : {product.name}")
    new_quantity = product.quantity + quantity
    now = datetime.now().isoformat()
    log.info(f"Restocking {quantity} units to '{product.name}'...\n")

    with _get_connection() as connection:
        connection.execute('''
            UPDATE products
            SET quantity = ?, is_out = 0, modified_at = ?
            WHERE nfc_tag = ?''',
            (new_quantity, now, nfc_tag)
        )
    
    log.info(f"Product restocked. New quantity : {new_quantity}.\n")
    return True
