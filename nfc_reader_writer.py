from datetime import datetime
from select import select
import queue
import threading
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException
import logging
from database import Product, add_product, get_product, print_product, restock_product, update_quantity

GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
_MISSING_READER_WARN_INTERVAL = 10
_missing_reader_count = 0
log = logging.getLogger(__name__)

def read_nfc_tag():
    '''
    Scans for readers and waits for a card to be placed.
    Returns the UID string, "WAITING" if no card is present, or None if no reader is found.
    '''

    global _missing_reader_count

    try:
        available_readers = readers()
        if not available_readers:
            _missing_reader_count += 1
            # Log an error every _MISSING_READER_WARN_INTERVAL attempts to avoid spamming the logs
            if _missing_reader_count == 1 or _missing_reader_count % _MISSING_READER_WARN_INTERVAL == 0:
                log.error("No NFC reader found. Please connect a reader and try again.")
            return None

        # Reset the missing reader count if a reader is found
        if _missing_reader_count > 0:
            log.info(f"NFC reader detected after {_missing_reader_count} attempts.")
            _missing_reader_count = 0

        # For simplicity, we use the first available reader. We could enhance this to allow selecting among multiple readers if needed.
        reader = available_readers[0]
        log.debug(f"Using NFC reader: {reader}")

        connection = reader.createConnection()
        connection.connect()

        # Log the connection status at debug level to avoid cluttering the logs during normal operation
        data, sw1, sw2 = connection.transmit(GET_UID)
        log.debug(f"Data received: {toHexString(data)}, SW1: {sw1}, SW2: {sw2}")
        # Check the status words to determine if the UID was read successfully
        if sw1 == 0x90 and sw2 == 0x00:
            uid = toHexString(data).replace(" ", "").upper()  # Format the UID as a continuous uppercase string
            log.info(f"NFC tag UID read: {uid}")
            return uid
        else:
            log.warning(f"Failed to read NFC tag. SW1: {hex(sw1)}, SW2: {hex(sw2)}")
            return None

    # Handle specific exceptions for better logging and control flow
    except NoCardException:
        log.debug("No card present. Waiting...")
        return "WAITING"
    except CardConnectionException as e:
        log.error(f"Error connecting to NFC reader: {e}")
        return None
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")
        return None

def input_with_timeout(prompt: str, timeout: int = 30) -> str:
    '''
    Prompts the user for input with a timeout.
    Cross-platform: works on Windows, Linux, and macOS.
    Returns the user input, or empty string if the timeout is reached.
    '''

    q = queue.Queue()

    def read_input():
        try:
            q.put(input(prompt))
        except EOFError:
            q.put("")

    thread = threading.Thread(target=read_input, daemon=True)
    thread.start()

    try:
        result = q.get(timeout=timeout)
        return result.strip().lower()
    except queue.Empty:
        print(f"No response after {timeout}s. Sleeping...")
        thread.join(0)
        return 

def parse_date(prompt: str) -> str:
    '''
    Prompts the user for a date in YYYY-MM-DD format, retrying untill valid.
    '''

    while True:
        val = input(prompt).strip()
        try:
            datetime.strptime(val, "%Y-%m-%d")
            return val
        except ValueError:
            print("Invalid date format. Please enter a date in YYYY-MM-DD format.\n")

def parse_int(prompt: str) -> int:
    '''
    Prompts the user for an integer, retrying until valid.
    '''

    while True:
        val = input(prompt).strip()
        try:
            return int(val)
        except ValueError:
            print("Invalid input. Please enter a valid integer.\n")

def handle_nfc_interaction(nfc_tag: str):
    '''
    Business logic: check if tax exists in the database , otherwise offer registration.
    '''

    print(f"\nChecking Tag : {nfc_tag} ...\n")
    product = get_product(nfc_tag)

    if product:
        print("This NFC tag already exists in the database\n")
        print_product(product)

        choice = input_with_timeout(
            "Do you want to Update quantity (Press u) or Restock quantity (Press r) ? (Press Enter to skip):\n", timeout=30
        )

        if choice == "u":
            qty = parse_int("How many to remove ? :\n")
            update_quantity(nfc_tag, qty)
            print_product(get_product(nfc_tag))
        elif choice == "r":
            qty = parse_int("How many to add ? :\n")
            restock_product(nfc_tag, qty)
            print_product(get_product(nfc_tag))

    else:
        print("This NFC is unknown")
        choice = input_with_timeout(
            "Do you want to add this product to the database ? (y/n)\n", timeout=30
        )

        if choice == "y":
            print("Please enter product details : ")
            name = input("Enter product name : ")
            description = input("Enter product description : ")
            production_date = parse_date("Enter production date (YYYY-MM-DD) : ")
            expiration_date = parse_date("Enter expiration date (YYYY-MM-DD) : ")
            other_infos = input("Enter other infos (optional) : ")
            qty = parse_int("Enter quantity : ")

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
            print_product(new_product)

        else:
            print("Registration cancelled.\n")
