import json
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from gocardless.utils import generate_signature

from .models import Payload


def verify_signature(payload):

    pms = payload.copy()
    pms.pop('signature')
    signature = generate_signature(pms, settings.GOCARDLESS_APP_SECRET)

    if signature == payload['signature']:
        return True
    return False


class WebhookView(View):

    def post(self, request, *args, **kwargs):

        flag = None

        # move the json into a workable format
        payload = json.loads(request.body)['payload']

        if not verify_signature(payload):
            flag = u'Signature did not validate'

        # initialise the objects
        Payload.objects.create_for_payload(payload, flag)

        return HttpResponse('OK')


webhook_view = csrf_exempt(WebhookView.as_view())
