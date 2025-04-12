from contrib.newrest import RestfulDRY
from planejamento.contrato.models import Enterprise, CorporateStructure
from standard.models import Choice
from contrib.nil import nil_display


class PHEEnterprise(RestfulDRY):

    _model = Enterprise

    force_upper = False

    full_text_index = (
        "person__nome__icontains",
        "person__pessoajuridica__razao_social__icontains",
        "person__pessoajuridica__cnpj__icontains",
        "person__pessoafisica__social_name__icontains",
    )

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(
            motive_unicode=nil_display(instance, "motive", None),
            motive_choice=instance.motive,
        )

        return rst

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("planning.hiring.enterprise.Manage")')


class PHECorporateStructure(RestfulDRY):

    _model = CorporateStructure

    force_upper = False

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        cargo = Choice.objects.get(
            app_label="contrato", name="CARGO_EMPRESA", cvalue=instance.office
        )

        rst.update(office_unicode=cargo.label)

        return rst
