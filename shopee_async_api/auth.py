import hashlib
import time

def generate_shopee_signature(app_id: str, secret: str, payload: str, timestamp: int = None) -> str:
    """
    Generates the SHA256 signature for Shopee Affiliate Open API requests.
    
    Calculation method: SHA256(Credential + Timestamp + Payload + Secret)
    """
    if timestamp is None:
        timestamp = int(time.time())
        
    factor = f"{app_id}{timestamp}{payload}{secret}"
    signature = hashlib.sha256(factor.encode('utf-8')).hexdigest()
    return signature

def get_auth_headers(app_id: str, secret: str, payload: str) -> dict:
    """
    Creates the Authorization headers required by Shopee.
    """
    timestamp = int(time.time())
    signature = generate_shopee_signature(
        app_id=app_id, 
        secret=secret, 
        payload=payload, 
        timestamp=timestamp
    )
    
    auth_header = f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}"
    return {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
