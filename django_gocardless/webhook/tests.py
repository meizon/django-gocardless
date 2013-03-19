from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from .models import Payload

BILL_JSON_CREATED = """
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
            }
        ],
        "signature": "35fc26a0f49b298a4814c94e7e7b93c33d3b490e1fd02baecabacf4425f684a2"
    }
}
"""

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
        "signature": "f9daa60fa7e230df5051f8ce0c0333d50c6527f29b36d7efd582da5e79c42be6"
    }
}
"""

BILL_JSON_WITHDRAWN = """
{
    "payload": {
        "resource_type": "bill",
        "action": "withdrawn",
        "bills": [
            {
                "id": "AKJ398H8KA",
                "status": "withdrawn",
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

BILL_JSON_FAILED = """
{
    "payload": {
        "resource_type": "bill",
        "action": "failed",
        "bills": [
            {
                "id": "AKJ398H8KA",
                "status": "failed",
                "source_type": "subscription",
                "source_id": "KKJ398H8K8",
                "amount": "20.0",
                "amount_minus_fees": "19.8",
                "paid_at": "2011-12-01T12:00:00Z",
                "uri": "https://gocardless.com/api/v1/bills/AKJ398H8KA"
            }
        ],
        "signature": "68bd124264d64605b2eaa1d361497793214ce6da3c56d066d2a4585cfbbd16b5"
    }
}
"""

BILL_JSON_REFUNDED = """
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
        "signature": "4acba279d3ade5b310f86cc4c09cfefd034a9d77b1173044a89a930159b92682"
    }
}
"""

SUBSCRIPTION_JSON_CANCELLED = """
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
    "signature": "99510c2d41a33e13f7033a23fb0d86a2da0dcfbdb730cbae09839a9c5db92d06"
  }
}

"""

SUBSCRIPTION_JSON_EXPIRED = """
{
  "payload": {
    "resource_type": "subscription",
    "action": "expired",
    "subscriptions": [{
      "id": "AKJ398H8KBO122A",
      "status": "expired",
      "uri": "https://gocardless.com/api/v1/subscriptions/AKJ398H8KBO122A"
    }],
    "signature": "6b0864045b2e3a847c26d738d2d617633a0fec6ae40775e52864573651ef475e"
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

PRE_AUTH_JSON_EXPIRED = """
{
  "payload": {
    "resource_type": "pre_authorization",
    "action": "expired",
    "pre_authorizations": [{
      "id": "AKJ398H8KBOOO3",
      "status": "expired",
      "uri": "https://gocardless.com/api/v1/pre_authorizations/AKJ398H8KBOOO3"
    }, {
      "id": "AKJ398H8KBOOOA",
      "status": "expired",
      "uri": "https://gocardless.com/api/v1/pre_authorizations/AKJ398H8KBOOOA"
    }],
    "signature": "0733f3ce24f0c1c7c664099150492c3dad19232b87fa25b76f0f5e0ea29ffdd0"
  }
}
"""


class WebhookTests(TestCase):

    def test_request_bill_created(self):

        self.client.post(
            reverse('gocardless_webhook'), BILL_JSON_CREATED,
            content_type='application/javascript')

        # item should be flagged
        self.assertEqual(
            None,
            Payload.objects.all()[0].flag)

        # should produce one
        self.assertEqual(1, Payload.objects.count())

    def test_request_bill_paid(self):

        self.client.post(
            reverse('gocardless_webhook'), BILL_JSON_PAID,
            content_type='application/javascript')

        # item should be flagged
        self.assertEqual(
            None,
            Payload.objects.all()[0].flag)

        # should produce two
        self.assertEqual(2, Payload.objects.count())

    @override_settings(GOCARDLESS_APP_SECRET='BOGUS')
    def test_request_bill_paid_bogus(self):

        self.client.post(
            reverse('gocardless_webhook'), BILL_JSON_PAID,
            content_type='application/javascript')

        # item should be flagged
        self.assertEqual(
            'Signature did not validate',
            Payload.objects.all()[0].flag)

        # should produce two
        self.assertEqual(2, Payload.objects.count())

    def test_request_bill_withdrawn(self):

        self.client.post(
            reverse('gocardless_webhook'), BILL_JSON_WITHDRAWN,
            content_type='application/javascript')

        # item should be flagged
        self.assertEqual(
            None,
            Payload.objects.all()[0].flag)

        # should produce one
        self.assertEqual(1, Payload.objects.count())

    def test_request_bill_failed(self):

        self.client.post(
            reverse('gocardless_webhook'), BILL_JSON_FAILED,
            content_type='application/javascript')

        # item should be flagged
        self.assertEqual(
            None,
            Payload.objects.all()[0].flag)

        # should produce one
        self.assertEqual(1, Payload.objects.count())

    def test_request_bill_refunded(self):

        self.client.post(
            reverse('gocardless_webhook'), BILL_JSON_REFUNDED,
            content_type='application/javascript')

        # item should be flagged
        self.assertEqual(
            None,
            Payload.objects.all()[0].flag)

        # should produce one
        self.assertEqual(1, Payload.objects.count())

    def test_subscription_cancelled(self):

        self.client.post(
            reverse('gocardless_webhook'), SUBSCRIPTION_JSON_CANCELLED,
            content_type='application/javascript')

        # item should not be flagged
        self.assertEqual(
            None,
            Payload.objects.all()[0].flag)

        # should produce two
        self.assertEqual(2, Payload.objects.count())

    def test_subscription_expired(self):

        self.client.post(
            reverse('gocardless_webhook'), SUBSCRIPTION_JSON_EXPIRED,
            content_type='application/javascript')

        # item should not be flagged
        self.assertEqual(
            None,
            Payload.objects.all()[0].flag)

        # should produce one
        self.assertEqual(1, Payload.objects.count())

    def test_request_pre_auth_cancelled(self):

        self.client.post(
            reverse('gocardless_webhook'), PRE_AUTH_JSON_CANCELLED,
            content_type='application/javascript')

        # item should not be flagged
        self.assertEqual(
            None,
            Payload.objects.all()[0].flag)

        # should produce two
        self.assertEqual(2, Payload.objects.count())

    def test_request_pre_auth_expired(self):

        self.client.post(
            reverse('gocardless_webhook'), PRE_AUTH_JSON_EXPIRED,
            content_type='application/javascript')

        # item should not be flagged
        self.assertEqual(
            None,
            Payload.objects.all()[0].flag)

        # should produce two
        self.assertEqual(2, Payload.objects.count())
