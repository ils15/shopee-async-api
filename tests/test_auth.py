import pytest
from shopee_async_api.auth import generate_shopee_signature

def test_signature_generation_matches_docs():
    """
    Tests if the generated signature perfectly matches the example provided
    in the Shopee Affiliate Open API documentation.
    
    Docs Example:
    Hypothesis AppId=123456, Secret=demo,
    Timestamp=1577836800,
    Payload={"query":"{\\nbrandOffer{\\n    nodes{\\n        commissionRate\\n        offerName\\n    }\\n}\\n}"}
    Result should be dc88d72feea70c80c52c3399751a7d34966763f51a7f056aa070a5e9df645412
    """
    app_id = "123456"
    secret = "demo"
    timestamp = 1577836800
    payload = '{"query":"{\\nbrandOffer{\\n    nodes{\\n        commissionRate\\n        offerName\\n    }\\n}\\n}"}'
    
    expected_signature = "dc88d72feea70c80c52c3399751a7d34966763f51a7f056aa070a5e9df645412"
    
    signature = generate_shopee_signature(
        app_id=app_id,
        secret=secret,
        payload=payload,
        timestamp=timestamp
    )
    
    assert signature == expected_signature
