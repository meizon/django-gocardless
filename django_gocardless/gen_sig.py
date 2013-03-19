import json
from gocardless.utils import generate_signature

GOCARDLESS_APP_SECRET = (
    'BBYKKNKEK4WKN9YVK0BRARGS4QHDRVJB'
    '8JWYM84XTR9XQ591RGFSEFQ82B0ZKKYM')

js = """
{
    "payload": {
        "resource_type": "bill",
        "action": "refunded",
        "bills": [
            {
                "id": "AKJ398H8KA",
                "status": "refunded",
                "source_type": "subscription",
                "source_id": "KKJ398H8K8",
                "amount": "20.0",
                "amount_minus_fees": "19.8",
                "paid_at": "2011-12-01T12:00:00Z",
                "uri": "https://gocardless.com/api/v1/bills/AKJ398H8KA"
            }
        ],
        "signature": "7b2bc20d10ef8322e580205fea0056524e22a862f90ffdd14ab069affd680f3e"
    }
}
"""

payload = json.loads(js)['payload']

pms = payload.copy()
pms.pop('signature')
print generate_signature(pms, GOCARDLESS_APP_SECRET)
