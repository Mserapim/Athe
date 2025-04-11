Ext._define('rh.gfp.payroll.EventWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.payroll.EventRestful',

    width: 550,
    height: 700,

    getIncideSobrePanel: function(cfg) {
        if(!this._incideSobrePanel)
            this._incideSobrePanel = Ext._create('core.fields.RelatedRestfulField', {
                frame: true,
                border: false,
                title: "Incide sobre",
                name: 'incide_sobre',
                relatedname: 'aplica_em',
                width: 540,
                height: 370,
                rest: this.rest,
                sourceRest: 'rh.gfp.payroll.EventRestful',
                oId: cfg.oId,
            });

        return this._incideSobrePanel;
    },

    getAplicaEmPanel: function(cfg) {
        if(!this._aplicaEmPanel)
            this._aplicaEmPanel = Ext._create('core.fields.RelatedRestfulField', {
                frame: true,
                border: false,
                title: "Aplica sobre",
                name: 'aplica_em',
                relatedname: 'incide_sobre',
                width: 540,
                height: 370,
                rest: this.rest,
                sourceRest: 'rh.gfp.payroll.EventRestful',
                oId: cfg.oId,
            });

        return this._aplicaEmPanel;
    },

    getDifferencePanel: function(cfg) {
        if(!this._configDifferencePanel)
            this._configDifferencePanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                defaults: {
                    width: 400
                },
                title: 'Diferenças',
                layout: 'form',
                items: [
                    {
                        fieldLabel: 'Avaliar diferença',
                        xtype: 'checkbox',
                        name: 'evaluate_difference',
                        readOnly: true,
                    },{
                        fieldLabel: 'Separar por competência',
                        xtype: 'checkbox',
                        name: 'separate_for_competencies',
                        readOnly: true,
                    },{
                        fieldLabel: 'Separar por info',
                        xtype: 'checkbox',
                        name: 'separate_for_info_event',
                        readOnly: true,
                    },{
                        title: 'Configurações',
                        xtype: 'fieldset',
                        // checkboxToggle: true,
                        autoHeight: true,
                        autoWidth: true,
                        // layout: 'fit',
                        items:[
                            {
                                xtype: 'displayfield',
                                value: "<b>Configuração padrão:</b><br /><br /><code><b>MEA</b>:{GN}06.VALOR={DV},{GN}06.PATRONAL={DP};<br /><b>DIF</b>:{GN}01.VALOR={DV},{GN}01.PATRONAL={DP};<br /><b>DEV</b>:{GN}02.VALOR=-{DV},{GN}02.PATRONAL={DP};<br /><b>ESD</b>:{GN}07.VALOR=-{DV},{GN}07.PATRONAL={DP};<br /><b>ESC</b>:{GN}08.VALOR=-{DV},{GN}08.PATRONAL={DP};</code>"
                            },
                            {
                                xtype: 'displayfield',
                                value: "<b>Legenda:</b><br /><br /><code><b>MEA</b>:Mês anterior (diferença total não );<br /><b>DIF</b>:{GN}01.VALOR={DV},{GN}01.PATRONAL={DP};<br /><b>DEV</b>:{GN}02.VALOR=-{DV},{GN}02.PATRONAL={DP};<br /><b>ESD</b>:{GN}07.VALOR=-{DV},{GN}07.PATRONAL={DP};<br /><b>ESC</b>:{GN}08.VALOR=-{DV},{GN}08.PATRONAL={DP};</code>"
                            },
                            {
                                xtype: 'textarea',
                                name: 'config_value',
                                allowBlank: true,
                                height: 100,
                                width: 500,
                                hideLabel: true,
                                // readOnly: true,
                            }
                        ]
                    }
                ]
            });

        return this._configDifferencePanel;
    },

    _observe: function() {

        // var grid_incide = this.getIncideSobrePanel();
        // var grid_aplica = this.getAplicaEmPanel();
        // if(this.oId) {
        //     grid_incide.enable();
        //     grid_aplica.enable();
        // }else{
        //     grid_incide.disable();
        //     grid_aplica.disable();
        // }
    },

    getTagsPanel: function (cfg) {
        if (!this._employeeTypePanel)
            this._employeeTypePanel = Ext._create('core.fields.RelatedRestfulField', {
                title: 'Tags',
                name: 'tags',
                displayField: 'label',
                width: 540,
                height: 445,
                rest: this.rest,
                disabled: false,
                border: false,
                sourceRest: 'standard.ChoiceRestful',
                oId: cfg.oId,
                preFilter: [
                    {
                        'property': 'name',
                        'value': 'EVENT_TAGS',
                    }
                ],
                gridConfig: {
                    columnAction: false,
                    configOrderToolBar: ['search', '->'],
                    onlyColumns: [
                        'label', 'cvalue'
                    ]
                }
            });

        return this._employeeTypePanel;
    },

    getTabPanel: function(cfg) {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 700,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    this.getEventPanel(cfg),
                    // this.getConfigPanel(cfg),
                    // this.getIncideSobrePanel(cfg),
                    // this.getAplicaEmPanel(cfg),
                    this.getDifferencePanel(cfg),
                    this.getTagsPanel(cfg)
                ]
            });

        return this._tabPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: this.getTabPanel(cfg),
                submit_all_checks: true
            });

        return this._formPanel;
    },

    event_name: function(genre, specie){
        if(specie == ' ')
            return genre;
        else
            return genre.concat(' - ', specie);
    },

    invert_type_verify: function(genre_type_event, specie_invert_type){
        if(specie_invert_type){
            if(genre_type_event=='P') return 'D';
            else return 'P'
        }else
            return genre_type_event;
    },

    getSpecieForm: function(cfg){
        if(!this._specie_event)
            this._specie_event = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Espécie',
                name: 'specie_event',
                allowBlank: true,
                rest: 'rh.gfp.payroll.SpecieEventRestful',
                readOnly: false,
                baseParams: (cfg.action == 'create' ? {genre_event: cfg.values.genre_event} : {}),
                comboListeners:{
                    scope: this,
                    select: function(combo, record, index){
                        if(cfg.action == 'create'){
                            var form = this.getFormPanel().getForm();

                            titulo = this.event_name(this._genre_event.get('title'), record.get('title'));
                            form.findField('titulo').setValue(titulo);

                            numero_display = this._genre_event.get('genre_number').concat("-", record.get('specie_number'));
                            form.findField('numero_display').setValue(numero_display);

                            tipo = this.invert_type_verify(this._genre_event.get('type_event'), record.get('invert_type'));
                            form.findField('tipo').setValue(tipo);
                        }
                    }
                }
            });

        return this._specie_event;
    },

    getBancoConsignacaoForm: function(cfg){
        if(!this._banco_consignacao)
            this._banco_consignacao = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Banco Consignação',
                name: 'banco_consignacao',
                allowBlank: true,
                rest: 'rh.gfp.payroll.BancoConsignacaoRestful',
                //readOnly: cfg.values.carater == 7 ? false : true,
            });

        return this._banco_consignacao;
    },

    getEventPanel: function(cfg) {
        if(!this._eventPanel)
            this._eventPanel = Ext._create("Ext.Panel", {
                frame: true,
                border: false,
                defaults: {
                    width: 400,
                },
                title: "Geral",
                layout: "form",
                items: [
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Gênero",
                        allowBlank: true,
                        rest: "rh.gfp.payroll.GenreEventRestful",
                        name: "genre_event",
                        readOnly: cfg.action == "create" ? false : true,
                        comboListeners: {
                            scope: this,
                            select: function (combo, record, index) {
                                if (cfg.action == "create") {
                                    this._genre_event = record;
                                    var form = this.getFormPanel().getForm();
                                    form.findField("carater").setValue(record.get("character"));
                                    form.findField("specie_event").setReadOnly(false);
                                    this.getSpecieForm().baseParams.genre_event = record.id;
                                    this.getSpecieForm().getComboField().getStore().reload();
                                }
                            },
                        },
                    },
                    this.getSpecieForm(cfg),
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Evento anterior",
                        allowBlank: true,
                        rest: "rh.gfp.payroll.EventRestful",
                        name: "previous_event",
                        readOnly: false,
                        comboListeners: {
                            scope: this,
                            select: function (cmb, rec, idx) {
                                if (this.values.previous_event != rec.data.pk) {
                                    var form = this.getFormPanel().getForm();
                                    form.findField("lancamento").setValue(rec.data.lancamento);
                                    form.findField("tipo_calculo").setValue(rec.data.tipo_calculo);
                                    form.findField("automatico").setValue(rec.data.automatico);
                                    form.findField("calculo_invertido").setValue(rec.data.calculo_invertido);
                                    form.findField("aplica_consignado").setValue(rec.data.aplica_consignado);
                                    form.findField("aplica_consignavel").setValue(rec.data.aplica_consignavel);
                                    form.findField("evaluate_difference").setValue(rec.data.evaluate_difference);
                                    form.findField("quantidade").setValue(rec.data.quantidade);
                                    form.findField("quantidade_max").setValue(rec.data.quantidade_max);
                                    form.findField("porcentagem").setValue(rec.data.porcentagem);
                                    form.findField("valor_base").setValue(rec.data.valor_base);
                                    form.findField("teto").setValue(rec.data.teto);
                                    form.findField("piso").setValue(rec.data.piso);
                                    form.findField("config_transparencia").setValue(rec.data.config_transparencia);
                                    form.findField("base_de_calculo").setValue(rec.data.base_de_calculo);
                                }
                            },
                        },
                    },
                    {
                        fieldLabel: "Número",
                        xtype: "textfield",
                        name: "numero_display",
                        allowBlank: false,
                        readOnly: true,
                    },
                    {
                        fieldLabel: "Título",
                        xtype: "textfield",
                        name: "titulo",
                        allowBlank: false,
                        readOnly: true,
                    },
                    {
                        // FIXME - modificar para ChoiceField
                        fieldLabel: 'Lançamento',
                        xtype: 'combo',
                        hiddenName: 'lancamento',
                        store: [
                            ['F', 'FIXO'],
                            ['T', 'TEMPORÁRIO'],
                            ['U', 'TEMPORÁRIO - ÚNICO'],
                        ],
                        allowBlank: false,
                        // value: 'T',
                        triggerAction: "all",
                    },
                    {
                        fieldLabel: "Tipo",
                        xtype: "combo",
                        hiddenName: "tipo",
                        store: [
                            ["P", "PROVENTO"],
                            ["D", "DESCONTO"],
                            ["I", "INFORMATIVO"],
                        ],
                        allowBlank: false,
                        // value: 'P',
                        triggerAction: "all",
                        // readOnly: true
                    },
                    {
                        xtype: "choicefield",
                        fieldLabel: "Tipo Cálculo",
                        hiddenName: "tipo_calculo",
                        choiceId: "gfp.TYPE_OF_CALC",
                    },
                    {
                        xtype: "choicefield",
                        fieldLabel: "Caráter",
                        hiddenName: "carater",
                        choiceId: "gfp.EVENT_CHARACTER",
                        listeners: {
                            scope: this,
                            select: function(combo, record) {
                                var form = this.getFormPanel().getForm();
                                if(record.data.value == 7){
                                    form.findField("banco_consignacao").setReadOnly(false);
                                }else{
                                    form.findField("banco_consignacao").setValue(null);
                                    form.findField("banco_consignacao").setReadOnly(false);
                                }
                            }
                        },
                    },
                    // {
                    //     fieldLabel: 'Automático',
                    //     xtype: 'checkbox',
                    //     name: 'automatico',
                    //     readOnly: true,
                    // },
                    // Ext._create('core.fields.AutocompleteField', {
                    //     fieldLabel: 'Cálculo',
                    //     name: 'calculo',
                    //     displayField: 'path',
                    //     allowBlank: true,
                    //     rest: 'standard.classcode.Restful',
                    //     readOnly: true,
                    // }),{
                    //     fieldLabel: 'Cálculo invertido',
                    //     xtype: 'checkbox',
                    //     name: 'calculo_invertido',
                    //     readOnly: true,
                    // },
                    {
                        fieldLabel: "Gerencia Consignável?",
                        xtype: "checkbox",
                        name: "consignment_manager",
                    },
                    this.getBancoConsignacaoForm(cfg),
                    {
                        fieldLabel: "Ativo",
                        xtype: "checkbox",
                        name: "active",
                    },
                    {
                        fieldLabel: "Descrição",
                        maxLength: 255,
                        allowBlank: true,
                        name: "description",
                        xtype: "textfield",
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Classificação Aplic',
                        hiddenName: 'aplic_classification',
                        choiceId: 'gfp.APLIC_CLASS',
                        allowBlank: true,
                        anchor: '99%'
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo Aplic',
                        hiddenName: 'aplic_type',
                        choiceId: 'gfp.APLIC_TYPE',
                        allowBlank: true,
                        anchor: '99%'
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Classificação Portal',
                        hiddenName: 'portal_classification',
                        choiceId: 'gfp.PORTAL_CLASS',
                        allowBlank: true,
                        anchor: '99%'
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Conta Contábil',
                        hiddenName: 'conta_contabil',
                        choiceId: 'gfp.CONTA_CONTABIL',
                        allowBlank: false,
                        anchor: '99%'
                    },
                ],
            });

        return this._eventPanel;
    },

    getConfigPanel: function(cfg) {
        if(!this._configPanel)
            this._configPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                defaults: {
                    width: 400
                },
                title: 'Padrões',
                layout: 'form',
                items: [
                    {
                        fieldLabel: 'Quantidade',
                        xtype: 'numberfield',
                        name: 'quantidade',
                        allowBlank: true,
                        allowNegative: false,
                        readOnly: true,
                    },{
                        fieldLabel: 'Quantidade máxima',
                        xtype: 'numberfield',
                        name: 'quantidade_max',
                        allowBlank: true,
                        allowNegative: false,
                        readOnly: true,
                    },{
                        fieldLabel: 'Porcentagem',
                        xtype: 'numberfield',
                        name: 'porcentagem',
                        allowBlank: true,
                        allowNegative: false,
                        decimalPrecision: 6,
                        readOnly: true,
                    },{
                        fieldLabel: 'Valor base',
                        xtype: 'numberfield',
                        name: 'valor_base',
                        allowBlank: true,
                        allowNegative: false,
                        readOnly: true,
                    },{
                        fieldLabel: 'Teto',
                        xtype: 'numberfield',
                        name: 'teto',
                        allowBlank: true,
                        allowNegative: false,
                        readOnly: true,
                    },{
                        fieldLabel: 'Piso',
                        xtype: 'numberfield',
                        name: 'piso',
                        allowBlank: true,
                        allowNegative: false,
                        readOnly: true,
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Portal Transparência',
                        hiddenName: 'config_transparencia',
                        choiceId: 'rh.CONFIG_TRANSPARENCY',
                    },
                    {
                        fieldLabel: 'Base de cálculo',
                        xtype: 'combo',
                        hiddenName: 'base_de_calculo',
                        store: [
                            [0, "SEM BASE"],
                            [1, "REMUNERAÇÃO BRUTA"],
                            [2, "PREVIDENCIÁRIA"],
                            [3, "REMUNERAÇÃO BASE"]
                        ],
                        allowBlank: true,
                        triggerAction: 'all'
                    },
                ]
            });

        return this._configPanel;
    },

    constructor: function(cfg) {
        rh.gfp.payroll.EventWindow.superclass.constructor.call(this, cfg);
        this._observe();
    }
});
