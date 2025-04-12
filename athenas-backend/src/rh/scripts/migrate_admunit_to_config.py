import datetime

from rh.models import AdministrativeUnitConfig, UnidadeAdministrativa


def run(unit=None):
    if not unit:
        query = UnidadeAdministrativa.objects.filter(ativo=True)
    else:
        query = UnidadeAdministrativa.objects.filter(pk=unit)

    for ua in query:
        print(
            f"UNIDADE: {unit}\n CNAE: {ua.cnae_preponderant}\n TAX: {ua.tax_classification}"
        )
        config, isnew = AdministrativeUnitConfig.objects.get_or_create(
            administrative_unit=ua,
            cnae_preponderant=ua.cnae_preponderant,
            tax_classification=ua.tax_classification,
            start_validity=datetime.date(2021, 1, 1),
        )
        print(
            "%s CRIEi uma configuração nova %s" % ("NÃO" if not isnew else "", config)
        )
        ua.configs.add(config)
