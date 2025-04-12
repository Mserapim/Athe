from django.urls import path

from standard.apiv2.views.choices import ChoicesListFormulariosView

urlpatterns = [
   path('choices-formulario/', ChoicesListFormulariosView.as_view()),

]