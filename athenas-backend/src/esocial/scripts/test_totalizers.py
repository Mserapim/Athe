# -.- coding: utf-8 -.-
import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from contrib.middleware import set_current_user
from esocial.models import S5001, S5002, S5011, S5012

set_current_user("gustavodettenborn")


def run():
    ts5001()
    ts5002()
    ts5011()
    ts5012()


def ts5001():
    print("\n\nS5001")
    for s5001tot in (
        S5001.objects.valids_by_status()
        .filter(ide_trabalhador_cpf_trab="93471947191")
        .exclude(is_invalid_cache=True)
    ):
        print(s5001tot.created_at, s5001tot.modified_at, s5001tot)
        print(f"ide_evento_nr_rec_arq_base: {s5001tot.ide_evento_nr_rec_arq_base}")
        print(f"ide_evento_ind_apuracao: {s5001tot.ide_evento_ind_apuracao}")
        print(f"ide_evento_per_apur: {s5001tot.ide_evento_per_apur}")
        print(f"ide_empregador_tp_insc: {s5001tot.ide_empregador_tp_insc}")
        print(f"ide_empregador_nr_insc: {s5001tot.ide_empregador_nr_insc}")
        print(f"ide_trabalhador_cpf_trab: {s5001tot.ide_trabalhador_cpf_trab}")
        print(f"info_cp_class_trib: {s5001tot.info_cp_class_trib}")

        print("infoCpCalc")
        for rs in s5001tot.info_cp_calc.filter():
            print(rs)
            print(f"info_cp_calc_tp_cr: {rs.info_cp_calc_tp_cr}")
            print(f"info_cp_calc_vr_cp_seg: {rs.info_cp_calc_vr_cp_seg}")
            print(f"info_cp_calc_vr_desc_seg: {rs.info_cp_calc_vr_desc_seg}")
        print("ide_estab_lot")
        for estab in s5001tot.ide_estab_lot.filter():
            print(estab)
            print(f"ide_estab_lot_tp_insc: {estab.ide_estab_lot_tp_insc}")
            print(f"ide_estab_lot_nr_insc: {estab.ide_estab_lot_nr_insc}")
            print(f"ide_estab_lot_cod_lotacao: {estab.ide_estab_lot_cod_lotacao}")
            for info_categ_incid in estab.info_categ_incid.filter():
                print(info_categ_incid)
                print(
                    f"info_categ_incid_matricula: {info_categ_incid.info_categ_incid_matricula}"
                )
                print(
                    f"info_categ_incid_cod_categ: {info_categ_incid.info_categ_incid_cod_categ}"
                )
                print(
                    f"info_categ_incid_ind_simples: {info_categ_incid.info_categ_incid_ind_simples}"
                )
                for per_ref in info_categ_incid.info_per_ref.filter():
                    print(per_ref.info_per_ref_per_ref)
                    for det in per_ref.det_info_per_ref.filter():
                        print(det)
                        print(f"det_info_per_ref_ind13: {det.det_info_per_ref_ind13}")
                        print(
                            f"det_info_per_ref_tp_vr_per_ref: {det.det_info_per_ref_tp_vr_per_ref}"
                        )
                        print(
                            f"det_info_per_ref_vr_per_ref: {det.det_info_per_ref_vr_per_ref}"
                        )
                print("INFOBASE")
                for info_base_cs in info_categ_incid.info_base_cs.filter():
                    print(info_base_cs)
                    print(f"info_base_cs_ind13: {info_base_cs.info_base_cs_ind13}")
                    print(
                        f"info_base_cs_tp_valor: {info_base_cs.info_base_cs_tp_valor}"
                    )
                    print(f"info_base_cs_valor: {info_base_cs.info_base_cs_valor}")


