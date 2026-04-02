
_MISSING_READER_WARN_INTERVAL = 10
_missing_reader_count = 0

def read_nfc_tag():
    '''
    Scans for readers and waits for a card to be placed.
    Returns the UID string, "WAITING" if no card is present, or None if no reader is found.
    '''
    global _missing_reader_count