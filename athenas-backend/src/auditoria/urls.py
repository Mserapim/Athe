from django.urls import path
from auditoria.apiv2.views import AuditoriaLogView, ModelosLogView

urlpatterns = [
    path("logs/", AuditoriaLogView.as_view(), name="auditoria-logs"),
    path("logs/modelos/", ModelosLogView.as_view(), name="auditoria-logs-modelos"),
]
