# -.- coding: utf-8 -.-
import codecs
import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


from esocial.models import S5001, DetInfoPerRef


def write_s5001(message="", mode="a+"):
    with codecs.open("evaluation_inss_s5001.csv", mode, encoding="utf-8") as f:
        f.write(f"{message}\n")


def evaluation_s5001(competence_month, competence_year):
    print("\n\n\nListagem de diferença S5001")
    # write_s5001('S1200|MES|ANO|indMV|tpCR|vrCpSeg|vrDescSeg|Diferença|SERVIDOR', mode='w')
    write_s5001("matricula|tpCR|vrCpSeg|vrDescSeg", mode="w")
    count = 0
    result = []
    for s in (
        S5001.objects.filter(
            competence_month=competence_month, competence_year=competence_year
        )
        .filter(is_invalid_cache=False)
        .order_by("-competence_year", "-competence_month")
    ):
        info_cp_calc = s.info_cp_calc.last()

        if info_cp_calc:
            #     diff = float(abs(info_cp_calc.info_cp_calc_vr_cp_seg - info_cp_calc.info_cp_calc_vr_desc_seg))
            #     # if info_cp_calc.info_cp_calc_vr_cp_seg != info_cp_calc.info_cp_calc_vr_desc_seg and diff == 0.01:
            #     # if info_cp_calc.info_cp_calc_vr_cp_seg != info_cp_calc.info_cp_calc_vr_desc_seg and diff != 0:
            #     # if info_cp_calc.info_cp_calc_vr_cp_seg != info_cp_calc.info_cp_calc_vr_desc_seg or True:
            #     if True:
            #         count += 1
            s1200 = s.event_connection.event
            #         info_cp_calc_vr_cp_seg = info_cp_calc.info_cp_calc_vr_cp_seg
            #         info_cp_calc_vr_desc_seg = info_cp_calc.info_cp_calc_vr_desc_seg
            #         # message = f'{s1200}|{s1200.competence_month}|{s1200.competence_year}|{info_cp_calc.info_cp_calc_tp_cr}-{S5001.TP_CR.get(info_cp_calc.info_cp_calc_tp_cr)}|{s1200.info_mv_ind_mv}|{info_cp_calc_vr_cp_seg}|{info_cp_calc_vr_desc_seg}|{diff}|{s1200.employee()}'
            #         message = f'{s1200}|{s1200.competence_month}|{s1200.competence_year}|{s1200.info_mv_ind_mv}|{info_cp_calc_vr_cp_seg}|{info_cp_calc_vr_desc_seg}|{diff}|{s1200.employees().filter(ativo=True).last()}'
            #         # print(s1200, s1200.competence_month, s1200.competence_year, s1200.employees().filter(ativo=True).last())
            #         print(message)
            #         print(info_cp_calc_vr_cp_seg, info_cp_calc_vr_desc_seg, diff)
            #         # write_s5001(f'{s1200.employees().filter(ativo=True).last()} | {info_cp_calc_vr_cp_seg} | {info_cp_calc_vr_desc_seg}')
            buff = show_det_info_per_ref(s, competence_month, competence_year)
            name = s1200.employees().filter(ativo=True).last().pessoa_fisica.nome
            result.append(f"{name}\n{buff}")

    result.sort()
    for rs in result:
        write_s5001(rs)

    print(f"count: {count}")


def show_det_info_per_ref(s5001, competence_month, competence_year):
    result = ""
    for dipr in DetInfoPerRef.objects.filter(
        detinfoperref_infoperref__infoperref_infocategincid__infocategincid_ideestablot__ideestablot5001_s5001__pk=s5001.pk,
        # detinfoperref_infoperref__info_per_ref_per_ref=f"{competence_year}-0{competence_month}"
    ):
        buff = dipr.detinfoperref_infoperref.last().info_per_ref_per_ref
        buff += f" | decimo: {dipr.det_info_per_ref_ind13}"
        buff += f" | tp: {dipr.det_info_per_ref_tp_vr_per_ref}"
        buff += f" | vr: {dipr.det_info_per_ref_vr_per_ref}"
        result += f"{buff}\n"
    return result


if __name__ == "__main__":
    evaluation_s5001(competence_month=6, competence_year=2022)
