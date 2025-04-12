from contrib.controller import DefaultController
from contrib.decorator import login_required
from contrib.utils import get_json_engine, getLogger

json = get_json_engine()
log = getLogger(__name__)


class DAYOFFEnjoyedRecessesAndGapsReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.EnjoyedRecessesAndGaps")')


class DAYOFFPendingRecessesAndGapsReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.PendingRecessesAndGaps")')


class DAYOFFUsufructRecessesAndGapsReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.UsufructRecessesAndGaps")')


class DAYOFFHistoryRecessesAndGapsReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.HistoryRecessesAndGaps")')