def ts5002():
    print("\n\nS5002")
    # for s5002tot in S5002.objects.valids_by_status().filter(competence_year=2023, competence_month=5):
    for s5002tot in (
        S5002.objects.valids_by_status()
        .filter(ide_trabalhador_cpf_benef="93471947191")
        .exclude(is_invalid_cache=True)
    ):
        print(s5002tot.created_at, s5002tot.modified_at)
        print(
            f"{s5002tot.event_connection.batches.count()} s5002tot: {s5002tot} | {s5002tot.event_connection} | {s5002tot.event_connection.batches.first().pk}"
        )
        print(f"ide_evento_nr_rec_arq_base: {s5002tot.ide_evento_nr_rec_arq_base}")
        print(f"ide_evento_ind_apuracao: {s5002tot.ide_evento_ind_apuracao}")
        print(f"ide_evento_per_apur: {s5002tot.ide_evento_per_apur}")
        print(f"ide_empregador_tp_insc: {s5002tot.ide_empregador_tp_insc}")
        print(f"ide_empregador_nr_insc: {s5002tot.ide_empregador_nr_insc}")
        print(f"ide_trabalhador_cpf_trab: {s5002tot.ide_trabalhador_cpf_benef}")

        print("dm_dev")
        for dm_dev in s5002tot.ide_trabalhador_dm_dev.filter():
            print(dm_dev)
            print(f"dm_dev_per_ref: {dm_dev.dm_dev_per_ref}")
            print(f"dm_dev_ide_dm_dev: {dm_dev.dm_dev_ide_dm_dev}")
            print(f"dm_dev_tp_pgto: {dm_dev.dm_dev_tp_pgto}")
            print(f"dm_dev_dt_pgto: {dm_dev.dm_dev_dt_pgto}")
            print(f"dm_dev_cod_categ: {dm_dev.dm_dev_cod_categ}")
            for dm_dev_info_ir in dm_dev.dm_dev_info_ir.filter():
                print(dm_dev_info_ir)
                print(f"tp_info_ir: {dm_dev_info_ir.tp_info_ir}")
                print(f"valor: {dm_dev_info_ir.valor}")

            for tot_apur_men in dm_dev.tot_apur_men.filter():
                print(tot_apur_men)
                print(f"cr_men: {tot_apur_men.cr_men}")
                print(f"vlr_cr_men: {tot_apur_men.vlr_cr_men}")
                print(f"vlr_cr_men_susp: {tot_apur_men.vlr_cr_men_susp}")


