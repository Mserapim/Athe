from rh.pvf.absence.models import (
    HealthTreatmentAbsence,
    FamilyHealthTreatmentAbsence,
    MaternityAbsence,
    PaternityAbsence,
    MourningAbsence,
    MarriageAbsence,
    BloodDonationAbsence,
)
from rh.pvf.apiv2.serializers.absenceserializers import *
from rh.models import Servidor
from rh.pvf.const import *
from rest_framework.permissions import IsAuthenticated
from auth.permissions.vdf.permissions import IsPermissionVDF
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from django.shortcuts import get_object_or_404
from contrib.middleware import set_current_user
from rest_framework.views import APIView


class PVFRequestAbsenceViewSet(GenericViewSet):
    """
    View das solicitações de afastamento VDF
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = None
    serializer_class = None
    portal_request_type = None

    def post(self, request, *args, **kwargs):
        """Cria uma nova solicitação"""
        return self.create(request, *args, **kwargs)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(item)
        return Response(serializer.data)


class PVFPreValidacaoAfastamentoView(APIView):
    """
    View da pré validação de afastamentos
    """

    permission_classes = [IsAuthenticated, IsPermissionVDF]
    queryset = PortalRequestAbsence.objects.filter()
    serializer_class = PVFPreValidacaoAfastamentoSerializador

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "date"},
                    "end_date": {"type": "date"},
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        set_current_user(request.user)
        dados = request.data
        dados_serializados = self.serializer_class().pre_validacao(dados)
        if dados_serializados["success"]:
            return Response(dados_serializados, status=status.HTTP_200_OK)
        return Response(dados_serializados, status=status.HTTP_400_BAD_REQUEST)


class PVFHealthTreatmentAbsenceViewSet(PVFRequestAbsenceViewSet):
    """
    View das solicitações de afastamento de licença para tratamento de saúde
    """

    queryset = HealthTreatmentAbsence.objects.filter()
    serializer_class = PVFHealthTreatmentAbsenceSerializer
    portal_request_type = None

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "date"},
                    "end_date": {"type": "date"},
                    "substitutes": {
                        "type": "[{start_date:date,end_date:date,substitute:pk,exercise:pk}]"
                    },
                    "medical_certificate": {"type": "integer"},
                    "observation": {"type": "string"},
                    "hours": {"type": "integer"},
                    "cid": {"type": "integer"},
                },
            },
        },
    )
    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().create(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFHealtFamiliyDeseaseViewSet(PVFRequestAbsenceViewSet):
    """
    View das solicitações de afastamento de licença em doença em pessoa da família
    """

    queryset = FamilyHealthTreatmentAbsence.objects.filter()
    serializer_class = PVFHealtFamiliyDeseaseSerializer
    portal_request_type = None

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "date"},
                    "end_date": {"type": "date"},
                    "substitutes": {
                        "type": "[{start_date:date,end_date:date,substitute:pk,exercise:pk}]"
                    },
                    "degree_kinship": {"type": "integer"},
                    "person": {"type": "integer"},
                    "cid": {"type": "integer"},
                    "medical_certificate": {"type": "integer"},
                    "observation": {"type": "string"},
                },
            },
        },
    )
    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().create(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFMaternityAbsenceViewSet(PVFRequestAbsenceViewSet):
    """
    View das solicitações de afastamento de licença maternidade
    """

    queryset = MaternityAbsence.objects.filter()
    serializer_class = PVFMaternityAbsenceSerializer
    portal_request_type = None

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "date"},
                    "end_date": {"type": "date"},
                    "dependent": {"type": "integer"},
                    "dependent_type": {"type": "integer"},
                    "substitutes": {
                        "type": "[{start_date:date,end_date:date,substitute:pk,exercise:pk}]"
                    },
                    "is_childcare_assistence": {"type": "bool"},
                    "capacity": {"type": "bool"},
                    "is_incoming_tax": {"type": "bool"},
                    "birth_certificate": {"type": "integer"},
                    "observation": {"type": "string"},
                },
            },
        },
    )
    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().create(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFBirthAbsenceViewSet(PVFMaternityAbsenceViewSet):
    """
    View das solicitações de afastamento de licença paternidade
    """

    queryset = PaternityAbsence.objects.filter()
    serializer_class = PVFBirthAbsenceSerializer
    portal_request_type = None


class PVFDeathAbsenceViewSet(PVFRequestAbsenceViewSet):
    """
    View das solicitações de afastamento de licença luto
    """

    queryset = MourningAbsence.objects.filter()
    serializer_class = PVFDeathAbsenceSerializer
    portal_request_type = None

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "date"},
                    "end_date": {"type": "date"},
                    "person": {"type": "integer"},
                    "family_bond": {"type": "integer"},
                    "substitutes": {
                        "type": "[{start_date:date,end_date:date,substitute:pk,exercise:pk}]"
                    },
                    "death_certificate": {"type": "integer"},
                    "observation": {"type": "string"},
                },
            },
        },
    )
    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().create(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFMarriageAbsenceViewSet(PVFRequestAbsenceViewSet):
    """
    View das solicitações de afastamento de licença gala
    """

    queryset = MarriageAbsence.objects.filter()
    serializer_class = PVFMarriageAbsenceSerializer
    portal_request_type = None

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "date"},
                    "end_date": {"type": "date"},
                    "person": {"type": "integer"},
                    "substitutes": {
                        "type": "[{start_date:date,end_date:date,substitute:pk,exercise:pk}]"
                    },
                    "marriage_certificate": {"type": "integer"},
                    "observation": {"type": "string"},
                },
            },
        },
    )
    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().create(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)


class PVFBloodDonationAbsenceViewSet(PVFRequestAbsenceViewSet):
    """
    View das solicitações de ausência doação de sangue
    """

    queryset = BloodDonationAbsence.objects.filter()
    serializer_class = PVFBloodDonationAbsenceSerializer
    portal_request_type = None

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "date"},
                    "end_date": {"type": "date"},
                    "substitutes": {
                        "type": "[{start_date:date,end_date:date,substitute:pk,exercise:pk}]"
                    },
                    "blood_donation_certificate": {"type": "integer"},
                    "observation": {"type": "string"},
                },
            },
        },
    )
    def create(self, request):
        set_current_user(request.user)
        data = request.data
        serializer_data = self.serializer_class().create(data)
        if serializer_data["success"]:
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)
