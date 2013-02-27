from django.conf.urls.defaults import patterns, url

from .views import webhook_view

urlpatterns = patterns(
    '',
    url(r'^$', webhook_view, name="gocardless_webhook"),
)
