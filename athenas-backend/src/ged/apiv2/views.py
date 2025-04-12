from app import settings
from contrib.base_converter import normalizar_nome, str_to_bool
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from contrib.uploadfile import UploadFile
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import authentication_classes, permission_classes
from contrib.utils import import_from_string
import os


class UploadFileView(APIView):
    """
    View para realizar o upload do arquivo
    """

    permission_classes = [IsAuthenticated]
    # parser_classes = [FileUploadParser]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "name": {"type": "string"},
                    "format_valid": {"type": "string"},
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request):
        response = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "file_id": None,
        }
        file_obj = request.FILES.get("file", None)
        format_valid = request.data.get("format_valid", None)
        root, extension = os.path.splitext(file_obj.name)
        root = normalizar_nome(root)
        filename = f"{root}{extension}"

        file = UploadFile.create_file(file_obj, filename, request.user)
        if not file:
            response.update({"success": False, "message": "O arquivo não foi enviado!"})
        elif format_valid and format_valid != extension.upper().replace(".", ""):
            response.update(
                {
                    "success": False,
                    "message": "Por favor, selecione um arquivo válido. Apenas arquivos no formato PDF são aceitos.",
                }
            )
        else:
            response.update(
                {
                    "success": True,
                    "message": "Arquivo enviado com sucesso!",
                    "file_id": file.pk,
                }
            )
        if response["success"]:
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes(import_from_string(settings.AUTHENTICATION_CLASSES_REPORT))
@permission_classes(import_from_string(settings.PERMISSION_CLASSES_REPORT))
class DownloadFileView(APIView):
    """
    View para realizar o download do arquivo
    """

    # permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="file_id", description="Arquivo Id", type=int),
            OpenApiParameter(name="download", description="Baixar", type=str),
        ]
    )
    def get(self, request, *args, **kwargs):
        rst = {"success": False, "message": "Arquivo não econtrado"}
        file_id = request.GET.get("file_id", None)
        download = str_to_bool(request.GET.get("download", "true"))
        file = UploadFile.get_file(file_id)
        if file:
            file_path = file.absolute_path
            with open(file_path, "rb") as f:
                response = HttpResponse(f.read())
                content_type = "attachment" if download else "inline"
                response["Content-Disposition"] = (
                    f"{content_type}; filename={file.filename}"
                )
                response["Content-Type"] = file.mimetype
                return response
        return Response(rst, status=status.HTTP_400_BAD_REQUEST)
