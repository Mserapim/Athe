# -.- coding: utf-8 -.-
from contrib.decorator import to_search
from django.db import models


class GrupoDespesa(models.Model):
    numero = models.IntegerField()
    descricao = models.CharField(max_length=150)

    def __str__(self):
        return "{0} - {1}".format(self.numero, self.descricao)


class ModalidadeAplicacao(models.Model):
    numero = models.IntegerField()
    descricao = models.CharField(max_length=150)

    def __str__(self):
        return "{0} - {1}".format(self.numero, self.descricao)


class CategoriaEconomica(models.Model):
    numero = models.IntegerField()
    descricao = models.CharField(max_length=150)

    def __str__(self):
        return "{0} - {1}".format(self.numero, self.descricao)


class ElementoDespesa(models.Model):
    numero = models.IntegerField()
    descricao = models.CharField(max_length=150)

    def __str__(self):
        return "{0} - {1}".format(self.numero, self.descricao)


class ElementoDespesaSubItem(models.Model):
    elemento_despesa = models.ForeignKey(
        "ElementoDespesa", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    numero = models.IntegerField()
    descricao = models.CharField(max_length=150)

    def __str__(self):
        return "{0} - {1}".format(self.numero, self.descricao)


@to_search(
    [
        {"name": "grupo_despesa__numero", "type": "number"},
        {"name": "grupo_despesa__descricao", "type": "text"},
        {"name": "modalidade_aplicacao__numero", "type": "number"},
        {"name": "modalidade_aplicacao__descricao", "type": "text"},
        {"name": "categoria_economica__numero", "type": "number"},
        {"name": "categoria_economica__descricao", "type": "text"},
        {"name": "elemento_despesa__numero", "type": "number"},
        {"name": "elemento_despesa__descricao", "type": "text"},
    ]
)
class NaturezaDespesa(models.Model):

    class Meta:
        unique_together = [
            "grupo_despesa",
            "modalidade_aplicacao",
            "categoria_economica",
            "elemento_despesa",
        ]
        ordering = [
            "grupo_despesa__numero",
            "modalidade_aplicacao__numero",
            "categoria_economica__numero",
            "elemento_despesa__numero",
        ]

    grupo_despesa = models.ForeignKey(
        "GrupoDespesa", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # Parametro "on_delete" adicionado. (Django 2)
    modalidade_aplicacao = models.ForeignKey(
        "ModalidadeAplicacao", on_delete=models.CASCADE
    )
    categoria_economica = models.ForeignKey(
        "CategoriaEconomica", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    elemento_despesa = models.ForeignKey(
        "ElementoDespesa", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    numero_cache = models.CharField(max_length=100, null=True, blank=True)

    def save(self, force_insert=False, force_update=False):

        self.numero_cache = "%d.%d.%d.%d" % (
            self.grupo_despesa.numero,
            self.categoria_economica.numero,
            self.modalidade_aplicacao.numero,
            self.elemento_despesa.numero,
        )

        models.Model.save(self, force_insert, force_update)

    def __str__(self):
        return "%d.%d.%d.%d - %s" % (
            self.grupo_despesa.numero,
            self.categoria_economica.numero,
            self.modalidade_aplicacao.numero,
            self.elemento_despesa.numero,
            self.elemento_despesa.descricao,
        )
