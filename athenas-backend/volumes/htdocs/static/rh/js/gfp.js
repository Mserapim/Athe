
if (typeof (toolkit) == "undefiend" || typeof (toolkit.util) == "undefined" || typeof (toolkit.widget)) {

    toolkit.gfp = {

    }

    toolkit.gfp.Configuracao = function (folha) {

    }

    toolkit.gfp.FolhaMensage = Ext.extend(
        toolkit.restful.FormPanel,
        {
            router: toolkit.util.Normalize.controller_action('GFPFolhaMensagemRestful'),

            getFormPanel: function () {

                if (!this.formPanel)
                    this.formPanel = new Ext.form.FormPanel({
                        frame: true,
                        labelAlign: 'top',
                        items: [
                            {
                                name: 'texto',
                                fieldLabel: 'Mensagem',
                                xtype: 'xhtmleditor',
                                height: 240,
                                value: this.values ? this.values.texto : ''
                            }
                        ]
                    });

                return this.formPanel;
            },

            constructor: function (cf) {

                Ext.apply(
                    cf,
                    {
                        title: 'Envio de Mensagens',
                        modal: true,
                        closable: true,
                        border: false,
                        width: 532
                    }
                );

                toolkit.gfp.FolhaMensage.superclass.constructor.call(this, cf);
            }
        }
    );

    toolkit.gfp.FolhaPagamentoField = Ext.extend(
        Ext.Panel,
        {
            constructor: function (cf) {

                Ext.applyIf(
                    cf,
                    {
                        names: {
                            ano: 'folha_ano',
                            mes: 'folha_mes',
                            tipo: 'folha_tipo'
                        },
                        values: {
                            ano: null,
                            mes: null,
                            tipo: null
                        }
                    }
                );

                var defaults = {
                    layout: 'hbox',
                    fieldLabel: 'undefined',
                    frame: true,
                    defaults: {
                        xtype: 'panel',
                        layout: 'form',
                        labelAlign: 'top',
                        flex: 1.0,
                        border: false,
                        defaults: {
                            width: 130
                        }
                    },
                    items: [
                        {
                            width: 70,
                            items: [
                                {
                                    fieldLabel: 'Ano',
                                    xtype: 'numberfield',
                                    name: cf.names.ano,
                                    allowDecimals: false,
                                    minValue: 1997,
                                    width: 60,
                                    value: cf.values.ano ? cf.values.ano : undefined
                                }
                            ]
                        },
                        {
                            width: 120,
                            items: [
                                {
                                    fieldLabel: 'Mês',
                                    xtype: 'combo',
                                    width: 110,
                                    hiddenName: cf.names.mes,
                                    store: [
                                        [1, 'JANEIRO'],
                                        [2, 'FEVEREIRO'],
                                        [3, 'MARÇO'],
                                        [4, 'ABRIL'],
                                        [5, 'MAIO'],
                                        [6, 'JUNHO'],
                                        [7, 'JULHO'],
                                        [8, 'AGOSTO'],
                                        [9, 'SETEMBRO'],
                                        [10, 'OUTUBRO'],
                                        [11, 'NOVEMBRO'],
                                        [12, 'DEZEMBRO'],
                                        [13, '13º SALÁRIO'],
                                    ],
                                    triggerAction: 'all',
                                    value: cf.values.mes ? cf.values.mes : undefined
                                },
                            ]
                        },
                        {
                            labelAlign: 'top',
                            listeners: {
                                render: function (p) {
                                    var fix = 200;
                                    p.setWidth(p.ownerCt.getBox().width - fix);
                                    p.getComponent(0).setWidth(p.ownerCt.getBox().width - (fix + 5));
                                }
                            },
                            width: 250,
                            items: [
                                {
                                    xtype: "rest-autocompletefield",
                                    fieldLabel: "Tipo de Folha",
                                    allowBlank: false,
                                    rest: "rh.gfp.payroll.PayrollTypeRestful",
                                    name: cf.names.tipo,
                                    value: (cf.values.tipo ? cf.values.tipo : '')
                                }
                            ]
                        }
                    ]
                };

                Ext.applyIf(cf, defaults);

                toolkit.gfp.FolhaPagamentoField.superclass.constructor.call(this, cf);
            }
        }
    )

    toolkit.gfp.Configuracao = Ext.extend(
        Ext.Panel,
        {
            getFormPanel: function () {
                if (!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        border: false,
                        labelWidth: 150,
                        labelAlign: 'right',
                        defaults: {
                            defaults: {
                                width: 425
                            }
                        },
                        items: [
                            {
                                xtype: 'fieldset',
                                title: 'Informações da Instituição',
                                collapsible: true,
                                items: [
                                    {
                                        xtype: "rest-autocompletefield",
                                        fieldLabel: "Instituição",
                                        allowBlank: false,
                                        rest: "rh.administrativeunit.Restful",
                                        name: "orgao",
                                        value: this.values.instituicao.orgao ? this.values.instituicao.orgao : undefined
                                    },
                                    {
                                        xtype: "rest-autocompletefield",
                                        fieldLabel: "Responsável",
                                        allowBlank: false,
                                        rest: "rh.employee.Restful",
                                        name: "responsavel_orgao",
                                        value: this.values.instituicao.responsavel ? this.values.instituicao.responsavel : undefined
                                    },
                                    {
                                        fieldLabel: 'Telefone',
                                        name: 'telefone_responsavel_orgao',
                                        xtype: 'fonefield',
                                        value: this.values.instituicao.telefone ? this.values.instituicao.telefone : undefined
                                    },
                                    {
                                        fieldLabel: 'CEP',
                                        name: 'cep_orgao',
                                        xtype: 'cepfield',
                                        value: this.values.instituicao.cep ? this.values.instituicao.cep : undefined
                                    },
                                    {
                                        fieldLabel: 'Endereço',
                                        name: 'endereco_orgao',
                                        xtype: 'textfield',
                                        value: this.values.instituicao.endereco ? this.values.instituicao.endereco : undefined
                                    },
                                    {
                                        fieldLabel: 'Bairro',
                                        name: 'bairro_orgao',
                                        xtype: 'textfield',
                                        value: this.values.instituicao.bairro ? this.values.instituicao.bairro : undefined
                                    },
                                    {
                                        fieldLabel: 'Complemento',
                                        name: 'complemento_orgao',
                                        xtype: 'textfield',
                                        value: this.values.instituicao.complemento ? this.values.instituicao.complemento : undefined
                                    }
                                ]
                            },
                            {
                                xtype: 'fieldset',
                                title: 'Informações da Folha de Pagamento',
                                collapsible: true,
                                items: [
                                    {
                                        xtype: "rest-autocompletefield",
                                        fieldLabel: "Responsável",
                                        allowBlank: false,
                                        rest: "rh.employee.Restful",
                                        name: "responsavel_gfp",
                                        value: this.values.folha.responsavel ? this.values.folha.responsavel : undefined
                                    },
                                    {
                                        fieldLabel: 'Telefone',
                                        name: 'telefone_responsavel_gfp',
                                        xtype: 'fonefield',
                                        value: this.values.folha.telefone ? this.values.folha.telefone : undefined
                                    },
                                    {
                                        fieldLabel: 'Fax',
                                        name: 'fax_gfp',
                                        xtype: 'fonefield',
                                        value: this.values.folha.fax ? this.values.folha.fax : undefined
                                    },
                                    {
                                        fieldLabel: 'Endereço Eletrônico',
                                        name: 'email_gfp',
                                        xtype: 'textfield',
                                        value: this.values.folha.email ? this.values.folha.email : undefined
                                    },
                                    // {
                                    //     xtype: "rest-autocompletefield",
                                    //     fieldLabel: "Folha",
                                    //     allowBlank: false,
                                    //     rest: "rh.gfp.payroll.PayrollRestful",
                                    //     name: "folha",
                                    //     value: this.values.folha.folha ? this.values.folha.folha : undefined
                                    // },
                                    {
                                        xtype: "rest-autocompletefield",
                                        fieldLabel: "INSS",
                                        allowBlank: false,
                                        rest: "rh.person.legalperson.Restful",
                                        name: "inss",
                                        value: this.values.folha.inss ? this.values.folha.inss : undefined
                                    },
                                    // {
                                    //     fieldLabel: 'INSS', //
                                    //     name: 'inss',
                                    //     xtype: 'autocomplete',
                                    //     controller: 'RHPessoaJuridica',
                                    //     father: 'GFPConfiguracao',
                                    //     store: new Ext.data.JsonStore({
                                    //         url: toolkit.util.Normalize.controller_action(
                                    //             'GFPConfiguracao',
                                    //             'autocomplete',
                                    //             ['PessoaJuridica']
                                    //         ),
                                    //         root: 'result',
                                    //         fields: ['id', 'description']
                                    //     }),
                                    //     displayField: 'description',
                                    //     valueField: 'id',
                                    //     value: this.values.folha.inss ? this.values.folha.inss : undefined
                                    // },
                                ]
                            },
                            {
                                xtype: 'fieldset',
                                title: 'Classificação',
                                collapsible: true,
                                items: [
                                    {
                                        fieldLabel: 'Classificação Tributária',
                                        maxLength: 2,
                                        name: 'class_trib',
                                        xtype: 'textfield',
                                        value: this.values.instituicao.class_trib ? this.values.instituicao.class_trib : '99'
                                    },
                                    {
                                        fieldLabel: 'Natureza Jurídica',
                                        maxLength: 5,
                                        name: 'nat_jurid',
                                        xtype: 'textfield',
                                        value: this.values.instituicao.nat_jurid ? this.values.instituicao.nat_jurid : '1171'
                                    },
                                    {
                                        fieldLabel: 'Número SIAFI',
                                        name: 'nr_siafi',
                                        xtype: 'textfield',
                                        value: this.values.instituicao.nr_siafi ? this.values.instituicao.nr_siafi : undefined
                                    },
                                ]
                            },
                            {
                                xtype: 'fieldset',
                                title: 'Informações relativas ao ente(federativo, estadual ou municipal)',
                                collapsible: true,
                                items: [
                                    {
                                        fieldLabel: 'Ente Federativo',
                                        name: 'cod_ente_federativo',
                                        rest: 'rh.person.legalperson.Restful',
                                        xtype: 'rest-autocompletefield',
                                        value: this.values.instituicao.cod_ente_federativo ? this.values.instituicao.cod_ente_federativo : undefined
                                    },
                                    {
                                        xtype: 'rest-autocompletefield',
                                        fieldLabel: 'Município',
                                        allowBlank: false,
                                        rest: 'rh.localidade.Restful',
                                        name: 'cod_munic',
                                        value: this.values.instituicao.cod_munic ? this.values.instituicao.cod_munic : undefined,
                                    },
                                    {
                                        fieldLabel: 'Ente possui RPPS',
                                        xtype: 'combo',
                                        hiddenName: 'ind_rpps',
                                        name: 'ind_rpps',
                                        store: [
                                            ['S', 'SIM'],
                                            ['N', 'NÃO']
                                        ],
                                        allowBlank: false,
                                        triggerAction: 'all',
                                        value: this.values.instituicao.ind_rpps ? this.values.instituicao.ind_rpps : undefined,
                                    },
                                    {
                                        fieldLabel: 'Poder que se refere o subteto',
                                        xtype: 'combo',
                                        hiddenName: 'subteto',
                                        name: 'subteto',
                                        store: [
                                            [1, 'EXECUTIVO'],
                                            [2, 'JUDICIÁRIO'],
                                            [3, 'LEGISLATIVO'],
                                            [9, 'TODOS OS PODERES'],
                                        ],
                                        allowBlank: false,
                                        triggerAction: 'all',
                                        value: this.values.instituicao.subteto ? this.values.instituicao.subteto : undefined
                                    },
                                    {
                                        fieldLabel: 'Valor do subteto',
                                        maxLength: 14,
                                        name: 'vr_subteto',
                                        xtype: 'textfield',
                                        value: this.values.instituicao.vr_subteto ? this.values.instituicao.vr_subteto : undefined
                                    },
                                    {
                                        fieldLabel: 'Alíquota RAT',
                                        maxLength: 1,
                                        name: 'aliq_rat',
                                        xtype: 'textfield',
                                        value: this.values.instituicao.vr_subteto ? this.values.instituicao.aliq_rat : undefined
                                    },
                                    {
                                        fieldLabel: 'FAP',
                                        allowBlank: true,
                                        maxLength: 5,
                                        name: 'fap',
                                        xtype: 'textfield',
                                        value: this.values.instituicao.vr_subteto ? this.values.instituicao.fap : undefined
                                    },
                                    {
                                        fieldLabel: 'Alíquota do RAT após ajuste pelo FAP ',
                                        allowBlank: true,
                                        maxLength: 5,
                                        name: 'aliq_rat_ajust',
                                        xtype: 'textfield',
                                        value: this.values.instituicao.vr_subteto ? this.values.instituicao.aliq_rat_ajust : undefined
                                    },
                                ]
                            }
                        ]
                    });
                }

                return this.formPanel
            },

            commit: function () {
                var form = this.getFormPanel().getForm();

                form.waitMsgTarget = this.getEl();

                form.submit({
                    url: toolkit.util.Normalize.controller_action(
                        'GFPConfiguracao',
                        'commit'
                    ),
                    method: 'POST',
                    waitMsg: 'Salvando as informações de configuração.',
                    success: function (form, action) {

                    },
                    failure: function (form, action) {
                        switch (action.failureType) {
                            case 'connect':
                                alert('Erro negociando com o servidor, tente novamente mais tarde.');
                                break;
                            case 'server':
                                alert(action.result.message);
                                break;
                            default:
                                alert('Ocorreu um erro desconhecido. Contacte a equipe de desenvolvimento.');
                                break;
                        }
                    },
                    scope: this
                });
            },

            reset: function () {

            },

            constructor: function () {

                var cf = {
                    title: 'Configurador',
                    autoScroll: true,
                    closable: true,
                    items: [
                        {
                            border: false,
                            xtype: 'panel',
                            html: '<div class="loading"><p>Carregando informações de configuração.</p></div>'
                        }
                    ],
                    style: 'padding: 10pt',
                    buttonAlign: 'center',
                    buttons: [
                        {
                            text: 'Salvar',
                            handler: this.commit,
                            scope: this
                        },
                        {
                            text: 'Restaurar',
                            handler: this.reset,
                            scope: this
                        }
                    ]
                };

                toolkit.gfp.Configuracao.superclass.constructor.call(this, cf);

                var ts = toolkit.Application.tabspace;

                ts.remove(ts.getActiveTab());
                ts.add(this);
                ts.setActiveTab(this);

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action(
                        'GFPConfiguracao',
                        'get_configurations'
                    ),
                    method: 'POST',
                    success: function (request) {
                        try {
                            this.values = Ext.decode(request.responseText);

                            if (!this.values.success) {
                                alert(this.values.message);
                                this.values = {
                                    folha: {},
                                    instituicao: {}
                                };
                            }
                        }
                        catch (e) { }
                        this.removeAll();
                        this.add(this.getFormPanel());
                        this.doLayout();
                    },
                    failure: function () {
                        this.removeAll();
                    },
                    scope: this
                });
            }
        }
    );

    toolkit.gfp.SelecionaFolha = Ext.extend(
        Ext.Window,
        {
            getFormPanel: function () {
                if (!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        frame: true,
                        border: false,
                        defaults: {
                            width: 230
                        },
                        labelWidth: 100,
                        labelAlign: 'right',
                        items: [
                            {
                                xtype: "rest-autocompletefield",
                                fieldLabel: "Folha",
                                allowBlank: true,
                                rest: "rh.gfp.payroll.PayrollRestful",
                                name: "payroll",
                                value: (this.values.folha ? this.values.folha.pk : '')
                            },
                            {
                                xtype: 'checkbox',
                                fieldLabel: 'Folha de Trabalho',
                                name: 'folha_atual',
                                checked: false
                            }
                        ]
                    });

                    this.formPanel.getForm().setValues(this.values);
                }

                return this.formPanel
            },

            select: function () {

                // var rest = new rh.gfp.payroll.PayrollRestful();

                var form = this.getFormPanel().getForm();
                // var fieldFolha = form.findField('folha');
                // console.debug(fieldFolha);
                // rest.getRoute('update', )


                form.waitMsgTarget = this.getEl();
                form.submit({
                    url: toolkit.util.Normalize.controller_action(
                        'GFPPayroll',
                        'select'
                    ),
                    success: function (form, action) {
                        this.trigger(action.result.payroll);
                        this.destroy();
                    },
                    failure: function (form, action) {
                        switch (action.failureType) {
                            case 'connect':
                                alert('Não foi possivel contactar o servidor.');
                                break;
                            default:
                                alert('Erro desconhecido.')
                        }
                    },
                    scope: this,
                    waitMsg: 'Loalizando informações da folha de pagamento.'
                });
            },

            constructor: function (trigger, values) {
                var cf = {
                    title: 'Seletor de Periodo da Folha',
                    closable: true,
                    border: false,
                    width: 370,
                    modal: true,
                    trigger: trigger,
                    values: values,
                    buttons: [
                        {
                            text: 'Selecionar',
                            handler: this.select,
                            scope: this
                        },
                        {
                            text: 'Cancelar',
                            handler: this.destroy,
                            scope: this
                        }
                    ]
                };

                toolkit.gfp.SelecionaFolha.superclass.constructor.call(this, cf);

                this.add(this.getFormPanel());
            }
        }
    );

    toolkit.gfp.LancadorEvento = Ext.extend(
        Ext.Window,
        {
            applyInformation: function (cfg) {
                var form = this.getFormPanel().getForm();

                var disable = (!this.evento || false) && true;
                var proccessed = this.cfg.folha.status == 3 || this.cfg.folha.status == 4;
                console.debug(this);

                // form.findField('patronal').setReadOnly(!cfg.enable.patronal);
                var qnt_field = form.findField('qnt');
                var qnt_max_field = form.findField('qnt_max');
                var pct_field = form.findField('pct');
                var parcela_field = form.findField('parcela');
                var prazo_field = form.findField('prazo');
                var valor_field = form.findField('valor');
                var valor_base_field = form.findField('valor_base');
                var patronal_field = form.findField('patronal');
                var base_previdencia_field = form.findField('base_previdencia');
                var info_field = form.findField('info');
                var reference_year_field = form.findField('reference_year');
                var reference_month_field = form.findField('reference_month');
                var choices_field = form.findField('oIds');
                var paycheck_difference = form.findField('paycheck_difference_id');
                var status_entry = form.findField('status_entry');
                var correct_valor = form.findField('correct_valor');
                var diff_valor_aprovisionado = form.findField('diff_valor_aprovisionado');
                var correct_patronal = form.findField('correct_patronal');
                var diff_patronal_aprovisionado = form.findField('diff_patronal_aprovisionado');
                var correct_base_previdencia = form.findField('correct_base_previdencia');
                var message_field = form.findField('message');

                // Deixando os campos do formulário desabilitados, se necessário

                qnt_field.setDisabled(disable);
                qnt_max_field.setDisabled(disable);
                pct_field.setDisabled(disable);
                parcela_field.setDisabled(disable || proccessed);
                prazo_field.setDisabled(disable || proccessed);
                valor_field.setDisabled(disable || proccessed);
                valor_base_field.setDisabled(disable);
                patronal_field.setDisabled(disable || proccessed);
                base_previdencia_field.setDisabled(disable || proccessed);
                reference_year_field.setDisabled(disable);
                reference_month_field.setDisabled(disable);
                info_field.setDisabled(disable);
                paycheck_difference.setDisabled(disable || proccessed);

                correct_valor.setDisabled(disable || !proccessed);
                correct_patronal.setDisabled(disable || !proccessed);
                correct_base_previdencia.setDisabled(disable || !proccessed);

                console.debug('STATUS: ' + this.cfg.folha.status + ' DISABLE: ' + disable + ' PROCCESSED: ' + proccessed);
                if (!disable) {
                    if (this.evento.multi_calculate && this.cfg.choices) {
                        choices_field.setDisabled(disable);
                        if (choices_field.getStore().getCount() == 0)
                            choices_field.getStore().loadData(this.cfg.choices);
                        if (this.cfg.oIds) {
                            choices_field.suspendEvents();
                            choices_field.setValue(this.cfg.oIds[0]);
                            choices_field.resumeEvents();
                        }
                    }
                } else {
                    choices_field.getStore().loadData([]);
                    choices_field.setDisabled(disable || proccessed);
                }

                // Setando os valores dos fields
                qnt_field.setValue(this.cfg.qnt);
                qnt_max_field.setValue((this.cfg.qnt_max ? this.cfg.qnt_max : this.evento.quantidade_max));
                pct_field.setValue(this.cfg.pct);
                parcela_field.setValue(this.cfg.parcela);
                prazo_field.setValue(this.cfg.prazo);
                valor_field.setValue(this.cfg.valor);
                valor_base_field.setValue(this.cfg.valor_base);
                patronal_field.setValue(this.cfg.patronal);
                base_previdencia_field.setValue(this.cfg.base_previdencia);
                reference_year_field.setValue(this.cfg.reference_year);
                reference_month_field.setValue(this.cfg.reference_month);
                info_field.setValue(this.cfg.info);
                paycheck_difference.setValue(this.cfg.paycheck_difference);

                correct_valor.setValue(this.cfg.correct_valor);
                correct_patronal.setValue(this.cfg.correct_patronal);
                correct_base_previdencia.setValue(this.cfg.correct_base_previdencia);

                // Deixando os campos readonly, se necessário
                if (this.cfg.enable) {
                    pct_field.setReadOnly(!this.cfg.enable.pct);
                    prazo_field.setReadOnly(!this.cfg.enable.prazo);
                    parcela_field.setReadOnly(!this.cfg.enable.parcela);
                    qnt_field.setReadOnly(!this.cfg.enable.qnt);
                    valor_field.setReadOnly(!this.cfg.enable.valor);
                    valor_base_field.setReadOnly(!this.cfg.enable.valor_base);
                    reference_year_field.setReadOnly(!this.cfg.enable.reference_year);
                    reference_month_field.setReadOnly(!this.cfg.enable.reference_month);
                }

                if (cfg.validate && cfg.validate.message) {
                    alert(cfg.validate.message);
                }

            },

            clearFolhaEvento: function () {
                if (!this.cfg.folhaevento) {
                    this.cfg.qnt = 0;
                    this.cfg.pct = 0;
                    this.cfg.prazo = 0;
                    this.cfg.parcela = 0;
                    this.cfg.valor = 0;
                    this.cfg.valor_base = 0;
                    this.cfg.patronal = 0;
                    this.cfg.base_previdencia = 0;
                    this.cfg.correct_valor = 0;
                    this.cfg.correct_base_previdencia = 0;
                    this.cfg.correct_patronal = 0;
                    this.cfg.reference_month = this.cfg.folha.periodo_mes;
                    this.cfg.reference_year = this.cfg.folha.periodo_ano;
                    this.cfg.info = "";
                }
            },

            infoEvento: function (params) {
                var form = this.getFormPanel().getForm();
                var lm = new Ext.LoadMask(this.getEl(), { 'msg': 'Processando...' });


                // console.debug('Executing INFO EVENTO...');
                // console.debug(this.cfg);
                if (this.evento) {
                    if (this.evento.automatico === true) {
                        lm.show();
                        Ext.applyIf(params, { servidor: this.cfg.servidor.pk, folha: this.cfg.folha.pk, evento: this.evento.pk });
                        if (this.cfg.folhaevento) {
                            Ext.applyIf(params, { folhaevento: this.cfg.folhaevento })
                        }
                        qnt_field = this.formPanel.getForm().findField("qnt");
                        if ([3, 4, 5].indexOf(this.evento.tipo_calculo) >= 0 && Ext.isNumber(qnt_field.getValue())) {
                            Ext.applyIf(params, { qnt: qnt_field.getValue() });
                        }
                        pct_field = this.formPanel.getForm().findField("pct");
                        if ([1, 4, 5].indexOf(this.evento.tipo_calculo) >= 0 && Ext.isNumber(pct_field.getValue())) {
                            Ext.applyIf(params, { pct: pct_field.getValue() });
                        }
                        info_field = this.formPanel.getForm().findField("info");
                        choices_field = this.formPanel.getForm().findField("oIds");
                        if (choices_field.getValue())
                            Ext.applyIf(params, { oIds: choices_field.getValue() });

                        Ext.applyIf(params, { info: info_field.getValue() });
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action('GFPLancador', 'info_evento'),
                            params: params,
                            scope: this,
                            success: function (request) {
                                // var cfg = {};
                                var data_folhaevento = Ext.decode(request.responseText);
                                Ext.apply(this.cfg, data_folhaevento);
                                this.applyInformation(this.cfg);
                                lm.hide();
                            },
                            failure: function (request) {
                                lm.hide();
                                alert('Erro ao processar requisição! Informe ao departamento de TI.');
                            }
                        })
                    } else {
                        this.applyInformation(this.cfg);
                    }
                } else {
                    console.error('Evento não definido!');
                }
            },

            getEvento: function (id) {
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPEvento', 'query'),
                    params: {
                        pk: id,
                        keyword: ''
                    },
                    success: function (request) {
                        var obj = Ext.decode(request.responseText);
                        if (obj.totalRows == 1) {
                            Ext.applyIf(this.cfg.evento, obj.result[0]);
                        } else {
                            console.debug('ERRO ao carregar informação do evento!')
                            console.debug(obj);
                        }
                    },
                    failure: function (request) {
                        console.debug(request);
                        alert('Erro ao carregar informação do evento!')
                    },
                    scope: this
                })
            },

            calculoValor: function () {
                // 1: 'PERCENTUAL',
                // 3: 'QUANTIDADE',
                // 2: 'VALOR BASE',
                // 4: 'LIVRE',
                // 5: 'QUANTIDADE/PERCENTUAL',
                if (this.evento.automatico === false) {
                    var valor = this.formPanel.getForm().findField("valor").getValue();
                    var qnt = this.formPanel.getForm().findField("qnt").getValue();
                    var qnt_max = this.formPanel.getForm().findField("qnt_max").getValue();
                    var pct = this.formPanel.getForm().findField("pct").getValue();
                    var valor_base = this.formPanel.getForm().findField("valor_base").getValue(); //this.cfg.valor_base;
                    var parcela = this.formPanel.getForm().findField("parcela").getValue();
                    var prazo = this.formPanel.getForm().findField("prazo").getValue();
                    var reference_month = this.formPanel.getForm().findField("reference_month").getValue();
                    var reference_year = this.formPanel.getForm().findField("reference_year").getValue();
                    //                     console.debug('TIPO: '+ this.evento.tipo_calculo + ' PRAZO: '+ prazo);
                    if (this.evento.tipo_calculo != 4 && prazo == 0) {
                        //                         console.debug('CALCULANDO VALOR...');
                        var fator_qnt = (qnt > 0 && qnt_max > 0) ? (qnt / qnt_max) : 1.0
                        var fator_pct = (pct > 0) ? (pct / 100.0) : 1.0

                        valor = (fator_pct * valor_base * fator_qnt).toFixed(2);
                        this.formPanel.getForm().findField("valor").setValue(valor);
                    }
                } else {
                    console.debug('Evento é automático!');
                }
            },

            markDirty: function (field) {
                //                 console.debug('MARKDIRTY '+ field.name);
                if (this.cfg.markIfDirty && field.isDirty()) {
                    field.getEl().setStyle('background-color', '#ff7777');
                } else {
                    field.getEl().setStyle('background-color', '#d1d1d1');
                }
            },

            changeValue: function (el, newValue, oldValue) {
                //                 console.debug('CHANGE VALUE '+el.name+ ' NEW: '+ newValue+ ' OLD: '+ oldValue+ ' DIRTY: '+ (newValue != oldValue));
                if (newValue != oldValue) {
                    if (this.evento.automatico === true) {
                        this.infoEvento({});
                    } else {
                        this.calculoValor();
                    }
                }
                this.markDirty(el);
            },

            getFormPanel: function () {
                if (!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        frame: true,
                        labelAlign: 'top',
                        autoHeight: true,
                        items: [
                            {
                                xtype: 'rest-autocompletefield',
                                tabIndex: 1,
                                fieldLabel: 'Evento',
                                name: 'evento_id',
                                rest: 'rh.gfp.payroll.EventRestful',
                                readOnly: (this.cfg.evento.pk) ? true : false,
                                oId: (this.cfg.evento.pk) ? this.cfg.evento.pk : null,
                                value: (this.cfg.evento.pk) ? this.cfg.evento.pk : null,
                                preFilter: [
                                    {
                                        'property': 'genre_event__isnull',
                                        'value': false,
                                    }
                                ],
                                comboListeners: {
                                    scope: this,
                                    changevalid: function (cmb, nv, ov, valid) {
                                        if (valid) {
                                            if (!this.evento || this.evento.pk != nv) {
                                                idx = cmb.getStore().findExact(cmb.valueField, nv);
                                                this.evento = cmb.getStore().getAt(idx).data;
                                                this.clearFolhaEvento();
                                                this.infoEvento({});
                                            }
                                        } else {
                                            this.evento = null;
                                        }
                                    },
                                },
                            }, {
                                xtype: 'combo',
                                tabIndex: 2,
                                width: 457,
                                typeAhead: true,
                                triggerAction: 'all',
                                lazyRender: true,
                                mode: 'local',
                                store: new Ext.data.ArrayStore({
                                    id: 0,
                                    fields: [
                                        'oId',
                                        'displayText'
                                    ],
                                    data: []
                                }),
                                valueField: 'oId',
                                displayField: 'displayText',
                                hiddenName: 'oIds',
                                disabled: true,
                                editable: false,
                                fieldLabel: 'Opções',
                                listeners: {
                                    scope: this,
                                    change: this.changeValue,
                                    // valid: this.markDirty,
                                },
                            }, {
                                layout: 'hbox',
                                items: [
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Quantidade',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            minValue: 0,
                                            decimalPrecision: 5,
                                            name: 'qnt',
                                            tabIndex: 3,
                                            value: Ext.isNumber(this.cfg.qnt) ? this.cfg.qnt : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                change: this.changeValue,
                                                valid: this.markDirty,
                                            },
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Qtd. Base',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            minValue: 0,
                                            readOnly: true,
                                            decimalPrecision: 5,
                                            name: 'qnt_max',
                                            tabIndex: 4,
                                            value: (Ext.isNumber(this.cfg.evento.qnt_max) ? this.cfg.evento.qnt_max : this.cfg.quantidade_max),
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                valid: this.markDirty,

                                            }
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Parcela',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            name: 'parcela',
                                            tabIndex: 5,
                                            value: Ext.isNumber(this.cfg.parcela) ? this.cfg.parcela : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                valid: this.markDirty,

                                            }
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Prazo',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            name: 'prazo',
                                            tabIndex: 6,
                                            value: Ext.isNumber(this.cfg.prazo) ? this.cfg.prazo : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                valid: this.markDirty,

                                            }
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Percentual',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            minValue: 0,
                                            maxValue: 100.00,
                                            decimalPrecision: 6,
                                            name: 'pct',
                                            tabIndex: 7,
                                            value: Ext.isNumber(this.cfg.pct) ? this.cfg.pct : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                change: this.changeValue,
                                                valid: this.markDirty,

                                            }
                                        }
                                    }
                                ]
                            },
                            {
                                layout: 'hbox',
                                items: [
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Valor',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            name: 'valor',
                                            tabIndex: 8,
                                            value: Ext.isNumber(this.cfg.valor) ? this.cfg.valor : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                valid: this.markDirty,
                                            },

                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Valor Base',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            name: 'valor_base',
                                            tabIndex: 9,
                                            value: Ext.isNumber(this.cfg.valor_base) ? this.cfg.valor_base : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                change: this.changeValue,
                                                valid: this.markDirty,
                                            }
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Patronal',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            name: 'patronal',
                                            tabIndex: 10,
                                            value: Ext.isNumber(this.cfg.patronal) ? this.cfg.patronal : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                valid: this.markDirty,
                                            },
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Base Prev.',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            name: 'base_previdencia',
                                            tabIndex: 11,
                                            value: Ext.isNumber(this.cfg.base_previdencia) ? this.cfg.base_previdencia : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                valid: this.markDirty,
                                            },
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: '',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            value: '',
                                            disabled: true,
                                        }
                                    }
                                ]
                            },
                            {
                                layout: 'hbox',
                                items: [
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Valor Devido',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            name: 'correct_valor',
                                            tabIndex: 12,
                                            value: Ext.isNumber(this.cfg.correct_valor) ? this.cfg.correct_valor : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                valid: this.markDirty,
                                            },

                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: '',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            tabIndex: 13,
                                            disabled: true,
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Pat. Devido',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            name: 'correct_patronal',
                                            tabIndex: 14,
                                            value: Ext.isNumber(this.cfg.correct_patronal) ? this.cfg.correct_patronal : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                valid: this.markDirty,
                                            },
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Prev. Devida',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            name: 'correct_base_previdencia',
                                            tabIndex: 15,
                                            value: Ext.isNumber(this.cfg.correct_base_previdencia) ? this.cfg.correct_base_previdencia : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                valid: this.markDirty,
                                            },
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: '',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'numberfield',
                                            value: '',
                                            disabled: true,
                                        }
                                    },
                                ]
                            },
                            {
                                layout: 'hbox',
                                items: [
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 315,
                                            fieldLabel: 'Informações',
                                            style: 'margin: 0 5px 0 0',
                                            xtype: 'textfield',
                                            name: 'info',
                                            tabIndex: 17,
                                            value: this.cfg.info ? this.cfg.info : '',
                                            disabled: true,
                                            listeners: {
                                                scope: this,
                                                valid: this.markDirty,
                                            },
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Mês/Ref.',
                                            name: 'reference_month',
                                            tabIndex: 18,
                                            value: Ext.isNumber(this.cfg.reference_month) ? this.cfg.reference_month : this.cfg.folha.periodo_mes,
                                            disabled: true,
                                            xtype: 'combo',
                                            hiddenName: 'reference_month',
                                            store: [
                                                [1, 'JANEIRO'],
                                                [2, 'FEVEREIRO'],
                                                [3, 'MARÇO'],
                                                [4, 'ABRIL'],
                                                [5, 'MAIO'],
                                                [6, 'JUNHO'],
                                                [7, 'JULHO'],
                                                [8, 'AGOSTO'],
                                                [9, 'SETEMBRO'],
                                                [10, 'OUTUBRO'],
                                                [11, 'NOVEMBRO'],
                                                [12, 'DEZEMBRO'],
                                            ],
                                            triggerAction: 'all'
                                        }
                                    },
                                    {
                                        layout: 'form',
                                        labelAlign: 'top',
                                        items: {
                                            width: 100,
                                            fieldLabel: 'Ano/Ref.',
                                            style: 'margin: 0 0 0 5px',
                                            xtype: 'numberfield',
                                            name: 'reference_year',
                                            tabIndex: 19,
                                            value: Ext.isNumber(this.cfg.reference_year) ? this.cfg.reference_year : this.cfg.folha.periodo_ano,
                                            disabled: true,
                                        }
                                    }
                                ]
                            }, {
                                xtype: 'rest-autocompletefield',
                                tabIndex: 20,
                                fieldLabel: 'Diferença',
                                name: 'paycheck_difference_id',
                                rest: 'rh.gfp.paycheckdifference.PayCheckDifferenceRestful',
                                // readOnly: (this.cfg.paycheck_difference)? true: false,
                                oId: (this.cfg.paycheck_difference) ? this.cfg.paycheck_difference : null,
                                value: (this.cfg.paycheck_difference) ? this.cfg.paycheck_difference : null,
                                preFilter: [
                                    { property: 'status', value: 1, stage: 1001 },
                                    { property: 'employee__id', value: this.cfg.servidor.pk, stage: 1000 },
                                ],
                            },
                            {
                                layout: 'form',
                                hideLabels: true,
                                autoHeight: true,
                                hidden: true,
                                items: {
                                    // width: 370,
                                    style: 'margin: 0 5px 0 0',
                                    xtype: 'displayfield',
                                    name: 'validate_message',
                                    value: '',
                                    id: 'validate_message'
                                }
                            }
                        ],
                        scope: this
                    });
                    if (this.cfg.evento.pk) {
                        var frmEvento = this.formPanel.getForm().findField('evento_id');
                        // console.debug(frmEvento);
                        frmEvento.setValue(this.cfg.evento.pk);
                    }
                }
                return this.formPanel;
            },

            save: function (destroy) {
                var form = this.getFormPanel().getForm();
                var lm = new Ext.LoadMask(this.getEl(), { 'msg': 'Processando...' });

                // form.targetMsgWait = this.getEl();
                lm.show();
                form.submit({
                    url: toolkit.util.Normalize.controller_action('GFPLancador', this.cfg.evento__pk ? 'update' : 'create'),
                    params: {
                        folha_id: this.cfg.folha.pk,
                        servidor_id: this.cfg.servidor.pk,
                        id: this.cfg.folhaevento,
                        // base_previdencia: this.cfg.base_previdencia
                    },
                    success: function (form, action) {
                        if (this.cfg.scope) {
                            var obj = this.cfg.scope;
                            obj.__cb__ = this.cfg.callback
                            obj.__cb__();
                            delete obj['__cb__'];
                        }
                        else {
                            this.cfg.callback();
                        }

                        if (!destroy) form.reset();
                        else this.destroy();
                        lm.hide();
                    },
                    failure: function (form, action) {
                        lm.hide();
                        if (action.failureType == 'server')
                            Ext.Msg.show({
                                icon: Ext.Msg.ERROR,
                                msg: action.result.message,
                                buttons: Ext.Msg.OK
                            });
                    },
                    scope: this
                })
            },

            constructor: function (cfg) {
                var cf = {
                    title: 'Lançar Evento',
                    resizable: false,
                    border: false,
                    width: 560,
                    cfg: cfg,
                    modal: true,
                    buttons: [
                        {
                            text: 'Salvar',
                            scope: this,
                            id: 'btnSave',
                            handler: function () { this.save(true) }
                        },
                        {
                            text: 'Salvar e novo',
                            scope: this,
                            id: 'btnSaveNew',
                            handler: function () { this.save(false) }
                        },
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.destroy
                        }
                    ]
                };

                this.qnt = 0;
                this.valor_base = 0;

                toolkit.gfp.LancadorEvento.superclass.constructor.call(this, cf);
                // console.debug(cfg);
                // if(this.cfg.evento.pk){
                //     this.getEvento(this.cfg.evento.pk);
                // }
                this.add(this.getFormPanel());
            }
        }
    );

    toolkit.gfp.GridDependente = Ext.extend(
        Ext.Window,
        {

            dependente: function (value, dispatch) {
                dispatch = core.nullValue(dispatch, true);

                if (value !== undefined) {
                    this._dependente = value;

                    if (dispatch) this.observeDependente();
                }
                else
                    return this._dependente;
            },

            getGridDependente: function (cfg) {
                if (!this._gridDependente)
                    this._gridDependente = Ext._create('rh.dependente.DependenteGrid', {
                        region: 'center',
                        gridAutoLoad: true,
                        hideColumns: [
                            'unicode',
                            'auxilio_creche',
                            'data_alteracao',
                            'data_fim',
                            'motivo_inicio_dependencia',
                            'motivo_inicio_dependencia_display',
                            'motivo_fim_dependencia',
                            'motivo_fim_dependencia_display',
                            'data_cadastro',
                            'dep_ir',
                            'data_inicio',
                            'dep_sf',
                            'dependente_direto',
                            'responsavel_unicode',
                        ]
                    });

                this._gridDependente.getSelectionModel().on({
                    scope: this,
                    rowselect: function (sm, index, data) {
                        this.dependente(data.get('pk'));
                    },
                    rowdeselect: function () {
                        this.dependente(null);
                    },
                });
                this._gridDependente.getStore().on({
                    scope: this,
                    load: function (gd, opts) {
                        var rec = this._gridDependente.getSelectionModel().getSelected();
                        this._gridDependente.getSelectionModel().clearSelections();
                        this.dependente(null);
                        if (rec) {
                            this._gridDependente.getSelectionModel().selectRecords([rec]);
                        }

                    }
                })

                return this._gridDependente;
            },

            getGridDependencia: function () {
                if (!this._gridDependencia)
                    this._gridDependencia = Ext._create('rh.dependente.DependenciaGrid', {
                        region: 'south',
                        height: 300,
                        // values: {servidor: this.dependente(),},
                        // params: {end_validity: null},
                        gridAutoLoad: false,
                        hideColumns: [
                            'unicode',
                        ]
                    });

                return this._gridDependencia;
            },

            observeDependente: function () {
                if (this.dependente()) {
                    console.debug('OB DEPENDENTE...');
                    this.getGridDependencia().enable();
                    this.getGridDependencia().setParam('dependente', this.dependente());
                    this.getGridDependencia().setFilterProperty('dependente_id', this.dependente(), 100);
                }
                else {
                    console.debug('NOT OB DEPENDENTE...');
                    this.getGridDependencia().disable();
                    this.getGridDependencia().getStore().removeAll();
                    this.getGridDependencia().setFilterProperty('dependente_id', 0, 100, false);
                }
            },

            constructor: function (cfg) {
                cfg = cfg ? cfg : {};

                Ext.applyIf(
                    cfg,
                    {
                        title: 'Gestor de Dependentes'
                    }
                );

                Ext.apply(
                    cfg,
                    {
                        layout: 'border',
                        items: [
                            this.getGridDependente(),
                            this.getGridDependencia()
                        ]
                    }
                );
                console.debug('rh.dependente.DependenteManageWindow');
                this.observeDependente();
                rh.dependente.DependenteManageWindow.superclass.constructor.call(this, cfg);
            }
        }
    );

    toolkit.gfp.GridDependentePanel = Ext.extend(
        Ext.Panel,
        {
            constructor: function (cf) {
                var df = {
                    layout: 'fit',
                    scope: this,
                    items: this.getPanel(cf)
                };
                Ext.apply(cf, df);
                toolkit.gfp.GridDependente.superclass.constructor.call(this, cf);
            },

            getPanel: function (cf) {
                if (!this._panel)
                    this._panel = new Ext.Panel({
                        height: 400,
                        layout: 'border',
                        items: [
                            this.getDependentesGrid(cf),
                            {
                                region: 'south',
                                height: 200,
                                split: true,
                                layout: 'hbox',
                                border: false,
                                items: [
                                    this.getDependenciaGrid(),
                                ]
                            }
                        ]
                    });
                this.getDependenciaGrid().disable();
                return this._panel;

            },

            manageSelectDependente: function () {
                var sel = this.getDependentesGrid().getSelectionModel().getSelected();
                if (sel) {
                    this.getDependenciaGrid().enable();
                    this.getDependenciaGrid().getStore().baseParams = {
                        'pk': sel.get('pk'),
                    };
                    new Ext.LoadMask(this.getDependenciaGrid().getEl(), {
                        msg: 'Carregando dados...',
                        store: this.getDependenciaGrid().getStore()
                    });
                    this.getDependenciaGrid().getStore().load({});
                }
                else {
                    this.getDependenciaGrid().disable();
                    this.getDependenciaGrid().getStore().baseParams = {};
                    this.getDependenciaGrid().getStore().removeAll();
                }
            },

            getDependentesGrid: function (cf) {
                if (!this._dependenteGrid) {
                    this._dependenteGrid = new toolkit.gfp.DependentesGrid({
                        region: 'center',
                        scope: this,
                        bodyStyle: 'border-left:none',
                        sm: new Ext.grid.RowSelectionModel({
                            listeners: {
                                scope: this,
                                rowselect: this.manageSelectDependente
                            }
                        })
                    }, cf);
                }
                return this._dependenteGrid;
            },

            getDependenciaGrid: function () {
                if (!this._dependenciaGrid) {
                    this._dependenciaGrid = new toolkit.gfp.DependenciaGrid({
                        region: 'center',
                        flex: 1,
                        layout: 'fit',
                        height: 200,
                        minHeight: 200,
                        bodyStyle: 'border-right:none',
                    });
                }
                return this._dependenciaGrid;
            },
        }
    );
}
