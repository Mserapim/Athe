from django.urls import path
from rh.gfp.apiv2.views import CedulacView


urlpatterns = [
    path("cedulac/", CedulacView.as_view(), name="cedula-c"),
]
