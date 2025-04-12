from apiv2.baseserializers import BaseSerializer

from rh.models import MembersTelecommuting


class MembrosTrabalhoRemotoSerializer(BaseSerializer):
    class Meta:
        model = MembersTelecommuting
        fields = "__all__"
