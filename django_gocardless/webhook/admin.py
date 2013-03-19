from django.contrib import admin

from .models import Payload


class PayloadAdmin(admin.ModelAdmin):

    list_display = ('payload_id', 'resource_type', 'status', 'received')
    exclude = ('json',)

    def has_add_permission(self, request):
        return False

admin.site.register(Payload, PayloadAdmin)

