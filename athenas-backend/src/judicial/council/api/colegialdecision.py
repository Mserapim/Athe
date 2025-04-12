# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.council.models import ColegialDecision
from contrib.utils import DateUtils
from contrib.nil import nil_pk, nil_unicode, nil_display
from contrib.nil import nil_datetime
from judicial.api.partlawsuit import BasePartLawsuit


log = getLogger(__name__)


class CouncilColegialDecision(BasePartLawsuit, Restful):

    _model = ColegialDecision

    def model_to_dict(self, instance):
        rst = super(CouncilColegialDecision, self).model_to_dict(instance)

        rst.update(
            signed_at=nil_datetime(instance.signed_at, None),
            modified_by=nil_pk(instance.modified_by, None),
            modified_by_unicode=nil_unicode(instance.modified_by, None),
            type_part=instance.type_part,
            created_at=nil_datetime(instance.created_at, None),
            cached_number=instance.cached_number,
            modified_at=nil_datetime(instance.modified_at, None),
            number=int(instance.number or 0),
            created_by=nil_pk(instance.created_by, None),
            created_by_unicode=nil_unicode(instance.created_by, None),
            part_origin=nil_pk(instance.part_origin, None),
            part_origin_unicode=nil_unicode(instance.part_origin, None),
            signed_by=nil_pk(instance.signed_by, None),
            signed_by_unicode=nil_unicode(instance.signed_by, None),
            year=int(instance.year or 0),
            cache_rendered=instance.cache_rendered,
            resume=instance.resume,
            lawsuit=nil_pk(instance.lawsuit, None),
            lawsuit_unicode=nil_unicode(instance.lawsuit, None),
            rapporteur_vote_type=instance.rapporteur_document.rapporteur_vote_type,
            rapporteur_vote_type_display=nil_display(
                instance.rapporteur_document, "rapporteur_vote_type", None
            ),
            # rapporteur_document=nil_pk(instance.rapporteur_document, None),
            # rapporteur_document_unicode=nil_unicode(instance.rapporteur_document, None)
        )

        return rst
