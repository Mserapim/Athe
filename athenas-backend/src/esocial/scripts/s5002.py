# -.- coding: utf-8 -.-
import codecs
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from django.db.models import Q
from contrib.middleware import set_current_user
from esocial.models import BatchEvent, Event, S5002
from esocial.extractors.s1200 import ExtractorPayroll
from rh.gfp.models import ContraCheque, FolhaEvento
from rh.models import Servidor
from lxml import etree


set_current_user("athenas")


def find_xml_by(identifier):
    """Encontrar o xml de um evento pelo seu identificador."""
    ...


def run():
    def _process_file(event):
        print("---------------------------")
        xml_or_file_path = event.file_path
        xml_str = etree.parse(xml_or_file_path)

        if xml_str:
            # print(xml_str)
            xml_obj = xml_str.getroot()
            # print(xml_obj)
            elem = _find_irrf(event, xml_obj)
            if elem:
                print("ENCONTRADO")
                print(etree.tostring(elem, encoding="utf-8", pretty_print=True))
        else:
            print("Não foi possível ler o arquivo XML.")

    def _find_irrf(event, xml_obj):
        # print(xml_obj.findall('.//{*}evtIrrfBenef'))
        print(etree.tostring(xml_obj, encoding="utf-8", pretty_print=True))
        print(f"event: {event.identifier} - type: {type(event.identifier)}")
        for element in xml_obj.findall(".//{*}evtIrrfBenef"):
            for elem in element:
                identifier = elem.getparent().attrib["Id"]
                print(f"id: {identifier}")
                print(f"type: {type(identifier)}")
                if event.identifier == identifier:
                    return elem
                # event_connection = event.events.filter(
                #     identifier=element.getparent().attrib["Id"]
                # ).last()
                # if event_connection.acronym != "s3000":
                #     event_connection = event_connection.event
                # print(class_totalizer)
                # print(elem)
                # print(etree.tostring(elem, encoding='utf-8', pretty_print=True))
                # totalizer = event._evaluate_return_totalizers_data(class_totalizer, elem, event_connection)
                # write_xml(element, totalizer)
            return None

    # query = S5002.objects.valids_by_status().filter(competence_year=2023, competence_month=5)
    query = S5002.objects.valids_by_status().filter(
        competence_year=2023, competence_month=5
    )
    for event in query[0:1]:
        try:
            _process_file(event)
        except Exception as e:
            print(event.file_name, event.file_directory, event.file_path)
            print(e)
            continue


def ts5002():
    print("\nAnalisando S5002 e lançamentos 99900, 99100:")
    for s5002tot in S5002.objects.valids_by_status().filter(
        competence_year=2023, competence_month=5
    ):
        vlr_cr_men = 0
        for dm_dev in s5002tot.ide_trabalhador_dm_dev.filter():
            # print(f'per_ref: {dm_dev.dm_dev_per_ref} ide_dm_dev: {dm_dev.dm_dev_ide_dm_dev} tp_pgto: {dm_dev.dm_dev_tp_pgto} dt_pgto: {dm_dev.dm_dev_dt_pgto} cod_categ: {dm_dev.dm_dev_cod_categ}')
            # for dm_dev_info_ir in dm_dev.dm_dev_info_ir.filter():
            #     print(f'tp_info_ir: {dm_dev_info_ir.tp_info_ir} valor: {dm_dev_info_ir.valor}')
            msg = ""
            for tot_apur_men in dm_dev.tot_apur_men.filter():
                if msg:
                    msg += "\n"
                msg += f"cr_men: {tot_apur_men.cr_men} vlr_cr_men: {tot_apur_men.vlr_cr_men} vlr_cr_men_susp: {tot_apur_men.vlr_cr_men_susp}"
                vlr_cr_men += tot_apur_men.vlr_cr_men
            if not msg:
                msg = "Não possui apuração mensal."

        total_paycheck = paychecks_employee(s5002tot.ide_trabalhador_cpf_benef)
        if total_paycheck != vlr_cr_men:
            print(
                f"{s5002tot.ide_trabalhador_cpf_benef}: {Servidor.objects.filter(pessoa_fisica__cpf=s5002tot.ide_trabalhador_cpf_benef).first()}"
            )
            print(msg)
            print(
                f"TOTAL DE 99900, 99100: {total_paycheck}\nTOTAL ESOCIAL: {vlr_cr_men}\nDIF: {total_paycheck - vlr_cr_men}"
            )
            paychecks_employee(s5002tot.ide_trabalhador_cpf_benef, verbose=True)
            print("---------------------")

    print("\nAnalisando lançamentos 99900, 99100 que não estão em S5002:")
    paychecks = ContraCheque.objects.filter(
        folha__status__in=(3, 4),
        pensioner__isnull=True,
        folha__periodo__mes=5,
        folha__periodo__ano=2023,
        lancamentos__evento__numero__in=("99900", "99100"),
    )
    for paycheck in paychecks:
        s5002tot = (
            S5002.objects.valids_by_status()
            .filter(
                competence_year=2023,
                competence_month=5,
                ide_trabalhador_cpf_benef=paycheck.servidor.pessoa_fisica.cpf,
            )
            .first()
        )
        if s5002tot:
            vlr_cr_men = 0
            for dm_dev in s5002tot.ide_trabalhador_dm_dev.filter():
                # print(f'per_ref: {dm_dev.dm_dev_per_ref} ide_dm_dev: {dm_dev.dm_dev_ide_dm_dev} tp_pgto: {dm_dev.dm_dev_tp_pgto} dt_pgto: {dm_dev.dm_dev_dt_pgto} cod_categ: {dm_dev.dm_dev_cod_categ}')
                # for dm_dev_info_ir in dm_dev.dm_dev_info_ir.filter():
                #     print(f'tp_info_ir: {dm_dev_info_ir.tp_info_ir} valor: {dm_dev_info_ir.valor}')
                msg = ""
                for tot_apur_men in dm_dev.tot_apur_men.filter():
                    if msg:
                        msg += "\n"
                    msg += f"cr_men: {tot_apur_men.cr_men} vlr_cr_men: {tot_apur_men.vlr_cr_men} vlr_cr_men_susp: {tot_apur_men.vlr_cr_men_susp}"
                    vlr_cr_men += tot_apur_men.vlr_cr_men
                if not msg:
                    msg = "Não possui apuração mensal."

            total_paycheck = paycheck_payroll(s5002tot.ide_trabalhador_cpf_benef)
            if total_paycheck != vlr_cr_men:
                print(
                    f"{s5002tot.ide_trabalhador_cpf_benef}: {Servidor.objects.filter(pessoa_fisica__cpf=s5002tot.ide_trabalhador_cpf_benef).first()}"
                )
                print(msg)
                print(
                    f"TOTAL DE 99900, 99100: {total_paycheck}\nTOTAL ESOCIAL: {vlr_cr_men}\nDIF: {total_paycheck - vlr_cr_men}"
                )
                paycheck_payroll(s5002tot.ide_trabalhador_cpf_benef, verbose=True)
                print("---------------------")
        else:
            print(f"{paycheck} não possui S5002! {paycheck.servidor.pessoa_fisica.cpf}")


