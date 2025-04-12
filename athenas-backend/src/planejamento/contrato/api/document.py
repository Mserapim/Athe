from contrib.newrest import RestfulDRY
from planejamento.contrato.models import (
    Document,
    AgreementDocument,
    ValueDocument,
    MinuteDocument,
)


class PHDocument(RestfulDRY):

    _model = Document

    force_upper = False

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(filename=instance.filename, document_type=instance.document_type)

        return rst

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("planning.hiring.document.DocumentManager")')


class PHAgreementDocument(PHDocument):

    _model = AgreementDocument


class PHValueDocument(PHDocument):

    _model = ValueDocument


class PHMinuteDocument(PHDocument):

    _model = MinuteDocument
