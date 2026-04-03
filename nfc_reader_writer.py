
from datetime import datetime
from select import select
import sys

from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException
from logging import log

GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
_MISSING_READER_WARN_INTERVAL = 10
_missing_reader_count = 0

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
    Prompts the user for input with a timeout (Linux/MacOs only).
    Returns empty string if the user doesn't respond in time.
    FAils back to regular imput() on Windows.
    '''

    print(prompt, end='', flush=True)
    if sys.platform.startswith('win'):
        return input().strip().lower()
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().strip().lower()
    else:
        print("\nInput timed out.")
        return ""

def parse_data(prompt: str) -> str:
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

