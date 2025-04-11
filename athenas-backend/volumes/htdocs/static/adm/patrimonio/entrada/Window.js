/**
 *
 **/
Ext._define('adm.patrimonio.entrada.Window', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.entrada.Restful',

    width: 850,

    getProviderField: function() {
        if (!this._providerField) {
            this._providerField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Fornecedor',
                name: "fornecedor",
                rest: 'rh.person.legalperson.Restful'
            });
        }

        return this._providerField;
    },

    getTabDocumento: function() {
        if(!this._tabDocumento)
            this._tabDocumento = Ext._create('adm.patrimonio.DocumentoGrid', {
                title: 'Documentos',
                gridAutoLoad: false
            });

        return this._tabDocumento;
    },

    _observe: function() {
        var grid;

        if(this.oId) {
            grid = this.getTabDocumento();
            grid.enable();
            grid.setParam('documentos_de_entrada', this.oId);
            grid.setFilterProperty('documentos_de_entrada__id', this.oId);

            grid = this.getTabApontamento();
            grid.enable();
            grid.setParam('nota', this.oId);
            grid.setFilterProperty('nota__id', this.oId);

            grid = this.getTabSuspensoes();
            grid.enable();
            grid.setParam('nota_entrada', this.oId);
            grid.setFilterProperty('nota_entrada__id', this.oId);
        }
        else {
            this.getTabDocumento().disable();
            this.getTabApontamento().disable();
            this.getTabSuspensoes().disable();
        }
    },

    _tabFields: function() {
        return [
            {
                xtype: 'displayfield',
                name: 'formated_number',
                fieldLabel: 'Controle'
            },
            {
                xtype: 'rest-autocompletefield',
                fieldLabel: 'Conta Patrimonial',
                name: 'conta',
                rest: 'adm.patrimonio.parametro.ContaRestful',
                gridColumnAction: false
            },
            this.getProviderField(),
            {
                fieldLabel: 'Data da Compra',
                xtype: 'datefield',
                name: 'data_compra'
            },
            {
                fieldLabel: 'Data da Nota',
                xtype: 'datefield',
                name: 'data_nota'
            },
            {
                fieldLabel: 'Processo',
                xtype: 'textfield',
                name: 'processo'
            },
            {
                xtype: 'rest-autocompletefield',
                fieldLabel: 'Nota de Empenho',
                name: 'empenho',
                rest: 'adm.contabilidade.NERestful',
                gridColumnAction: false
            },
            {
                fieldLabel: 'Execução Orçamentária',
                xtype: 'combo',
                width: 670,
                store: [
                    [1, 'DEO - Dependente da Execução Orçamentária'],
                    [2, 'IEO - Independete da Execução Orçamentária'],
                    [3, 'IEO - Doação']
                ],
                editable: false,
                triggerAction: 'all',
                hiddenName: 'execucao_orcamentaria'
            }
        ];
    },

    getTabForm: function() {
        if(!this._tabForm)
            this._tabForm = Ext._create('Ext.Panel', {
                layout: 'form',
                frame: true,
                border: false,
                title: 'Dados',
                labelWidth: 140,
                items: this._tabFields()
            });

        return this._tabForm;
    },

    getTabApontamento: function() {
        if(!this._apontamentoGrid) {
            this._apontamentoGrid = Ext._create('adm.patrimonio.entrada.CriticarNotaEntradaGrid', {
                gridAutoLoad: false,
                title: 'Apontamentos'
            });

            this._apontamentoGrid.getStore().on({
                scope: this,
                beforeload: function() {
                    this.readData();
                }
            });
        }

        return this._apontamentoGrid;
    },

    getTabSuspensoes: function() {
        if(!this._suspensaoPanel)
            this._suspensaoPanel = Ext._create('adm.patrimonio.SuspensaoGrid', {
                gridAutoLoad: false,
                title: 'Suspensões'
            });

        return this._suspensaoPanel;
    },

    tabHeight: 850,

    border: false,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    {
                        xtype: 'tabpanel',
                        height: this.tabHeight,
                        activeItem: 0,
                        items: [
                            this.getTabForm(),
                            this.getTabDocumento(),
                            this.getTabApontamento(),
                            this.getTabSuspensoes()
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        adm.patrimonio.entrada.Window.superclass.constructor.call(this, cfg);
        this._observe();
    }
});
