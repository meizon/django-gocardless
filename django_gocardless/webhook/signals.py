from django.dispatch import Signal

# sent when a subscription is created
subscription_created = Signal()

# sent when a subscription is cancelled
subscription_cancelled = Signal()

# sent when a subscription has expired
subscription_expired = Signal()

# sent when a bill is created
bill_created = Signal()

# sent when a bill is paid
bill_paid = Signal()

# sent when a bill is withdrawn
bill_withdrawn = Signal()

# sent when a bill fails
bill_failed = Signal()

# sent when a bill is refunded
bill_refunded = Signal()

# sent when a pre_authorization is created
pre_authorization_created = Signal()

# sent when a pre_authorization is cancelled
pre_authorization_cancelled = Signal()

# sent when a pre_authorization has expired
pre_authorization_expired = Signal()
