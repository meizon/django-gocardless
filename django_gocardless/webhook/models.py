import json
import model_utils
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

from .signals import (
    subscription_created,
    subscription_cancelled,
    subscription_expired,
    bill_created,
    bill_paid,
    bill_withdrawn,
    bill_failed,
    bill_refunded,
    pre_authorization_created,
    pre_authorization_cancelled,
    pre_authorization_expired
)


class GoCardlessWebhook(models.Model):

    RESOURCE_CHOICES = model_utils.Choices(
        ('subscription', 'Subscription'),
        ('bill', 'Bill'),
        ('pre_authorization', 'Pre-Authorization')
    )

    ACTION_CHOICES = model_utils.Choices(
        ('created', 'Created'),
        ('paid', 'Paid'),
        ('withdrawn', 'Withdrawn'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    )

    resource_type = models.CharField(max_length=255, choices=RESOURCE_CHOICES)
    action = models.CharField(max_length=255, choices=ACTION_CHOICES)
    signature = models.TextField()
    received = models.DateTimeField(auto_now_add=True)

    # Track the original json we received, in case we need to post-process
    # later.
    json = models.TextField(blank=True, null=True)
    flag = models.TextField(blank=True, null=True)

    def initialise(self, request, payload, flag):
        self.resource_type = payload['resource_type']
        self.action = payload['action']
        self.signature = payload['signature']
        self.json = json.dumps(payload, cls=DjangoJSONEncoder)
        self.flag = flag
        self.save()

        if self.resource_type == self.RESOURCE_CHOICES.subscription:
            self.initialise_items(payload['subscriptions'])
        elif self.resource_type == self.RESOURCE_CHOICES.bill:
            self.initialise_items(payload['bills'])
        elif self.resource_type == self.RESOURCE_CHOICES.pre_authorization:
            self.initialise_items(payload['pre_authorizations'])

    def initialise_items(self, payload_items):

        for pi in payload_items:
            pi.update({'resource_type': self.resource_type})
            pi_obj = self.items.create(**pi)
            pi_obj.send_signals()


class GoCardlessWebhookItem(models.Model):

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

    SOURCE_CHOICES = model_utils.Choices(
        ('subscription', 'Subscription'),
        ('pre_authorization', 'Pre-Authorization')
    )

    RESOURCE_CHOICES = model_utils.Choices(
        ('subscription', 'Subscription'),
        ('bill', 'Bill'),
        ('pre_authorization', 'Pre-Authorization')
    )

    id = models.CharField(max_length=255, primary_key=True)
    resource_type = models.CharField(max_length=255, choices=RESOURCE_CHOICES)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    source_type = models.CharField(
        max_length=255, choices=SOURCE_CHOICES, null=True, blank=True)
    source_id = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)
    amount_minus_fees = models.DecimalField(
        decimal_places=2, max_digits=10, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    uri = models.CharField(max_length=255)

    webhook = models.ForeignKey(GoCardlessWebhook, related_name='items')

    def is_subscription(self):
        return self.resource_type == self.RESOURCE_CHOICES.subscription

    def is_bill(self):
        return self.resource_type == self.RESOURCE_CHOICES.bill

    def is_pre_authorization(self):
        return self.resource_type == self.RESOURCE_CHOICES.pre_authorization

    # bill related

    def is_bill_created(self):
        return self.status == self.STATUS_CHOICES.pending

    def is_bill_paid(self):
        return self.status == self.STATUS_CHOICES.paid

    def is_bill_withdrawn(self):
        return self.status == self.STATUS_CHOICES.withdrawn

    def is_bill_failed(self):
        return self.status == self.STATUS_CHOICES.failed

    def is_bill_refunded(self):
        return self.status == self.STATUS_CHOICES.refunded

    # pre-auth related

    def is_pre_authorization_created(self):
        return self.status == self.STATUS_CHOICES.active

    def is_pre_authorization_cancelled(self):
        return self.status == self.STATUS_CHOICES.cancelled

    def send_signals(self):
        if self.is_subscription():
            if self.is_subscription_created():
                subscription_created.send(sender=self)
            elif self.is_subscription_cancelled():
                subscription_cancelled.send(sender=self)
            elif self.is_subscription_expired():
                subscription_expired.send(sender=self)
        elif self.is_bill():
            if self.is_bill_created():
                bill_created.send(sender=self)
            elif self.is_bill_paid():
                bill_paid.send(sender=self)
            elif self.is_bill_withdrawn():
                bill_withdrawn.send(sender=self)
            elif self.is_bill_failed():
                bill_failed.send(sender=self)
            elif self.is_bill_refunded():
                bill_refunded.send(sender=self)
        elif self.is_pre_authorization():
            if self.is_pre_authorization_created():
                pre_authorization_created.send(sender=self)
            elif self.is_pre_authorization_cancelled():
                pre_authorization_cancelled.send(sender=self)
            elif self.is_pre_authorization_expired():
                pre_authorization_expired.send(sender=self)
