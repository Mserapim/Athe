from django.urls import path
from auth.apiv2.views import MastiffPermissionView, TokenObtainView
from rh.apiv2.views.employeecurrent import EmployeeCurrentView

urlpatterns = [
    path("mastiff/permissions/", MastiffPermissionView.as_view(), name="permissions"),
    path("login", TokenObtainView.as_view(), name="external-token"),
    path("current-user/", EmployeeCurrentView.as_view(), name="employee-current"),
]
