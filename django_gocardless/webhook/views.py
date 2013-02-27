import json
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from gocardless.utils import generate_signature

from .models import GoCardlessWebhook


class WebhookView(View):

    def verify_signature(self, payload):

        pms = payload.copy()
        pms.pop('signature')
        signature = generate_signature(pms, settings.GOCARDLESS_APP_SECRET)

        if signature == payload['signature']:
            return True
        return False

    def post(self, request, *args, **kwargs):

        flag = None
        webhook_obj = GoCardlessWebhook()

        # move the json into a workable format
        payload = json.loads(request.body)['payload']

        if not self.verify_signature(payload):
            flag = u'Signature did not validate'

        # initialise the obj
        webhook_obj.initialise(request, payload, flag)

        return HttpResponse('OK')


webhook_view = csrf_exempt(WebhookView.as_view())
