from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException, CardConnectionException

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