def run_create_totalizer():
    Event.objects.filter(
        competence_month=5, competence_year=2023, acronym__in=("s5002",)
    ).update(deleted=True)
    for batch in BatchEvent.objects.filter(
        events__pk__in=(
            Event.objects.valids_by_status()
            .filter(
                competence_month=5,
                competence_year=2023,
                acronym__in=(
                    # "s1200",
                    # "s1202",
                    # "s1207",
                    "s1210",
                ),
            )
            .values_list("pk", flat=True)
        )
    ).distinct():
        # print(batch)
        batch._set_process_return(
            update_batch=False,
            update_event=False,
            create_return_result=False,
            create_occurrence=False,
            release_send=False,
            totalizers=["s5002"],
        )


def paychecks_employee(registry_person, verbose=False):
    # print(ContraCheque.objects.filter(periodo__ano=2023, periodo__mes=5))
    total = 0
    query = ExtractorPayroll.all_entries_by_reference_esocial(
        month=5, year=2023, registry_person=registry_person
    ).filter(evento__numero__in=("99900", "99100"))
    for entry in query:
        if verbose:
            print(f"{entry}: {entry.valor}")
        total += entry.valor

    if verbose and not query.exists():
        print(
            f"Não possui evento 99900, 99100: {registry_person} {Servidor.objects.filter(pessoa_fisica__cpf=registry_person).first()}"
        )

    return total


def paycheck_payroll(registry_person, verbose=False):
    month = 5
    year = 2023
    total = 0
    # query = ExtractorPayroll.all_entries_by_reference_esocial(month=5, year=2023, registry_person=registry_person).filter(evento__numero__in=("99900", "99100"))
    paychecks = ContraCheque.objects.filter(
        folha__status__in=(3, 4),
        pensioner__isnull=True,
        folha__periodo__mes=month,
        folha__periodo__ano=year,
        servidor__pessoa_fisica__cpf=registry_person,
    )
    query = (
        FolhaEvento.objects.filter(
            pk__in=(
                pk
                for pk in paychecks.filter(
                    Q(
                        lancamentos__status__in=("CT", "CE", "BS"),
                        folha__status__in=(3, 4),
                    )
                )
                .filter(pensioner__isnull=True)
                .values_list("lancamentos__pk", flat=True)
            )
        )
        .filter(evento__numero__in=("99900", "99100"))
        .exclude(valor=0)
        .distinct()
    )
    for entry in query:
        total += entry.valor

    return total


if __name__ == "__main__":
    # run()
    # run_create_totalizer()
    ts5002()
