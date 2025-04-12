/**
 *
 **/
Ext._define('rh.movimentacao.requisicao.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.movimentacao.requisicao.Restful',

    width: 800,

    tabHeight: 450,

    border: false,

    tabHeight: 450,

    border: false,

    getTabEncargoFinanceiro: function() {
        if(!this._tabEncargoFinanceiro)
            this._tabEncargoFinanceiro = Ext._create('rh.movimentacao.requisicao.EncargoFinanceiroGrid', {
                title: 'Encargo Financeiro',
                gridAutoLoad: false
            });
        return this._tabEncargoFinanceiro;
    },

    getTabPeriodo: function() {
        if(!this._tabPeriodo)
            this._tabPeriodo = Ext._create('rh.movimentacao.requisicao.PeriodoRequisicaoGrid', {
                title: 'Períodos',
                gridAutoLoad: false
            });
        return this._tabPeriodo;
    },

    _observe: function() {
        var grid;

        if(this.oId) {
            grid = this.getTabEncargoFinanceiro();
            grid.enable();
            grid.setParam('requisicao', this.oId);
            grid.setFilterProperty('requisicao__id', this.oId);

            gridPeriodo = this.getTabPeriodo();
            gridPeriodo.enable();
            gridPeriodo.setParam('requisicao', this.oId);
            gridPeriodo.setFilterProperty('requisicao__id', this.oId);
        }
        else {
            this.getTabEncargoFinanceiro().disable();
            this.getTabPeriodo().disable();
        }

        if(this.getParams().servidor){
            this.getPosseOrigem().setPreFilter([{
                property: 'servidor__id',
                value: this.getParams().servidor,
                stage: 0
            }]);
        }
    },

    getPosseOrigem: function(){
        if(!this.posseOrigem){
            this.posseOrigem = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Posse Origem *',
                name: 'posse_origem',
                rest: 'rh.movimentacao.possession.AllPossessionsRestful',
                width: 360
            });
        }
        return this.posseOrigem;
    },

    getTabForm: function() {
        if(!this._tabForm)
            this._tabForm = Ext._create('Ext.Panel', {
                layout: 'form',
                frame: true,
                border: false,
                title: 'Dados',
                labelWidth: 140,
                items: [
                    this.getPosseOrigem(),
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: "Publicação da requisição *",
                        allowBlank: false,
                        rest: "rh.publicacao.Restful",
                        name: "publicacao_movimentacao",
                        width: 360
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: "Publicação revogação",
                        allowBlank: true,
                        rest: "rh.publicacao.Restful",
                        name: "publicacao_alteracao",
                        width: 360
                    },
                    {
                        fieldLabel: 'Ônus *',
                        xtype: 'combo',
                        resizable: true,
                        value: null,
                        hiddenName: 'onus',
                        triggerAction: 'all',
                        store: [
                            ['', '---------'],
                            [1, 'ORIGEM'],
                            [2, 'REQUISITANTE']
                        ],
                        allowBlank: false,
                        width: 360
                    },
                    {
                        fieldLabel: 'Categoria origem (eSocial) *',
                        name: "category",
                        xtype: "choicefield",
                        hiddenName: "category",
                        choiceId: 'rh.CATEGORY_WORKER',
                        width: 360
                    },
                    {
                        disabled: false,
                        allowBlank: true,
                        fieldLabel: 'Data Início *',
                        xtype: 'datefield',
                        format: 'd/m/Y',
                        value: null,
                        name: 'data_inicio'
                    },
                    {
                        disabled: true,
                        allowBlank: true,
                        fieldLabel: 'Data Fim',
                        xtype: 'datefield',
                        format: 'd/m/Y',
                        value: null,
                        name: 'data_fim'
                    },
                    {
                        checked: true,
                        fieldLabel: 'Gerar Anotação',
                        xtype: 'checkbox',
                        name: 'anota',
                        allowBlank: true
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Texto',
                        xtype: 'xhtmleditor',
                        value: '',
                        name: 'texto',
                        width: 360,
                        height: 180
                    }]
            });

        return this._tabForm;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [{
                    xtype: 'tabpanel',
                    height: this.tabHeight,
                    activeItem: 0,
                    items: [
                        this.getTabForm(),
                        this.getTabEncargoFinanceiro(),
                        this.getTabPeriodo()
                    ]
                }]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        rh.movimentacao.requisicao.Window.superclass.constructor.call(this, cfg);
        this._observe();
    }
});
