from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException
from database import get_product, print_product, restock_product, update_quantity, add_product, Product

GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]

def read_nfc_tag():
    '''
    Scans for an NFC tag and returns its UID as a string. If no tag is present, it returns "WAITING".
    '''

    try:
        available_readers = readers()
        if not available_readers:
            print("No NFC reader found. Please connect a reader and try again.")
            return None
        
        reader = available_readers[0]
        print(f"Using NFC reader: {reader}")

        connection = reader.createConnection()
        connection.connect()
        print("NFC reader connected. Waiting for a tag...")

        data, sw1, sw2 = connection.transmit(GET_UID)
        if sw1 == 0x90 and sw2 == 0x00:
            uid = toHexString(data)
            print(f"NFC tag UID read: {uid}")
            return uid
        else:
            print(f"Failed to read NFC tag. SW1: {sw1}, SW2: {sw2}")
            return None

    except NoCardException:
        print("WAITING")
        return None
    except CardConnectionException as e:
        print(f"Error connecting to NFC reader: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def handle_nfc_interaction(nfc_tag: str):
    '''
    Business logic : when a tag is detected, it checks if the product exists in the database, otherwise offer to add it.
    '''

    print(f"Checking for product with NFC tag: {nfc_tag}")
    product = get_product(nfc_tag)

    if product:
        print("Tag detected! Product already exists in database.")
        print_product(product)

        choice = input("Do you want to update quantity (press u) or restock product (press r) ? Press Enter to skip.\n").strip().lower()
        if choice == 'u':
            try:
                quantity = int(input("Enter quantity to pick : "))
                update_quantity(nfc_tag, quantity)
            except ValueError:
                print("Invalid quantity. Please enter a number.\n")
        elif choice == 'r':
            try:
                quantity = int(input("Enter quantity to restock : "))
                restock_product(nfc_tag, quantity)
            except ValueError:
                print("Invalid quantity. Please enter a number.\n")
    else:
        print("Tag detected! Product does not exist in database.")
        choice = input("Do you want to add this product to the database ? (y/n)\n").strip().lower()

        if choice == 'y':
            print("Please enter product details : ")
            name = input("Enter product name : ")
            description = input("Enter product description : ")
            production_date = input("Enter production date (YYYY-MM-DD) : ")
            expiration_date = input("Enter expiration date (YYYY-MM-DD) : ")
            other_infos = input("Enter other infos (optional) : ")

            try:
                qty = int(input("Enter quantity : "))
            except ValueError:
                print("Invalid quantity. Please enter a number.\n")
                qty = 0

            new_product = Product(
                nfc_tag=nfc_tag,
                name=name,
                description=description,
                production_date=production_date,
                expiration_date=expiration_date,
                other_infos=other_infos,
                quantity=qty
            )
            add_product(new_product)
            print_product(get_product(nfc_tag))

        else:
            print("Registration cancelled.\n")
