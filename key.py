from hashlib import sha256
import hashlib
import hmac
import ecdsa
import base58

# Rest of your code follows...

# Regular Private to Public Key Generation
def private_to_public(private_key_hex):
    """Convert a private key to its corresponding public key using ECDSA"""
    # Create signing key
    signing_key = ecdsa.SigningKey.from_string(
        bytes.fromhex(private_key_hex),
        curve=ecdsa.SECP256k1
    )
    
    # Get verifying key (public key)
    verifying_key = signing_key.get_verifying_key()
    
    # Get public key in compressed format
    public_key_bytes = verifying_key.to_string("compressed")
    return public_key_bytes.hex()

# HD Wallet Key Derivation
def hmac_sha512(key, data):
    """Create a HMAC using SHA512"""
    hmac_obj = hmac.new(key, data, hashlib.sha512)
    return hmac_obj.digest()

def derive_child_public_key(parent_public_key_hex, parent_chain_code_hex, index):
    """
    Derive a child public key from a parent public key (xpub derivation)
    Only works for normal (non-hardened) child keys
    """
    # Convert hex strings to bytes
    parent_public_key = bytes.fromhex(parent_public_key_hex)
    chain_code = bytes.fromhex(parent_chain_code_hex)
    
    # Structure the data for HMAC
    # For public parent -> public child, data = parent_pubkey || index
    data = parent_public_key + index.to_bytes(4, 'big')
    
    # Calculate HMAC-SHA512
    hmac_data = hmac_sha512(chain_code, data)
    
    # Split into left and right portions
    left_32_bytes = hmac_data[:32]  # Used for key
    right_32_bytes = hmac_data[32:] # New chain code
    
    # Create point on curve from parent public key
    curve = ecdsa.SECP256k1
    point = ecdsa.VerifyingKey.from_string(
        parent_public_key[1:],
        curve=curve
    ).pubkey.point
    
    # Create new key point
    left_int = int.from_bytes(left_32_bytes, 'big')
    G = curve.generator
    new_point = point + (left_int * G)
    
    # Convert new point to compressed public key format
    public_key = b'\x02' if new_point.y() % 2 == 0 else b'\x03'
    public_key += new_point.x().to_bytes(32, 'big')
    
    return {
        'child_public_key': public_key.hex(),
        'chain_code': right_32_bytes.hex()
    }

# Example usage for standard private -> public derivation
def example_private_to_public():
    # Example private key (32 bytes)
    private_key = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    public_key = private_to_public(private_key)
    return public_key

# Example usage for xpub child derivation
def example_xpub_derivation():
    # Example parent public key and chain code
    parent_public_key = "0279BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798"
    chain_code = "873DFF81C02F525623FD1FE5167EAC3A55A049DE3D314BB42EE227FFED37D508"
    
    # Derive child key at index 0
    child = derive_child_public_key(parent_public_key, chain_code, 0)
    return child