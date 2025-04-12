# -*- coding: utf-8 -*-


from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ("esocial", "0002_auto_20190329_1249"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="s2299",
            name="event_ptr",
        ),
        migrations.DeleteModel(
            name="S2299",
        ),
        migrations.CreateModel(
            name="ChildSupport",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "pen_alim_cpf_benef",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("pen_alim_dt_nascto_benef", models.DateField(null=True, blank=True)),
                (
                    "pen_alim_nm_benefic",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "pen_alim_vlr_pensao",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="CollectiveHealth",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "det_oper_cnpj_oper",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "det_oper_reg_ans",
                    models.CharField(max_length=6, null=True, blank=True),
                ),
                (
                    "det_oper_vr_pg_tit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="Demonstrative",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("dm_dev_ide_dm_dev", models.CharField(max_length=30)),
                ("dm_dev_cod_categ", models.PositiveIntegerField()),
                ("tp_insc", models.PositiveIntegerField(null=True, blank=True)),
                ("nr_insc", models.CharField(max_length=15, null=True, blank=True)),
                ("cod_lotacao", models.CharField(max_length=30, null=True, blank=True)),
                ("qtd_dias_av", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "info_compl_cont_cod_cbo",
                    models.CharField(max_length=6, null=True, blank=True),
                ),
                (
                    "info_compl_cont_nat_atividade",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_compl_cont_qtd_dias_trab",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="DemonstrativeItem",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("matricula", models.CharField(max_length=30, null=True, blank=True)),
                ("cod_rubr", models.CharField(max_length=30, null=True, blank=True)),
                ("ide_tab_rubr", models.CharField(max_length=8, null=True, blank=True)),
                (
                    "qtd_rubr",
                    models.DecimalField(
                        null=True, max_digits=6, decimal_places=2, blank=True
                    ),
                ),
                (
                    "fator_rubr",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "vr_unit",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "vr_rubr",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "pen_alim",
                    models.ManyToManyField(
                        related_name="demostrativeitems", to="esocial.ChildSupport"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="DetPgtoAnt",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "det_pgto_ant_cod_categ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="DetPgtoFer",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "det_pgto_fer_cod_categ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "det_pgto_fer_matricula",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("det_pgto_fer_dt_ini_goz", models.DateField(null=True, blank=True)),
                (
                    "det_pgto_fer_qt_dias",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "det_pgto_fer_vr_liq",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_pgto_fer_det_rubr_fer",
                    models.ManyToManyField(
                        related_name="det_pgto_fer_det_rubr_fer_register_S1210",
                        to="esocial.DemonstrativeItem",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="HealthPlan",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "det_plano_tp_dep",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "det_plano_cpf_dep",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "det_plano_nm_dep",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("det_plano_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "det_plano_vlr_pg_dep",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="IdeAdc",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("ide_adc_dt_ac_conv", models.DateField(null=True, blank=True)),
                (
                    "ide_adc_tp_ac_conv",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "ide_adc_comp_ac_conv",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                ("ide_adc_dt_ef_ac_conv", models.DateField(null=True, blank=True)),
                (
                    "ide_adc_dsc",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "ide_adc_remun_suc",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="IdePeriod",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "ide_periodo_per_ref",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "itens_remun",
                    models.ManyToManyField(
                        related_name="ideperiod_demonstrativeitem",
                        to="esocial.DemonstrativeItem",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="InfoPgto",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("info_pgto_dt_pgto", models.DateField()),
                ("info_pgto_tp_pgto", models.PositiveIntegerField()),
                ("info_pgto_ind_res_br", models.CharField(max_length=1)),
                (
                    "det_pgto_ben_pr_per_ref",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
                (
                    "det_pgto_ben_pr_ide_dm_dev",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "det_pgto_ben_pr_ind_pgto_tt",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "det_pgto_ben_pr_vr_liq",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "det_pgto_ben_pr_info_pgto_parc",
                    models.ManyToManyField(
                        related_name="det_pgto_ben_pr_info_pgto_parc_register_S1210",
                        to="esocial.DemonstrativeItem",
                    ),
                ),
                (
                    "det_pgto_ben_pr_ret_pgto_tot",
                    models.ManyToManyField(
                        related_name="det_pgto_ben_pr_ret_pgto_tot_register_S1210",
                        to="esocial.DemonstrativeItem",
                    ),
                ),
                (
                    "info_pgto_det_pgto_ant",
                    models.ManyToManyField(
                        related_name="info_pgto_det_pgto_ant_register_S1210",
                        to="esocial.DetPgtoAnt",
                    ),
                ),
                (
                    "info_pgto_det_pgto_fer",
                    models.ManyToManyField(
                        related_name="info_pgto_det_pgto_fer_register_S1210",
                        to="esocial.DetPgtoFer",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="InfoPgtoAnt",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "info_pgto_ant_tp_bc_irrf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "info_pgto_ant_vr_bc_irrf",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="PaymentDetail",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("per_ref", models.CharField(max_length=7, null=True, blank=True)),
                ("ide_dm_dev", models.CharField(max_length=30, null=True, blank=True)),
                ("ind_pgto_tt", models.CharField(max_length=1, null=True, blank=True)),
                (
                    "vr_liq",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                ("nr_rec_arq", models.CharField(max_length=40, null=True, blank=True)),
                (
                    "info_pgto_parc",
                    models.ManyToManyField(
                        related_name="parcpayments", to="esocial.DemonstrativeItem"
                    ),
                ),
                (
                    "ret_pgto_tot",
                    models.ManyToManyField(
                        related_name="totalpayments", to="esocial.DemonstrativeItem"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="RemunPerApur",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("matricula", models.CharField(max_length=30, null=True, blank=True)),
                ("ind_simples", models.PositiveIntegerField(null=True, blank=True)),
                ("grau_exp", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "det_oper",
                    models.ManyToManyField(
                        related_name="demonstrative_collectivehealth",
                        to="esocial.CollectiveHealth",
                    ),
                ),
                (
                    "itens_remun",
                    models.ManyToManyField(
                        related_name="demonstrative_demonstrativeitem",
                        to="esocial.DemonstrativeItem",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="RescissionDemonstrative",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("dm_dev_ide_dm_dev", models.CharField(max_length=30)),
                ("tp_insc", models.PositiveIntegerField(null=True, blank=True)),
                ("nr_insc", models.CharField(max_length=15, null=True, blank=True)),
                ("cod_lotacao", models.CharField(max_length=30, null=True, blank=True)),
                ("grau_exp", models.PositiveIntegerField(null=True, blank=True)),
                ("ind_simples", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "det_oper",
                    models.ManyToManyField(
                        related_name="rescissiondemonstratives",
                        to="esocial.CollectiveHealth",
                    ),
                ),
                (
                    "det_verbas",
                    models.ManyToManyField(
                        related_name="rescissiondemonstratives",
                        to="esocial.DemonstrativeItem",
                    ),
                ),
                (
                    "ide_adc",
                    models.ManyToManyField(
                        related_name="rescissiondemonstratives", to="esocial.IdeAdc"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1200",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_trabalhador_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_trabalhador_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("info_mv_ind_mv", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "remun_outr_empr_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "remun_outr_empr_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "remun_outr_empr_cod_categ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "remun_outr_empr_vlr_remun_oe",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_complem_nm_trab",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                ("info_complem_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "sucessao_vinc_tp_insc_ant",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "sucessao_vinc_cnpj_empreg_ant",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "sucessao_vinc_matric_ant",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("sucessao_vinc_dt_adm", models.DateField(null=True, blank=True)),
                (
                    "sucessao_vinc_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "dm_dev",
                    models.ManyToManyField(
                        related_name="itens_remun_register_s1200",
                        to="esocial.Demonstrative",
                    ),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1210",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_benef_cpf_benef", models.CharField(max_length=11)),
                (
                    "deps_vr_ded_dep",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "ide_pais_cod_pais",
                    models.CharField(max_length=3, null=True, blank=True),
                ),
                (
                    "ide_pais_ind_nif",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "ide_pais_nif_benef",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                (
                    "end_ext_dsc_lograd",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "end_ext_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "end_ext_complem",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "end_ext_bairro",
                    models.CharField(max_length=90, null=True, blank=True),
                ),
                (
                    "end_ext_nm_cid",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "end_ext_cod_postal",
                    models.CharField(max_length=12, null=True, blank=True),
                ),
                (
                    "info_pgto",
                    models.ManyToManyField(
                        related_name="info_pgto_register_S1210", to="esocial.InfoPgto"
                    ),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S1299",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                (
                    "ide_resp_inf_nm_resp",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
                (
                    "ide_resp_inf_cpf_resp",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "ide_resp_inf_telefone",
                    models.CharField(max_length=13, null=True, blank=True),
                ),
                (
                    "ide_resp_inf_email",
                    models.CharField(max_length=60, null=True, blank=True),
                ),
                ("info_fech_evt_remun", models.CharField(max_length=1)),
                ("info_fech_evt_pgtos", models.CharField(max_length=1)),
                ("info_fech_evt_aq_prod", models.CharField(max_length=1)),
                ("info_fech_evt_com_prod", models.CharField(max_length=1)),
                ("info_fech_evt_contrat_av_np", models.CharField(max_length=1)),
                ("info_fech_evt_info_compl_per", models.CharField(max_length=1)),
                (
                    "info_fech_comp_sem_movto",
                    models.CharField(max_length=7, null=True, blank=True),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.CreateModel(
            name="S2306",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_trab_sem_vinculo_cpf_trab", models.CharField(max_length=11)),
                (
                    "ide_trab_sem_vinculo_nis_trab",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("ide_trab_sem_vinculo_cod_categ", models.PositiveIntegerField()),
                ("info_tsv_alteracao_dt_alteracao", models.DateField()),
                (
                    "info_tsv_alteracao_nat_atividade",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "cargo_funcao_cod_cargo",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "cargo_funcao_cod_funcao",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "remuneracao_vr_sal_fx",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "remuneracao_und_sal_fixo",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "remuneracao_dsc_sal_var",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "info_estagiario_nat_estagio",
                    models.CharField(max_length=1, null=True, blank=True),
                ),
                (
                    "info_estagiario_niv_estagio",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "info_estagiario_area_atuacao",
                    models.CharField(max_length=50, null=True, blank=True),
                ),
                (
                    "info_estagiario_nr_apol",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                (
                    "info_estagiario_vlr_bolsa",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_estagiario_dt_prev_term",
                    models.DateField(null=True, blank=True),
                ),
                (
                    "inst_ensino_cnpj_inst_ensino",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "inst_ensino_nm_razao",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "inst_ensino_dsc_lograd",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "inst_ensino_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "inst_ensino_bairro",
                    models.CharField(max_length=90, null=True, blank=True),
                ),
                (
                    "inst_ensino_cep",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "inst_ensino_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "inst_ensino_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "age_integracao_cnpj_agnt_integ",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "age_integracao_nm_razao",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "age_integracao_dsc_lograd",
                    models.CharField(max_length=100, null=True, blank=True),
                ),
                (
                    "age_integracao_nr_lograd",
                    models.CharField(max_length=10, null=True, blank=True),
                ),
                (
                    "age_integracao_bairro",
                    models.CharField(max_length=90, null=True, blank=True),
                ),
                (
                    "age_integracao_cep",
                    models.CharField(max_length=8, null=True, blank=True),
                ),
                (
                    "age_integracao_cod_munic",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "age_integracao_uf",
                    models.CharField(max_length=2, null=True, blank=True),
                ),
                (
                    "supervisor_estagio_cpf_supervisor",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "supervisor_estagio_nm_superv",
                    models.CharField(max_length=70, null=True, blank=True),
                ),
            ],
            bases=("esocial.event",),
        ),
        migrations.AddField(
            model_name="event",
            name="end_validity",
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="event",
            name="start_validity",
            field=models.DateField(
                default=datetime.datetime(2019, 5, 28, 13, 55, 43, 162782), blank=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ideprocesso",
            name="ide_processo_tp_trib",
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="event",
            name="process_status",
            field=models.PositiveIntegerField(
                default=1,
                choices=[
                    (1, "Aguardando empacotamento"),
                    (2, "Aguardando finaliza\xe7\xe3o de depend\xeancia"),
                    (3, "Empacotado e aguardando envio"),
                    (4, "Enviado e aguardando processamento"),
                    (5, "Depend\xeancia n\xe3o satisfeita"),
                    (201, "Sucesso"),
                    (202, "Sucesso com advert\xeancia"),
                    (301, "Erro Servidor"),
                    (401, "Erro no conte\xfado do evento"),
                    (402, "Schema inv\xe1lido"),
                    (403, "Leiaute inv\xe1lido"),
                    (404, "Erro do certificado digital"),
                    (405, "Erro na assinatura evento"),
                    (406, "Evento n\xe3o pertence ao grupo"),
                    (407, "Regra de preced\xeancia de eventos n\xe3o seguida"),
                    (408, "Erro na integra\xe7\xe3o com o sistema CNPJ / CPF"),
                    (
                        409,
                        "Erro na integra\xe7\xe3o - Procura\xe7\xe3o Eletr\xf4nica RFB",
                    ),
                    (
                        410,
                        "Erro na integra\xe7\xe3o - Procura\xe7\xe3o Eletr\xf4nica Caixa",
                    ),
                    (411, "Assinante inv\xe1lido"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="s1200",
            name="proc_jud_trab",
            field=models.ManyToManyField(
                related_name="proc_jud_trab_register_s1200", to="esocial.IdeProcesso"
            ),
        ),
        migrations.AddField(
            model_name="infopgto",
            name="info_pgto_det_pgto_fl",
            field=models.ManyToManyField(
                related_name="info_pgto_det_pgto_fl_register_S1210",
                to="esocial.PaymentDetail",
            ),
        ),
        migrations.AddField(
            model_name="ideadc",
            name="ide_periodo",
            field=models.ManyToManyField(
                related_name="ideadc_ideperiod", to="esocial.IdePeriod"
            ),
        ),
        migrations.AddField(
            model_name="detpgtoant",
            name="info_pgto_ant",
            field=models.ForeignKey(
                related_name="info_pgto_ant_register_S1210",
                to="esocial.InfoPgtoAnt",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="demonstrative",
            name="ide_adc",
            field=models.ManyToManyField(
                related_name="demonstrative_ideadc", to="esocial.IdeAdc"
            ),
        ),
        migrations.AddField(
            model_name="demonstrative",
            name="remun_per_apur",
            field=models.ManyToManyField(
                related_name="remunperapur_trybutaryestablishment",
                to="esocial.RemunPerApur",
            ),
        ),
        migrations.AddField(
            model_name="collectivehealth",
            name="det_plano",
            field=models.ManyToManyField(
                related_name="collectivehealth_healthplan", to="esocial.HealthPlan"
            ),
        ),
        migrations.CreateModel(
            name="S2299",
            fields=[
                (
                    "event_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="esocial.Event",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("xmlns", models.CharField(max_length=256)),
                (
                    "ide_evento_tp_amb",
                    models.PositiveIntegerField(
                        default=2,
                        choices=[
                            (1, "Produ\xe7\xe3o"),
                            (2, "Pr\xe9-produ\xe7\xe3o - dados reais"),
                            (3, "Pr\xe9-produ\xe7\xe3o - dados fict\xedcios"),
                        ],
                    ),
                ),
                ("ide_evento_proc_emi", models.PositiveIntegerField(default=1)),
                ("ide_evento_ver_proc", models.CharField(max_length=20)),
                (
                    "ide_evento_ind_apuracao",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "MENSAL"), (2, "ANUAL(13 SAL\xc1RIO)")]
                    ),
                ),
                ("ide_evento_per_apur", models.CharField(max_length=7)),
                (
                    "ide_evento_ind_retif",
                    models.PositiveIntegerField(
                        default=1, choices=[(1, "ORIGINAL"), (2, "RETIFICADO")]
                    ),
                ),
                (
                    "ide_evento_nr_recibo",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                ("ide_empregador_tp_insc", models.PositiveIntegerField(default=1)),
                ("ide_empregador_nr_insc", models.CharField(max_length=15)),
                ("ide_vinculo_cpf_trab", models.CharField(max_length=11)),
                ("ide_vinculo_nis_trab", models.CharField(max_length=11)),
                ("ide_vinculo_matricula", models.CharField(max_length=30)),
                ("info_deslig_mtv_deslig", models.CharField(max_length=2)),
                ("info_deslig_dt_deslig", models.DateField()),
                ("info_deslig_ind_pagto_api", models.CharField(max_length=1)),
                (
                    "info_deslig_dt_proj_fim_api",
                    models.DateField(null=True, blank=True),
                ),
                ("info_deslig_pens_alim", models.PositiveIntegerField()),
                (
                    "info_deslig_perc_aliment",
                    models.DecimalField(
                        null=True, max_digits=5, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_deslig_vr_alim",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "info_deslig_nr_cert_obito",
                    models.CharField(max_length=32, null=True, blank=True),
                ),
                (
                    "info_deslig_nr_proc_trab",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("info_deslig_ind_cumpr_parc", models.PositiveIntegerField()),
                (
                    "info_deslig_qtd_dias_interm",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "observacoes_observacao",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                (
                    "sucessao_vinc_tp_insc_suc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "sucessao_vinc_cnpj_sucessora",
                    models.CharField(max_length=14, null=True, blank=True),
                ),
                (
                    "transf_tit_cpf_substituto",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                ("transf_tit_dt_nascto", models.DateField(null=True, blank=True)),
                (
                    "mudanca_cpf_novo_cpf",
                    models.CharField(max_length=11, null=True, blank=True),
                ),
                (
                    "info_trab_interm_cod_conv",
                    models.CharField(max_length=30, null=True, blank=True),
                ),
                ("info_mv_ind_mv", models.PositiveIntegerField(null=True, blank=True)),
                (
                    "remun_outr_empr_tp_insc",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "remun_outr_empr_nr_insc",
                    models.CharField(max_length=15, null=True, blank=True),
                ),
                (
                    "remun_outr_empr_cod_categ",
                    models.PositiveIntegerField(null=True, blank=True),
                ),
                (
                    "remun_outr_empr_vlr_remun_oe",
                    models.DecimalField(
                        null=True, max_digits=14, decimal_places=2, blank=True
                    ),
                ),
                (
                    "proc_cs_nr_proc_jud",
                    models.CharField(max_length=20, null=True, blank=True),
                ),
                ("quarentena_dt_fim_quar", models.DateField(null=True, blank=True)),
                (
                    "consig_fgts_ins_consig",
                    models.CharField(max_length=5, null=True, blank=True),
                ),
                (
                    "consig_fgts_nr_contr",
                    models.CharField(max_length=40, null=True, blank=True),
                ),
                (
                    "dm_dev",
                    models.ManyToManyField(
                        related_name="dm_dev_register_s2299",
                        to="esocial.RescissionDemonstrative",
                    ),
                ),
                (
                    "proc_jud_trab",
                    models.ManyToManyField(
                        related_name="proc_jud_trab_register_s2299",
                        to="esocial.IdeProcesso",
                    ),
                ),
            ],
            bases=("esocial.event",),
        ),
    ]
