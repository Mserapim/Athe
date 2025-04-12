# -*- coding: utf-8 -*-


from contrib.newrest import RestfulDRY
from contrib.utils import DateUtils, getLogger
from rh.gfp.models import ExtraPayment, ExtraPaymentPeriod

log = getLogger(__name__)


class GFPExtraPayment(RestfulDRY):

    _model = ExtraPayment

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = ("name__icontains",)

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = True

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    exclude_fields = ["modified_by", "created_by", "created_at", "modified_at"]

    def updater(self, args=[]):
        log.debug(self.request.POST)
        rst = {"success": False, "message": "Não foi executado nada ainda."}

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            rst.update(
                success=False,
                message="Você não tem permissão para alterar %s."
                % self.Model._meta.object_name,
            )
        else:
            try:
                inst = self.Model.objects.get(pk=self.request.POST.get("extra_payment"))
                inst.update_periods(
                    float(self.request.POST.get("value")),
                    DateUtils.str_to_date(self.request.POST.get("start_validity")),
                    False if self.request.POST.get("type_value") != "P" else True,
                    False if self.request.POST.get("method_value") != "A" else True,
                )
            except self.Model.DoesNotExist:
                rst.update(message="Não consegui encontrar o item desejado.")
            except Exception as e:
                rst.update(message=str(e))
            else:
                rst.update(success=True)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.extrapayment.ExtraPaymentManage")')


class GFPExtraPaymentPeriod(RestfulDRY):

    _model = ExtraPaymentPeriod

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "extra_payment__name__icontains",
        "employee__matricula__iexact",
        "employee__pessoa_fisica__nome__icontains",
        "information__icontains",
    )

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = True

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    exclude_fields = ["modified_by", "created_by", "created_at", "modified_at"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.extrapayment.ExtraPaymentPeriodManage")'
        )


class GFPExtraPaymentBenefitPeriod(GFPExtraPaymentPeriod):
    EXTRA_PAYMENT_ID = 30  # Retorna Benefício

    def get_query(self):
        return super().get_query().filter(extra_payment__id=self.EXTRA_PAYMENT_ID)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.benefits_manager.benefit.ExtraPaymentPeriodManage", {extra_payment: "%s"})'
            % (self.EXTRA_PAYMENT_ID)
        )


class GFPExtraPaymentRetireePeriod(GFPExtraPaymentBenefitPeriod):
    EXTRA_PAYMENT_ID = 4  # Retorna Servidor Aposentado

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.benefits_manager.inactive_employee.ExtraPaymentPeriodManage", {extra_payment: "%s"})'
            % (self.EXTRA_PAYMENT_ID)
        )


class GFPExtraPaymentRetireeMemberPeriod(GFPExtraPaymentBenefitPeriod):
    EXTRA_PAYMENT_ID = 6  # Retorna Membro Aposentado

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.benefits_manager.retiree_member.ExtraPaymentPeriodManage", {extra_payment: "%s"})'
            % (self.EXTRA_PAYMENT_ID)
        )


class GFPExtraPaymentAttachePeriod(GFPExtraPaymentPeriod):
    EXTRA_PAYMENT_ID = 2  # Retorna Adidos

    def get_query(self):
        return (
            super()
            .get_query()
            .filter(extra_payment__id=self.EXTRA_PAYMENT_ID)
            .exclude(employee__isnull=True)
        )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.benefits_manager.attache.ExtraPaymentPeriodManage", {extra_payment: "%s"})'
            % (self.EXTRA_PAYMENT_ID)
        )
