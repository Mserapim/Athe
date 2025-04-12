from django.contrib import admin
from ged import models as ged_models

admin.site.register(
    [
        ged_models.Arquivo,
    ]
)
