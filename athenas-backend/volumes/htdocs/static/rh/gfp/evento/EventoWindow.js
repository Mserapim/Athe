Ext._define('rh.gfp.evento.EventoWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.evento.EventoRestful',

    width: 550,

    getIncideSobrePanel: function(cfg) {
        if(!this._incideSobrePanel)
            this._incideSobrePanel = Ext._create('core.fields.RelatedRestfulField', {
                frame: true,
                border: false,
                title: "Incide sobre", 
                        // fieldLabel: 'Funcionalidades',
                name: 'incide_sobre',
                relatedname: 'aplica_em',
                width: 540,
                height: 370,
                rest: this.rest,
                sourceRest: 'rh.gfp.evento.EventoRestful',
                oId: cfg.oId,
                // listeners:{
                //     afterrender: function(panel){
                //         this.doLayout();
                //     },
                // }
            });

        return this._incideSobrePanel;
    },

    getAplicaEmPanel: function(cfg) {
        if(!this._aplicaEmPanel)
            this._aplicaEmPanel = Ext._create('core.fields.RelatedRestfulField', {
                frame: true,
                border: false,
                title: "Aplica sobre", 
                        // fieldLabel: 'Funcionalidades',
                name: 'aplica_em',
                relatedname: 'incide_sobre',
                width: 540,
                height: 370,
                rest: this.rest,
                sourceRest: 'rh.gfp.evento.EventoRestful',
                oId: cfg.oId,
            });

        return this._aplicaEmPanel;
    },

    _observe: function() {

        var grid_incide = this.getIncideSobrePanel();
        var grid_aplica = this.getAplicaEmPanel();
        if(this.oId) {
            grid_incide.enable();
            grid_aplica.enable();
        }else{
            grid_incide.disable();
            grid_aplica.disable();
        }
    },

    getTabPanel: function(cfg) {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 400,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    this.getEventPanel(cfg),
                    this.getConfigPanel(cfg),
                    this.getIncideSobrePanel(cfg),
                    this.getAplicaEmPanel(cfg),
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

    getEventPanel: function(cfg) {
        if(!this._eventPanel)
            this._eventPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                defaults: {
                    width: 400
                },
                title: 'Geral',
                layout: 'form',
                items: [
                    {
                        fieldLabel: 'Número',
                        xtype: 'textfield',
                        name: 'numero',
                        allowBlank: false
                    },{
                        fieldLabel: 'Título',
                        xtype: 'textfield',
                        name: 'titulo',
                        allowBlank: false
                    },{
                        fieldLabel: 'Lançamento',
                        xtype: 'combo',
                        hiddenName: 'lancamento',
                        store: [
                            ['F', 'FIXO'],
                            ['T', 'TEMPORÁRIO']
                        ],
                        allowBlank: false,
                        // value: 'T',
                        triggerAction: 'all'
                    },{
                        fieldLabel: 'Tipo',
                        xtype: 'combo',
                        hiddenName: 'tipo',
                        store: [
                            ['P', 'PROVENTO'],
                            ['D', 'DESCONTO']                        
                        ],
                        allowBlank: false,
                        // value: 'P',
                        triggerAction: 'all'
                    },{
                        fieldLabel: 'Tipo Cálculo',
                        xtype: 'combo',
                        hiddenName: 'tipo_calculo',
                        store: [
                            [1, 'PERCENTUAL'],
                            [3, 'QUANTIDADE'],
                            [2, 'VALOR BASE'],
                            [4, 'LIVRE'],
                            [5, 'QUANTIDADE/PERCENTUAL']
                        ],
                        allowBlank: false,
                        // value: 4,
                        triggerAction: 'all'
                    },{
                        fieldLabel: 'Caráter',
                        xtype: 'combo',
                        hiddenName: 'carater',
                        store: [
                            [0, 'OUTROS'],
                            [1, 'REMUNERATÓRIO'],
                            [2, 'INDENIZATÓRIO'],
                            [3, 'DE AUXÍLIO'],
                            [4, 'IMPOSTO'],
                            [5, 'PENSÃO'],
                            [6, 'MENSALIDADE'],
                            [7, 'CONSIGNAÇÃO']
                        ],
                        allowBlank: false,
                        // value: 0,
                        triggerAction: 'all'
                    },{
                        fieldLabel: 'Automático',
                        xtype: 'checkbox',
                        name: 'automatico',
                        // cls: 'forceSubmit',
                        // allowBlank: true
                    },
                    Ext._create('core.fields.AutocompleteField', {
                        fieldLabel: 'Cálculo',
                        name: 'calculo',
                        displayField: 'path',
                        allowBlank: true,
                        rest: 'standard.classcode.Restful',
                    }),{
                        fieldLabel: 'Cálculo invertido',
                        xtype: 'checkbox',
                        name: 'calculo_invertido',
                        // cls: 'forceSubmit',
                        // allowBlank: true
                    },{
                        fieldLabel: 'Consignado',
                        xtype: 'checkbox',
                        name: 'aplica_consignado',
                        // cls: 'forceSubmit',
                        // allowBlank: true
                    },{
                        fieldLabel: 'Consignável',
                        xtype: 'checkbox',
                        name: 'aplica_consignavel',
                        // cls: 'forceSubmit',
                        // allowBlank: true
                    },
                ]
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
                        allowNegative: false
                    },{
                        fieldLabel: 'Quantidade máxima',
                        xtype: 'numberfield',
                        name: 'quantidade_max',
                        allowBlank: true,
                        allowNegative: false
                    },{
                        fieldLabel: 'Porcentagem',
                        xtype: 'numberfield',
                        name: 'porcentagem',
                        allowBlank: true,
                        allowNegative: false,
                        decimalPrecision: 6
                    },{
                        fieldLabel: 'Valor base',
                        xtype: 'numberfield',
                        name: 'valor_base',
                        allowBlank: true,
                        allowNegative: false
                    },{
                        fieldLabel: 'Teto',
                        xtype: 'numberfield',
                        name: 'teto',
                        allowBlank: true,
                        allowNegative: false
                    },{
                        fieldLabel: 'Piso',
                        xtype: 'numberfield',
                        name: 'piso',
                        allowBlank: true,
                        allowNegative: false
                    },{
                        fieldLabel: 'Portal Transparência',
                        xtype: 'combo',
                        hiddenName: 'config_transparencia',
                        store: [
                            [3101, "DEDUÇÕES: IRRF"], 
                            [3102, "DEDUÇÕES: IRRF - 13º Salá1rio"], 
                            [3103, "DEDUÇÕES: Previdência Social"], 
                            [3104, "DEDUÇÕES: Previdência - 13º Salário"], 
                            [4001, "INDENIZATÓRIAS: Aux. Alimentação"], 
                            [4002, "INDENIZATÓRIAS: Aux. Creche"], 
                            [4003, "INDENIZATÓRIAS: Aux. Transparte"], 
                            [4009, "INDENIZATÓRIAS: Aux. Moradia"],
                            [4004, "INDENIZATÓRIAS: Diferença URV"], 
                            [4005, "INDENIZATÓRIAS: Diferença PAE"], 
                            [4006, "INDENIZATÓRIAS: Abono de Permanência"], 
                            [4007, "INDENIZATÓRIAS: Previdência Social"], 
                            [4008, "INDENIZATÓRIAS: IRRF"], 
                            [3001, "EFEITOS NEGATIVOS: Redutor de Teto"], 
                            [2001, "RECISÓRIA: Férias Vencidas"], 
                            [2002, "RECISÓRIA: Adicional de Férias"], 
                            [2003, "RECISÓRIA: Gratificação Natalina"], 
                            [1001, "REMUNERAÇÃO: Subsídio"], 
                            [1002, "REMUNERAÇÃO: Vencimento"], 
                            [1003, "REMUNERAÇÃO: Gratificação de Representação"], 
                            [1004, "REMUNERAÇÃO: VPI"], 
                            [1005, "REMUNERAÇÃO: Adicional de Férias"], 
                            [1006, "REMUNERAÇÃO: Abono Permanência"], 
                            [1007, "REMUNERAÇÃO: Gratificação Natilina"]
                        ],
                        allowBlank: true,
                        triggerAction: 'all'
                    },{
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
        rh.gfp.evento.EventoWindow.superclass.constructor.call(this, cfg);
        this._observe();
    }    
});
