from hashlib import sha256

def bitcoin_sha256(input_data):
    """
    Performs Bitcoin's double SHA256 hash
    Accepts either bytes or string input
    """
    # Convert string to bytes if necessary
    if isinstance(input_data, str):
        # Check if it's a hex string
        if all(c in '0123456789abcdefABCDEF' for c in input_data):
            # Convert hex string to bytes
            data = bytes.fromhex(input_data)
        else:
            # Convert normal string to bytes
            data = input_data.encode('utf-8')
    elif isinstance(input_data, bytes):
        data = input_data
    else:
        raise TypeError("Input must be string or bytes")
    
    # Perform double SHA256
    first_hash = sha256(data).digest()
    second_hash = sha256(first_hash).digest()
    return second_hash.hex()

# Test with different inputs
print("String input:", bitcoin_sha256("Hello World"))
print("Hex string input:", bitcoin_sha256("48656c6c6f20576f726c64"))  # "Hello World" in hex
print("Bytes input:", bitcoin_sha256(b"Hello World"))