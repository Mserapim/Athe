# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from corregedoria.inspection.models import (
    AdministrativeOrganizationProceduresInProgress,
)
import raf.api.util

log = getLogger(__name__)


class INSPECTIONAdministrativeOrganizationProceduresInProgress(RestfulDRY):

    force_upper = False

    full_text_index = ()

    _model = AdministrativeOrganizationProceduresInProgress

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.administrativeorganization.proceduresinprogress.Launcher")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(
            INSPECTIONAdministrativeOrganizationProceduresInProgress, self
        ).model_to_dict(instance)
        _dict_.update(
            {
                "taxonomy_class_title": (
                    instance.taxonomy_class.title if instance.taxonomy_class else None
                ),
                "taxonomy_matter_title": (
                    instance.taxonomy_matter.title
                    if instance.taxonomy_matter
                    else instance.matter
                ),
            }
        )
        return _dict_
