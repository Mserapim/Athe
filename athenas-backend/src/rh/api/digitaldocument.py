# -*- coding: utf-8 -*-

from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger
from rh.models import DigitalDocument, DigitalDocumentNaturalPerson

log = getLogger(__name__)


class RHDigitalDocument(RestfulDRY):

    _model = DigitalDocument

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    # exclude_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']

    full_text_index = ()

    exclude_fields = ["auditablemixins_ptr", "audittimestampmodel_ptr"]

    force_persist_boolean_fields = []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.digitaldocument.Manage")')

    @login_required("JSON")
    def model_to_dict(self, instance):
        rst = super(RHDigitalDocument, self).model_to_dict(instance)
        rst.update(permalink=instance.file.permalink() if instance.file else "")
        return rst


class RHDigitalDocumentAttachment(RHDigitalDocument):

    _model = DigitalDocument

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "cache_unicode__icontains",
    ) + RHDigitalDocument.full_text_index

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.digitaldocument.attachment.Manage")')


class RHDigitalDocumentNaturalPerson(RHDigitalDocument):

    _model = DigitalDocumentNaturalPerson

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    # exclude_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']

    full_text_index = () + RHDigitalDocument.full_text_index

    exclude_fields = ["digitaldocuments_ptr"] + RHDigitalDocument.exclude_fields

    force_persist_boolean_fields = []

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.digitaldocument.naturalperson.Manage")')


class RHDigitalDocumentEmployee(RHDigitalDocument):

    def get_query(self):
        """GET QUERY."""
        query = super(RHDigitalDocumentEmployee, self).get_query()
        user = employee_from_user(get_current_user())
        query = query.filter(employee=user)
        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.digitaldocument.employee.Manage")')
