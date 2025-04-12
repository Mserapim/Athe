# -*- coding:utf-8 -*-

from django.db import models
from django.template import loader, Context


class BankPartnership(models.Model):

    class Meta:
        verbose_name = "Tipo de Boleto"
        verbose_name_plural = "Tipos de Boletos"

    identifier = models.CharField(
        "Identificador de Tipo", default="interno", max_length=100
    )  # internal_payment OR external_payment
    charge_code = models.CharField(
        "Codigo de Cobranca", default="3179485", max_length=7
    )
    partnertship_code = models.CharField(
        "Codigo de Convenio de Com. Eletronico", default="319875", max_length=6
    )
    callback_url = models.CharField(
        "Url de Retorno", default="https://athenas.mpto.mp.br/athenas/", max_length=256
    )
    days_remaining = models.CharField(
        "Dias para o vencimento", default="10", max_length=3
    )

    def __str__(self):

        if self.identifier == "INTERNAL_PAYMENT":
            return "Dados para geração de boleto para membros e servidores do MPE"
        else:
            return "Dados para geração de boletos para pessoas sem vínculo com o MPE"

    @classmethod
    def render_partnership(self, identifier):
        partnership = self.objects.get(identifier=identifier)
        return loader.get_template("payments/partnership.html").render(
            Context({"partnership": partnership})
        )


class TicketPay(models.Model):

    class Meta:
        verbose_name = "Boleto"
        verbose_name_plural = "Boletos"

    name = models.CharField(verbose_name="Nome", max_length=60)
    cpf_cnpj = models.CharField(verbose_name="CPF/Cnpj", max_length=14)
    city = models.CharField(verbose_name="Cidade", max_length=18)
    state = models.CharField(verbose_name="UF", max_length=2)
    zip_code = models.CharField(verbose_name="CEP", max_length=8)
    types_recipes = models.CharField(
        verbose_name="Tipos de Receita", default="", max_length=100
    )
    process_number = models.CharField(
        verbose_name="Processo", default="0000000000000000000", max_length=25
    )
    message_store = models.CharField(verbose_name="Mensagem", max_length=1082)
    address = models.CharField(verbose_name="Endereço", max_length=250)
    value = models.DecimalField(verbose_name="Valor", decimal_places=2, max_digits=15)
    control = models.CharField(verbose_name="Controle", max_length=10)
    ticket_number = models.CharField(verbose_name="Número do Boleto", max_length=17)
    expiration_date = models.DateField(verbose_name="Data de Vencimento")
    person_type = models.CharField(
        verbose_name="Tipo de Pessoa", default="1", max_length=1
    )
    payment_type = models.CharField(
        verbose_name="Tipo de Pagamento", default="2", max_length=2
    )
    document_type = models.CharField(
        verbose_name="Tipo de Duplicata", default="DS", max_length=2
    )
    partnership = models.ForeignKey(
        BankPartnership, related_name="tickets", on_delete=models.CASCADE
    )
    creation_date = models.DateTimeField(
        verbose_name="Data de Emissão", auto_now_add=True
    )

    def formatControl(self):
        if self.pk:
            return str(self.pk).zfill(10)
        return None

    def __str__(self):
        return "%s" % self.ticket_number
