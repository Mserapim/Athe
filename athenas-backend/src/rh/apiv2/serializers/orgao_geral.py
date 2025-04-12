from apiv2.baseserializers import BaseSerializer

from rh.models import OrgaoGeral, UnidadeAdministrativa


class OrgaoGeralSerializer(BaseSerializer):
    class Meta:
        model = OrgaoGeral
        fields = "__all__"


class UnidadeAdministrativaSerializer(BaseSerializer):
    class Meta:
        model = UnidadeAdministrativa
        fields = "__all__"
