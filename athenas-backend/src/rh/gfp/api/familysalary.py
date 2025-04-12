# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.decorator import login_required
from rh.gfp.models import FamilySalary, FamilySalaryRange


log = getLogger(__name__)


class GFPFamilySalary(RestfulDRY):

    _model = FamilySalary

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.familysalary.Manage")')


class GFPFamilySalaryRange(RestfulDRY):

    _model = FamilySalaryRange