def ts5011():
    print("\n\nS5011")
    for s5011tot in (
        S5011.objects.valids_by_status().filter().exclude(is_invalid_cache=True)
    ):
        print(s5011tot)
        print(f"ide_evento_nr_rec_arq_base: {s5011tot.info_cs_nr_rec_arq_base}")
        print(f"ide_evento_nr_rec_arq_base: {s5011tot.info_cs_ind_exist_info}")
        print(f"ide_evento_ind_apuracao: {s5011tot.ide_evento_ind_apuracao}")
        print(f"ide_evento_per_apur: {s5011tot.ide_evento_per_apur}")
        print(f"ide_empregador_tp_insc: {s5011tot.ide_empregador_tp_insc}")
        print(f"ide_empregador_nr_insc: {s5011tot.ide_empregador_nr_insc}")
        print(f"info_cp_seg_vr_desc_cp: {s5011tot.info_cp_seg_vr_desc_cp}")
        print(f"info_cp_seg_vr_cp_seg: {s5011tot.info_cp_seg_vr_cp_seg}")
        print(f"info_contrib_class_trib: {s5011tot.info_contrib_class_trib}")
        print(f"info_pj_ind_coop: {s5011tot.info_pj_ind_coop}")
        print(f"info_pj_ind_constr: {s5011tot.info_pj_ind_constr}")
        print(f"info_pj_ind_subst_patr: {s5011tot.info_pj_ind_subst_patr}")
        print(f"info_pj_perc_red_contrib: {s5011tot.info_pj_perc_red_contrib}")
        print(f"info_pj_perc_transf: {s5011tot.info_pj_perc_transf}")
        print(f"info_at_conc_fator_mes: {s5011tot.info_at_conc_fator_mes}")
        print(f"info_at_conc_fator_13: {s5011tot.info_at_conc_fator_13}")

        print("ide_estab")
        for ide_estab in s5011tot.ide_estab.filter():
            print(ide_estab)
            print(f"ide_estab_tp_insc: {ide_estab.ide_estab_tp_insc}")
            print(f"ide_estab_nr_insc: {ide_estab.ide_estab_nr_insc}")
            print(f"info_estab_cnae_prep: {ide_estab.info_estab_cnae_prep}")
            print(f"info_estab_cnpj_prep: {ide_estab.info_estab_cnpj_prep}")
            print(f"info_estab_aliq_rat: {ide_estab.info_estab_aliq_rat}")
            print(f"info_estab_fap: {ide_estab.info_estab_fap}")
            print(f"info_estab_aliq_rat_ajust: {ide_estab.info_estab_aliq_rat_ajust}")
            print(f"info_estab_ref_aliq_rat: {ide_estab.info_estab_ref_aliq_rat}")
            print(f"info_estab_ref_fap: {ide_estab.info_estab_ref_fap}")
            print(
                f"info_estab_ref_aliq_rat_ajust: {ide_estab.info_estab_ref_aliq_rat_ajust}"
            )
            print(f"ide_lotacao_cod_lotacao: {ide_estab.ide_lotacao_cod_lotacao}")
            print(f"ide_lotacao_fpas: {ide_estab.ide_lotacao_fpas}")
            print(f"ide_lotacao_cod_tercs: {ide_estab.ide_lotacao_cod_tercs}")
            print(f"ide_lotacao_cod_tercs_susp: {ide_estab.ide_lotacao_cod_tercs_susp}")
            print(f"info_terc_susp_cod_terc: {ide_estab.info_terc_susp_cod_terc}")
            print("BASES REMUN")
            for bases_remun in ide_estab.bases_remun.filter():
                print(bases_remun)
                print(f"bases_remun_ind_incid: {bases_remun.bases_remun_ind_incid}")
                print(f"bases_remun_cod_categ: {bases_remun.bases_remun_cod_categ}")
                print(f"bases_cp_vr_bc_cp00: {bases_remun.bases_cp_vr_bc_cp00}")
                print(f"bases_cp_vr_bc_cp15: {bases_remun.bases_cp_vr_bc_cp15}")
                print(f"bases_cp_vr_bc_cp20: {bases_remun.bases_cp_vr_bc_cp20}")
                print(f"bases_cp_vr_bc_cp25: {bases_remun.bases_cp_vr_bc_cp25}")
                print(
                    f"bases_cp_vr_susp_bc_cp00: {bases_remun.bases_cp_vr_susp_bc_cp00}"
                )
                print(
                    f"bases_cp_vr_susp_bc_cp15: {bases_remun.bases_cp_vr_susp_bc_cp15}"
                )
                print(
                    f"bases_cp_vr_susp_bc_cp20: {bases_remun.bases_cp_vr_susp_bc_cp20}"
                )
                print(
                    f"bases_cp_vr_susp_bc_cp25: {bases_remun.bases_cp_vr_susp_bc_cp25}"
                )
                print(f"bases_cp_vr_desc_sest: {bases_remun.bases_cp_vr_desc_sest}")
                print(f"bases_cp_vr_calc_sest: {bases_remun.bases_cp_vr_calc_sest}")
                print(f"bases_cp_vr_desc_senat: {bases_remun.bases_cp_vr_desc_senat}")
                print(f"bases_cp_vr_calc_senat: {bases_remun.bases_cp_vr_calc_senat}")
                print(f"bases_cp_vr_sal_fam: {bases_remun.bases_cp_vr_sal_fam}")
                print(f"bases_cp_vr_sal_mat: {bases_remun.bases_cp_vr_sal_mat}")
            print("InfoCREstab")
            for info_cr_estab in ide_estab.info_cr_estab.filter():
                print(info_cr_estab)
                print(f"info_cr_estab_tp_cr: {info_cr_estab.info_cr_estab_tp_cr}")
                print(f"info_cr_estab_vr_cr: {info_cr_estab.info_cr_estab_vr_cr}")
                print(
                    f"info_cr_estab_vr_susp_cr: {info_cr_estab.info_cr_estab_vr_susp_cr}"
                )
        print("info_cr_contrib")
        for info_cr_contrib in s5011tot.info_cr_contrib.filter():
            print(info_cr_contrib)
            print(f"tp_cr: {info_cr_contrib.tp_cr}")
            print(f"vr_cr: {info_cr_contrib.vr_cr}")
            print(f"vr_cr_susp: {info_cr_contrib.vr_cr_susp}")


def ts5012():
    print("\n\nS5012")
    for s5012tot in (
        S5012.objects.valids_by_status().filter().exclude(is_invalid_cache=True)
    ):
        print(s5012tot)
        print(f"info_irrf_nr_rec_arq_base: {s5012tot.info_irrf_nr_rec_arq_base}")
        print(f"info_irrf_ind_exist_info: {s5012tot.info_irrf_ind_exist_info}")

        for tot_apur_men in s5012tot.tot_apur_men.filter():
            print(tot_apur_men)
            print(f"cr_men: {tot_apur_men.cr_men}")
            print(f"vlr_cr_men: {tot_apur_men.vlr_cr_men}")


if __name__ == "__main__":
    run()
