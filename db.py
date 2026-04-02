
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
