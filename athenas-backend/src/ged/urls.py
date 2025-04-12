from django.urls import path
from ged.apiv2.views import UploadFileView, DownloadFileView


urlpatterns = [
    path("upload/", UploadFileView.as_view(), name="upload-view"),
    path("download/", DownloadFileView.as_view(), name="download-view"),
]
