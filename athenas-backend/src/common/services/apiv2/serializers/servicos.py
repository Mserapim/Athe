from rest_framework import serializers

from apiv2.baseserializers import BaseSerializer

from common.services.models import ScheduledServices
from engine.mq.models import TaskMessages


class ServicosSerializer(BaseSerializer):
    """
    Serializer do model Servicos
    """

    classcode_path = serializers.SerializerMethodField()
    created_by_unicode = serializers.SerializerMethodField()
    modified_by_unicode = serializers.SerializerMethodField()
    executado_por_unicode = serializers.SerializerMethodField()
    status_execucao = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledServices
        fields = "__all__"

    def get_classcode_path(self, obj):
        return obj.classcode.path if obj.classcode else ""

    def get_created_by_unicode(self, obj):
        return obj.created_by.username

    def get_modified_by_unicode(self, obj):
        return obj.modified_by.username

    def get_executado_por_unicode(self, obj):
        return obj.executado_por.username if obj.executado_por else ""

    def get_status_execucao(self, obj):
        if obj.em_execucao == True:
            return "executando"
        else:
            return "sucesso" if obj.executado else "erro"


class MensagensServicoSerializer(BaseSerializer):
    """
    Serializer do model TaskMessages
    """

    task_uuid = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    owner_unicode = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    started_task = serializers.SerializerMethodField()
    finished_task = serializers.SerializerMethodField()

    class Meta:
        model = TaskMessages
        fields = "__all__"

    def get_task_uuid(self, obj):
        return obj.tasker.uuid if obj.tasker else ""

    def get_owner(self, obj):
        return f"{obj.tasker.owner.id}" if obj.tasker else ""

    def get_owner_unicode(self, obj):
        return f"{obj.tasker.owner.servidor}" if obj.tasker else ""

    def get_description(self, obj):
        return obj.tasker.description if obj.tasker else ""

    def get_state(self, obj):
        return obj.tasker.state if obj.tasker else ""

    def get_started_task(self, obj):
        return obj.tasker.started_task if obj.tasker else ""

    def get_finished_task(self, obj):
        return obj.tasker.finished_task if obj.tasker else ""
