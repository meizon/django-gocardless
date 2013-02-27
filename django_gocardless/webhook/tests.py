from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from .models import GoCardlessWebhook, GoCardlessWebhookItem

BILL_JSON_PAID = """
{
    "payload": {
        "resource_type": "bill",
        "action": "paid",
        "bills": [
            {
                "id": "AKJ398H8KA",
                "status": "paid",
                "source_type": "subscription",
                "source_id": "KKJ398H8K8",
                "amount": "20.0",
                "amount_minus_fees": "19.8",
                "paid_at": "2011-12-01T12:00:00Z",
                "uri": "https://gocardless.com/api/v1/bills/AKJ398H8KA"
            },
            {
                "id": "AKJ398H8KB",
                "status": "paid",
                "source_type": "subscription",
                "source_id": "8AKJ398H78",
                "amount": "20.0",
                "amount_minus_fees": "19.8",
                "paid_at": "2011-12-09T12:00:00Z",
                "uri": "https://gocardless.com/api/v1/bills/AKJ398H8KB"
            }
        ],
        "signature": "f6b9e6cd8eef30c444da48370e646839c9bb9e1cf10ea16164d5cf93a50231eb"
    }
}
"""

BILL_JSON_PENDING = """
{
    "payload": {
        "resource_type": "bill",
        "action": "created",
        "bills": [
            {
                "id": "AKJ398H8KA",
                "status": "pending",
                "source_type": "subscription",
                "source_id": "KKJ398H8K8",
                "amount": "20.0",
                "amount_minus_fees": "19.8",
                "paid_at": "2011-12-01T12:00:00Z",
                "uri": "https://gocardless.com/api/v1/bills/AKJ398H8KA"
            },
            {
                "id": "AKJ398H8KB",
                "status": "pending",
                "source_type": "subscription",
                "source_id": "8AKJ398H78",
                "amount": "20.0",
                "amount_minus_fees": "19.8",
                "paid_at": "2011-12-09T12:00:00Z",
                "uri": "https://gocardless.com/api/v1/bills/AKJ398H8KB"
            }
        ],
        "signature": "f6b9e6cd8eef30c444da48370e646839c9bb9e1cf10ea16164d5cf93a50231eb"
    }
}
"""

SUBSCRIPTION_JSON = """
{
  "payload": {
    "resource_type": "subscription",
    "action": "cancelled",
    "subscriptions": [{
      "id": "AKJ398H8KBO122A",
      "status": "cancelled",
      "uri": "https://gocardless.com/api/v1/subscriptions/AKJ398H8KBO122A"
    },{
      "id": "BBJ398H8KBO122A",
      "status": "cancelled",
      "uri": "https://gocardless.com/api/v1/subscriptions/BBJ398H8KBO122A"
    }],
    "signature": "f6b9e6cd8eef30c444da48370e646839c9bb9e1cf10ea16164d5cf93a50231eb"
  }
}

"""

PRE_AUTH_JSON_CANCELLED = """
{
  "payload": {
    "resource_type": "pre_authorization",
    "action": "cancelled",
    "pre_authorizations": [{
      "id": "AKJ398H8KBOOO3",
      "status": "cancelled",
      "uri": "https://gocardless.com/api/v1/pre_authorizations/AKJ398H8KBOOO3"
    }, {
      "id": "AKJ398H8KBOOOA",
      "status": "cancelled",
      "uri": "https://gocardless.com/api/v1/pre_authorizations/AKJ398H8KBOOOA"
    }],
    "signature": "ac57eb070b684f75686c49d058cb0c0ed13162b5f5bd695eb2a8fedefeb69185"
  }
}
"""


class WebhookTests(TestCase):

    @override_settings(GOCARDLESS_APP_SECRET='BOGUS')
    def test_request_bill_paid(self):

        self.client.post(
            reverse('gocardless_webhook'), BILL_JSON_PAID,
            content_type='application/javascript')

        # item should be flagged
        self.assertEqual(
            'Signature did not validate',
            GoCardlessWebhook.objects.all()[0].flag)

        # should produce two paid bills
        self.assertEqual(2, GoCardlessWebhookItem.objects.count())

    def test_request_pre_auth_cancelled(self):

        self.client.post(
            reverse('gocardless_webhook'), PRE_AUTH_JSON_CANCELLED,
            content_type='application/javascript')

        # item should not be flagged
        self.assertEqual(
            None,
            GoCardlessWebhook.objects.all()[0].flag)

        # should produce two paid bills
        self.assertEqual(2, GoCardlessWebhookItem.objects.count())
