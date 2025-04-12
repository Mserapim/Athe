from contrib.controller import DefaultController


class ClinicalManage(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.clinical.prescription.Manage")')
