django-gocardless
=================

Using GoCardless Django
-----------------------

1. Download the code from GitHub:

        git clone git://github.com/astonecutter/django-gocardless.git django_gocardless

1. Edit `settings.py` and add  `django_gocardless.webhook` to your `INSTALLED_APPS` 
   and `GOCARDLESS_APP_SECRET`:

        # settings.py
        ...
        INSTALLED_APPS = (... 'django_gocardless.webhook', ...)
        ...
        GOCARDLESS_APP_SECRET = "...$$$..."

1.  GoCardless will post to your "webhook_url". 
    The view `django_gocardless.webhook.views.webhok_view` handles this. 
    To set the correct `webhook_url` add the following to your `urls.py`:

        # urls.py
        ...
        urlpatterns = patterns('',
            (r'^something/hard/to/guess/', include('django_gocardless.webhook.urls')),
        )

1.  Whenever a webhook payload is processed a signal will be sent with the 
    result of the transaction. Connect the signals to actions to perform 
    the needed operations when a successful payment is recieved.
    
    There are two signals for subscriptions:
    - `subscription_cancelled` - Sent when a subscription is cancelled.
    - `subscription_expired` - Sent when a subscription expires.

    Two for pre-authorizations:
    - `pre_authorization_cancelled` - Sent when a pre-auth is cancelled.
    - `pre_authorization_expired` - Sent when a pre-auth expires.    

    Several more exist for bills:
    - `bill_created` - Sent when waiting for the money to clear from the customer's account.
    - `bill_paid` - Sent when bill has been succesfully been debited from the customer's account.
    - `bill_withdrawn` - Sent when the bill has been paid out to the merchant.
    - `bill_failed` - Sent when bill could not be debited from a customer's account.
    - `bill_refunded` - Sent when bill has been refunded to the customer.

    Connect to these signals and update your data accordingly. [Django Signals Documentation](http://docs.djangoproject.com/en/dev/topics/signals/).

        # models.py
        ...
        from django_gocardless.webhook.signals import bill_withdrawn
        
        def receive_the_money(sender, **kwargs):
            payload_obj = sender
            # Undertake some action depending upon `payload_obj`.

        bill_withdrawn.connect(receive_the_money)
