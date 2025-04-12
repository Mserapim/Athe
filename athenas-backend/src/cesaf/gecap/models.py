# -*- coding: utf-8 -*-
from django.db import models
from contrib.decorator import to_search


@to_search(
    [{"name": "titulo", "type": "text"}, {"name": "cache_codigo_cnpq", "type": "text"}]
)
class AreaConhecimento(models.Model):

    titulo = models.CharField(max_length=200)
    codigo_cnpq = models.SmallIntegerField(null=True, blank=True)
    cache_codigo_cnpq = models.CharField(max_length=20, null=True, blank=True)
    sub_area_de = models.ForeignKey(
        "gecap.AreaConhecimento",
        on_delete=models.CASCADE,
        related_name="sub_areas",
        null=True,
        blank=True,
    )  # Parametro "on_delete" adicionado. (Django 2)

    class Meta:
        ordering = ["titulo", "codigo_cnpq"]

    def get_codigo(self):
        if self.cache_codigo_cnpq is None or self.cache_codigo_cnpq == "":
            if self.sub_area_de is None:
                result = "%s" % self.codigo_cnpq
            else:
                result = "%s.%s" % (
                    self.sub_area_de.get_codigo(),
                    self.codigo_cnpq if self.codigo_cnpq else 0,
                )
            self.cache_codigo_cnpq = result
            self.save()
        return self.cache_codigo_cnpq

    def __str__(self):
        return "%s %s" % (self.get_codigo(), self.titulo)


class Capacitacao(models.Model):
    nome = models.CharField(max_length=60, null=False, blank=False, verbose_name="Nome")
    dt_inicio = models.DateField(verbose_name="Data de inicio", null=True, blank=True)
    dt_fim = models.DateField(verbose_name="Data de fim", null=True, blank=True)
    carga_horaria = models.IntegerField(null=True, blank=True)
    promovido_por = models.IntegerField(
        choices=(
            (1, "CESAF"),
            (2, "CESAF E TERCEIRO"),
            (3, "TERCEIRO"),
        )
    )
    promotores = models.ManyToManyField("rh.OrgaoGeral", related_name="capacitacoes")
    cidade_evento = models.ForeignKey(
        "rh.Localidade", related_name="capacitacoes", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    area_conhecimento = models.ManyToManyField(
        AreaConhecimento, related_name="capacitacoes"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ementa = models.TextField(verbose_name="Ementa", null=True, blank=True)
    publicar = models.BooleanField(verbose_name="Publicar no site", default=False)
    descricao = models.TextField(
        verbose_name="Descrição para o Site", null=True, blank=True
    )
    inscricao_inicio = models.DateTimeField(null=True, blank=True)
    inscricao_fim = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.nome)

    def delete(self):
        if self.inscricoes.exclude(homologado=None).count() > 0:
            raise Exception(
                "Não posso excluir esta capacitação, pois temos inscrições homologadas."
            )
        else:
            models.Model.delete(self)


class Evento(Capacitacao):
    pass


class Seminario(Capacitacao):
    pass


class Oficina(Capacitacao):
    pass


class Feira(Capacitacao):
    pass


class Reuniao(Capacitacao):
    pass


class Congresso(Capacitacao):
    pass


class Curso(Capacitacao):
    pass


class Inscricao(models.Model):
    class Meta:
        unique_together = ("capacitacao", "servidor")

    # Parametro "on_delete" adicionado. (Django 2)
    servidor = models.ForeignKey(
        "rh.Servidor", related_name="inscricoes", on_delete=models.CASCADE
    )
    capacitacao = models.ForeignKey(
        "gecap.Capacitacao", related_name="inscricoes", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Parametro "on_delete" adicionado. (Django 2)
    certificado = models.ForeignKey(
        "ged.Arquivo", null=True, blank=True, on_delete=models.CASCADE
    )
    homologado = models.DateTimeField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{0} / {1}".format(self.capacitacao, self.servidor)


class Investimento(models.Model):
    inscricao = models.ForeignKey(
        "gecap.Inscricao",
        related_name="investimentos",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    capacitacao = models.ForeignKey(
        "gecap.Capacitacao",
        on_delete=models.CASCADE,
        related_name="investimentos",
        null=True,
        blank=True,
    )  # Parametro "on_delete" adicionado. (Django 2)
    descricao = models.CharField(max_length=60)
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    previsao = models.BooleanField(default=True)
