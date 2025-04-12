# -*- coding: utf-8 -*-


from rh.models import PessoaFisica as NaturalPerson, Documento as Document
from django.db.models.signals import post_save  # post_delete
from django.dispatch import receiver
from contrib.utils import getLogger

log = getLogger(__name__)
log.info("LOAD SIGNAL %s" % __name__)


@receiver(post_save, sender=NaturalPerson)
# @receiver(post_delete, sender=NaturalPerson)
def update_changed_natural_person(sender, instance, **kwargs):
    log.info("LOAD SIGNAL esocial %s: DIF: %s" % (__name__, instance.diff))
    """Salva PaycheckDifference se o lançamento é proveniente de uma diferença."""
    map_fields = {"cpf": "cpf", "nome": "nome", "data_nascimento": "dn"}

    if hasattr(instance, "qualification"):
        relevant_changes = set(list(instance.diff)).intersection(
            ["cpf", "nome", "data_nascimento"]
        )
        if relevant_changes:
            qualif = instance.qualification
            for k in relevant_changes:
                setattr(qualif, map_fields.get(k), getattr(instance, k))

            qualif.last_modified_person_by = instance.modified_by
            qualif.last_modified_person_at = instance.modified_at
            qualif.status = 1
            qualif.qualified = False
            qualif.info = ""
            qualif.cod_cpf_inv = 1
            qualif.cod_nis_inv = 1
            qualif.cod_nome_inv = 1
            qualif.cod_dn_inv = 1
            qualif.cod_orientacao_cpf = 1
            qualif.cod_orientacao_nis = 1
            qualif.separador = 1
            qualif.reg_desformatado = 1
            qualif.save()
        return True


@receiver(post_save, sender=Document)
# @receiver(post_delete, sender=NaturalPerson)
def update_changed_nis_natural_person(sender, instance, **kwargs):
    """Salva PaycheckDifference se o lançamento é proveniente de uma diferença."""
    log.info("LOAD SIGNAL esocial %s: DIF: %s" % (__name__, instance))
    # map_fields = {
    #     'cpf': 'cpf',
    #     'nome': 'nome',
    #     'data_nascimento': 'dn'
    # }

    natural_person = instance.naturalpersons.first()

    # if hasattr(instance, 'qualification'):
    # NIS/PIS/PASEP
    if instance.tipo_documento in [5, 6] and hasattr(natural_person, "qualification"):
        # relevant_changes = set(list(instance.diff)).intersection(['cpf', 'nome', 'data_nascimento'])
        # if relevant_changes:
        if "numero" in instance.diff:
            qualif = natural_person.qualification
            qualif.nis = instance.numero

            qualif.last_modified_person_by = instance.modified_by
            qualif.last_modified_person_at = instance.modified_at
            qualif.status = 1
            qualif.qualified = False
            qualif.info = ""
            qualif.cod_cpf_inv = 1
            qualif.cod_nis_inv = 1
            qualif.cod_nome_inv = 1
            qualif.cod_dn_inv = 1
            qualif.cod_orientacao_cpf = 1
            qualif.cod_orientacao_nis = 1
            qualif.separador = 1
            qualif.reg_desformatado = 1

        return True
