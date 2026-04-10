import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

import psycopg
from psycopg.rows import dict_row
from psycopg.errors import UniqueViolation

DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "nfc_products"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres"),
}

@dataclass
class Product:
    nfc_tag : str
    name : str
    description : str
    production_date : str
    expiration_date : str
    other_infos : str
    quantity : int = 0
    is_out : int = 0
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    id: Optional[int] = None

def get_connection():
    return psycopg.connect(**DB_CONFIG, row_factory=dict_row)

def init_db():
    '''
    Initializes the database and creates the products table if it doesn't exist.
    '''

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    nfc_tag TEXT UNIQUE NOT NULL,
                    nom TEXT NOT NULL,
                    description TEXT,
                    date_de_fabrication TEXT,
                    date_d_expiration TEXT,
                    autres_infos TEXT,
                    quantite INTEGER DEFAULT 0,
                    sortie INTEGER DEFAULT 0,
                    date_de_creation TEXT NOT NULL,
                    date_de_modification TEXT NOT NULL
                )
            ''')
        connection.commit()
    print("Done\n")

def add_product(product : Product):
    '''
    Adds a new product to the database. If a product with the same NFC tag already exists, it will not be added.
    '''
    now = datetime.now().isoformat()
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO products (
                        nfc_tag, nom, description, date_de_fabrication,
                        date_d_expiration, autres_infos, quantite,
                        sortie, date_de_creation, date_de_modification
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s, %s)
                ''',
                    (product.nfc_tag, product.name, product.description, product.production_date,
                    product.expiration_date, product.other_infos, product.quantity, now, now))
            connection.commit()
        print("Product added\n")

    except UniqueViolation: print("A product with this NFC tag already exist\n")

def get_product(nfc_tag: str) -> Optional[Product]:
    '''
    Retrieves a product from the database by its NFC tag. Returns None if the product is not found.
    '''

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM products WHERE UPPER(nfc_tag) = UPPER(%s)', (nfc_tag,))
            row = cursor.fetchone()
    if row is None:
        return None
    return Product(
        id=row[0],
        nfc_tag=row[1],
        name=row[2],
        description=row[3],
        production_date=row[4],
        expiration_date=row[5],
        other_infos=row[6],
        quantity=row[7],
        is_out=row[8],
        created_at=row[9],
        modified_at=row[10]
    )

def update_quantity(nfc_tag : str, quantity_picked : int) -> bool:
    '''
    Updates the quantity of a product when it is picked. If the product is out of stock after picking,
    it will be marked as such. Returns True if the update was successful, 
    False otherwise.
    '''

    product = get_product(nfc_tag)

    if product is None : 
        print("Product not found\n")
        return False

    if product.is_out == 1:
        print(f"Product {product.name} is OUT OF STOCK.\n")
        return False

    print(f"Product {'found' if product is not None else 'not found'} : ")
    new_quantity = product.quantity - quantity_picked
    if new_quantity < 0:
        print(f"Not enough stock. Avilable : {product.quantity}\n")
        return False

    is_out = 1 if new_quantity == 0 else 0
    now = datetime.now().isoformat()
    print(f"Picking {quantity_picked} from {product.name}...\n")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''UPDATE products
                        SET quantite = %s, sortie = %s, date_de_modification = %s
                        WHERE nfc_tag = %s''', (new_quantity, is_out, now, nfc_tag))
            connection.commit()

    if is_out == 1 :
        print("Stock is now empty, Product marked OUT OF STOCK\n")
    else : 
        print(f"Stock updated. Remaining : {new_quantity}")

    return True

def restock_product(nfc_tag : str, qunatity_added: int) -> bool:
    '''
    Restocks a product by adding the specified quantity to the existing stock.
    If the product was previously marked as out of stock, it will be marked as in stock after restocking.
    Returns True if the update was successful, False otherwise.
    '''

    product = get_product(nfc_tag)

    if product is None : 
        print("Product not found\n")
        return False

    print(f"Product {'found' if product is not None else 'not found'} : ")
    new_quantity = product.quantity + qunatity_added
    now = datetime.now().isoformat()
    print(f"Restocking {qunatity_added} to {product.name}...\n")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute('''UPDATE products
                        SET quantite = %s, sortie = 0, date_de_modification = %s
                        WHERE nfc_tag = %s''',
                        (new_quantity, now, nfc_tag))
            connection.commit()

    print(f"Product restocked. New quantity : {new_quantity}\n")
    return True

def print_product(product: Product):
    '''
    Prints the details of a product in a readable format. If the product is None,
    it will print a message indicating that there is no product to display.
    '''

    if product is None:
        print("No product to display\n")
        return

    stock_status = "OUT OF STOCK" if product.is_out == 1 else "IN STOCK"
    print("\n" + "="*45)
    print(f"NFC Tag : {product.nfc_tag}")
    print(f"Name : {product.name}")
    print(f"Description : {product.description}")
    print(f"Production Date : {product.production_date}")
    print(f"Expiration Date : {product.expiration_date}")
    print(f"Other Infos : {product.other_infos}")
    print(f"Quantity : {product.quantity}")
    print(f"Is Out of Stock : {stock_status}")
    print(f"Created At : {product.created_at}")
    print(f"Modified At : {product.modified_at}")
    print("="*45 + "\n")
