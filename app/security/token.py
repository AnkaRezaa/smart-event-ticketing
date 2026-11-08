import hashlib
import secrets

def generate_qr_token() -> str:
    """
    Generates a cryptographically random, unpredictable token for a ticket QR Code.
    The raw token is encoded in the QR code delivered to the participant.
    """
    return secrets.token_urlsafe(48)

def hash_token(raw_token: str) -> str:
    """
    Computes SHA-256 hash of the ticket token for secure database storage.
    The raw token is never stored in plaintext in the database.
    """
    return hashlib.sha256(raw_token.strip().encode("utf-8")).hexdigest()

