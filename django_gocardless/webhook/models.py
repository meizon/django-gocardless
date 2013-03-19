import json
import model_utils
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from . import signals


class PayloadManager(models.Manager):

    def create_for_payload(self, payload, flag=None):

        resource_type = payload['resource_type']
        action = payload['action']
        signature = payload['signature']
        payload_json = json.dumps(payload, cls=DjangoJSONEncoder)

        attr_name = '%ss' % resource_type
        for item in payload[attr_name]:

            # create the object
            o = self.create(
                payload_id=item.get('id'),
                status=item.get('status'),
                source_type=item.get('source_type'),
                source_id=item.get('source_id'),
                amount=item.get('amount'),
                amount_minus_fees=item.get('amount_minus_fees'),
                paid_at=item.get('paid_at'),
                uri=item.get('uri'),
                resource_type=resource_type,
                action=action,
                signature=signature,
                json=payload_json,
                flag=flag
            )

            # send signals
            o.send_signals()


class Payload(models.Model):

    RESOURCE_CHOICES = model_utils.Choices(
        ('subscription', 'Subscription'),
        ('bill', 'Bill'),
        ('pre_authorization', 'Pre-Authorization')
    )

    ACTION_CHOICES = model_utils.Choices(
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('withdrawn', 'Withdrawn'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    )

    STATUS_CHOICES = model_utils.Choices(
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('withdrawn', 'Withdrawn'),
        ('refunded', 'Refunded'),
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired')
    )

    payload_id = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=255, choices=RESOURCE_CHOICES)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    source_type = models.CharField(
        max_length=255, choices=RESOURCE_CHOICES, null=True, blank=True)
    source_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)
    amount_minus_fees = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    uri = models.CharField(max_length=255)
    action = models.CharField(max_length=255, choices=ACTION_CHOICES)
    signature = models.TextField()
    received = models.DateTimeField(auto_now_add=True)
    flag = models.TextField(blank=True, null=True)

    # Track the original json we received, in case we need to post-process
    # later.
    json = models.TextField(blank=True, null=True)

    objects = PayloadManager()

    # helper methods

    def is_subscription(self):
        return self.resource_type == self.RESOURCE_CHOICES.subscription

    def is_bill(self):
        return self.resource_type == self.RESOURCE_CHOICES.bill

    def is_pre_authorization(self):
        return self.resource_type == self.RESOURCE_CHOICES.pre_authorization

    def is_cancelled(self):
        return self.action == self.ACTION_CHOICES.cancelled

    def is_expired(self):
        return self.action == self.ACTION_CHOICES.expired

    def is_created(self):
        return self.action == self.ACTION_CHOICES.created

    def is_paid(self):
        return self.action == self.ACTION_CHOICES.paid

    def is_withdrawn(self):
        return self.action == self.ACTION_CHOICES.withdrawn

    def is_failed(self):
        return self.action == self.ACTION_CHOICES.failed

    def is_refunded(self):
        return self.action == self.ACTION_CHOICES.refunded

    def send_signals(self):

        if self.is_subscription():
            if self.is_cancelled():
                signals.subscription_cancelled.send(sender=self)
            elif self.is_expired():
                signals.subscription_expired.send(sender=self)
        elif self.is_bill():
            if self.is_created():
                signals.bill_created.send(sender=self)
            elif self.is_paid():
                signals.bill_paid.send(sender=self)
            elif self.is_withdrawn():
                signals.bill_withdrawn.send(sender=self)
            elif self.is_failed():
                signals.bill_failed.send(sender=self)
            elif self.is_refunded():
                signals.bill_refunded.send(sender=self)
        if self.is_pre_authorization():
            if self.is_cancelled():
                signals.pre_authorization_cancelled.send(sender=self)
            elif self.is_expired():
                signals.pre_authorization_expired.send(sender=self)
