# -*- coding: utf-8 -*-

from django.db.models import (
    Model,
    CharField,
    IntegerField,
    DateField,
    SlugField,
    OneToOneField,
    ForeignKey,
    DateTimeField,
    BooleanField,
    TextField,
    CASCADE,
)

from edocs.protocolo.models import Protocolo, Referencia
from rh.models import Localidade
from django.template.defaultfilters import slugify
from django.db.models import Q


class Concurso(Model):
    nome = CharField(max_length=60, null=False, blank=False, verbose_name="Nome")
    dt_inicio = DateField(verbose_name="Data de inicio", null=True, blank=True)
    dt_fim = DateField(verbose_name="Data de fim", null=True, blank=True)
    promovido_por = IntegerField(
        choices=(
            (1, "CESAF"),
            (2, "CESAF E TERCEIRO"),
            (3, "TERCEIRO"),
        )
    )
    cidade_evento = ForeignKey(
        "rh.Localidade", related_name="concursos", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    data_cadastro = DateTimeField(auto_now_add=True)
    publicar = BooleanField(verbose_name="Publicar no site", default=False)
    descricao = TextField(verbose_name="Descrição para o Site", null=True, blank=True)
    slug = SlugField(max_length=384, verbose_name="Slug", null=True)

    class Meta:
        db_table = "concurso_concurso"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
            if Concurso.objects.filter(slug=self.slug).count() > 0:
                self.slug += str(Concurso.objects.latest("id").id + 1)
        super(Concurso, self).save(*args, **kwargs)

    def __str__(self):
        return "%s / %s" % (self.nome, self.cidade_evento)


class Vaga(Model):
    area = CharField("Área", max_length=384, db_index=True)
    # Parametro "on_delete" adicionado. (Django 2)
    local = ForeignKey(
        Localidade, verbose_name="Local", related_name="vagas", on_delete=CASCADE
    )
    quantidade = IntegerField("Quantidade", db_index=True)
    # Parametro "on_delete" adicionado. (Django 2)
    concurso = ForeignKey(
        Concurso, verbose_name="Concurso", related_name="vagas", on_delete=CASCADE
    )

    def __str__(self):
        return "%s - %s" % (self.area, self.local)


class Inscricao(Model):
    protocolo = OneToOneField(
        Protocolo, verbose_name="Protocolo", related_name="inscricao", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    vaga = ForeignKey(
        Vaga, verbose_name="Vaga", related_name="inscricoes", on_delete=CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    homologado = DateTimeField(null=True, blank=True)
    recurso = BooleanField(default=False, db_index=True)
    aprovado = BooleanField(null=True, blank=True)

    def check_recursos(self):
        refs = Referencia.objects.filter(protocolo=self.protocolo)
        recursos = Protocolo.objects.filter(
            referencias__in=refs, tipo_documento__nome="RECURSO-CONCURSO"
        ).exclude(~Q(data_finalizado=None))

        if recursos.count() > 0:
            self.recurso = True
        else:
            self.recurso = False
        self.save()

    def __str__(self):
        return "%s : %s / %s-%s" % (
            self.protocolo.codigo,
            self.vaga.area,
            self.vaga.local.nome,
            self.vaga.local.estado.sigla,
        )


class SelecaoEstagio(Model):
    curso = CharField("Curso", max_length=128)
    faculdade = CharField("Faculdade", max_length=384)
    # faculdade = models.ForeignKey('rh.OrgaoGeral', on_delete=CASCADE) # Parametro "on_delete" adicionado. (Django 2)
    matricula = CharField("Número de Matrícula", max_length=80, db_index=True)
    ano_periodo = CharField("Ano/Período", max_length=8)
    ano_conclusao = DateField("Previsão de Conclusão", db_index=True)
    disponibilidade = IntegerField(
        choices=((1, "Manhã"), (2, "Tarde")), null=True, default=1
    )
    inscricao = OneToOneField(
        Inscricao,
        verbose_name="Inscrição",
        related_name="para_estagio",
        on_delete=CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    def __str__(self):
        return "%s : %s" % (self.inscricao.vaga.concurso.nome, self.inscricao)
