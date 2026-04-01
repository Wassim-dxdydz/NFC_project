import sqlite3
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

DB_NAME = "nfc_products.db"

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

def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        )'''
    )
    connection.commit()
    connection.close()
    print("Done\n")


def add_product(product : Product):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    now = datetime.now().isoformat()
    try:
        cursor.execute('''
            INSERT INTO products (nfc_tag, nom, description, date_de_fabrication, date_d_expiration,
            autres_infos, quantite, sortie, date_de_creation, date_de_modification)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)''',
            (product.nfc_tag, product.name, product.description, product.production_date,
             product.expiration_date, product.other_infos, product.quantity, now, now))
        
        connection.commit()
        print("Produit ajouté\n")

    except sqlite3.IntegrityError: print(" Un produit avec cet NFC tag existe déja\n")
    finally:
        connection.close()


def get_product(nfc_tag: str) -> Optional[Product]:
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products WHERE nfc_tag = ?', (nfc_tag,))
    row = cursor.fetchone()
    connection.close()
    if row is None:
        print("Il n y a aucun produit avec cet NFC tag, veuillez-vous le rajouter ?\nRésultat :")
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
    product = get_product(nfc_tag)
    
    if product is None : 
        print("Produit introuvable.\n")
        return False
    
    if product.is_out == 1:
        print("Produit en rupture de stock.\n")
        return False
    
    new_quantity = product.quantity - quantity_picked
    if new_quantity < 0:
        print(f"Stock insuffisant : Il reste {product.quantity}\n")
        return False
    
    is_out = 1 if new_quantity == 0 else 0
    now = datetime.now().isoformat()

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute('''UPDATE products
                   SET quantite = ?, sortie = ?, date_de_modification = ?
                   WHERE nfc_tag = ?''', (new_quantity, is_out, now, nfc_tag))
    connection.commit()
    connection.close()

    if is_out == 1 :
        print("Stock vide, nécessité de restocker\n")
    else : 
        print(f"Srock modifié : Il reste {product.quantity}")
    
    return True
