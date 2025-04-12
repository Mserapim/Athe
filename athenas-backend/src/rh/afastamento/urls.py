from django.urls import path, include
from rh.afastamento.apiv2.views.base_afastamentos import BaseAbsenceViewSet

from rest_framework import routers

router = routers.DefaultRouter()

router.register("absences", BaseAbsenceViewSet, basename="absences")

urlpatterns = [path("", include(router.urls))]
