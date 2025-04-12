Ext._define('common.distribution.SelectDistributionWindow', {
    extend: 'Ext.Window',

    result: null,

    getHelpButton: function (cfg) {
        if (!this._helpButton) {
            this._helpButton = Ext._create('Ext.Button', {
                text: 'Ajuda',
                iconCls: 'icon-distribution icon-dist-help',
                scope: this,
                handler: function () {
                    Ext.Msg.show({
                        title: "Ajuda",
                        msg: [
                            'A Distribuição de "origem" é aquela da qual serão copiados',
                            'os Participantes.',
                            '<br><br>',
                            'Primeiramente selecione a sua lotação, e, logo abaixo, ',
                            'procure na lista a Distribuição que servirá de origem.',
                            '<br><br>',
                            'Por fim, clique no botão "Selecionar" para prosseguir com a ',
                            'operação.'
                        ].join(' '),
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                }
            });
        }

        return this._helpButton;
    },

    getSelectButton: function (cfg) {
        if (!this._selectButton) {
            this._selectButton = Ext._create('Ext.Button', {
                text: 'Selecionar',
                scope: this,
                disabled: true,
                handler: function () {
                    this.destroy();
                }
            });
        }

        return this._selectButton;
    },

    getCancelButton: function (cfg) {
        if (!this._cancelButton) {
            this._cancelButton = Ext._create('Ext.Button', {
                text: 'Cancelar',
                scope: this,
                handler: function () {
                    this.result = null;
                    this.destroy();
                }
            });
        }

        return this._cancelButton;
    },

    _employeeOriginSelect: function (combo, record, index) {
        var grid = this.getDistributionGrid();
        grid.enable();
        grid.setFilterProperty('origin', record.data.pk, 100);
    },

    _getEmployeeOriginStore: function (cfg) {
        if (!this._employeeOriginStore) {
            var url = core.callAction('CDDistribution', 'employee_locations');

            this._employeeOriginStore = Ext._create('Ext.data.Store', {
                proxy: Ext._create('Ext.data.HttpProxy', {url: url}),
                reader: Ext._create('Ext.data.JsonReader', {
                    totalProperty: 'count',
                    root: 'collection',
                    fields: [
                        {name: 'pk', type: 'int'},
                        {name: 'description', type: 'string'}
                    ]
                })
            });
        }

        return this._employeeOriginStore;
    },

    getEmployeeOriginField: function (cfg) {
        if (!this._employeeOriginField) {
            this._employeeOriginField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Lotação',
                hiddenName: 'origin',
                valueField: 'pk',
                displayField: 'description',
                anchor: '99%',
                emptyText: 'Lotação de origem...',
                store: this._getEmployeeOriginStore(),
                allowBlank: false
            });

            this._employeeOriginField.on({
                scope: this,
                select: this._employeeOriginSelect
            });
        }

        return this._employeeOriginField;
    },

    _distributionSelectionChange: function (selectionModel) {
        var selected = selectionModel.getSelected();

        if (selected) {
            this.result = selected.get('pk');
            this.getSelectButton().enable();
        } else {
            this.result = null;
            this.getSelectButton().disable();
        }
    },

    _distributionRowDblClick: function (grid, rowIndex, event) {
        var store = this.getDistributionGrid().getStore();
        this.result = store.getAt(rowIndex).data.pk;
        this.destroy();
    },

    getDistributionGrid: function (cfg) {
        if (!this._distributionGrid) {
            this._distributionGrid = Ext._create('common.distribution.Grid', {
                height: 490,
                border: true,
                disabled: true,
                gridAutoLoad: false,
                allowUpdate: false,
                columnAction: false,
                keywordFieldWidth: 600,
                configOrderToolBar: ['search', '->', 'download']
            });

            this._distributionGrid.getSelectionModel().on({
                scope: this,
                selectionchange: this._distributionSelectionChange
            });

            this._distributionGrid.on({
                scope: this,
                rowdblclick: this._distributionRowDblClick
            });
        }

        return this._distributionGrid;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 50,
                items: [
                    this.getEmployeeOriginField(cfg),
                    {
                        xtype: 'panel',
                        style: {
                            marginTop: '10px'
                        },
                        items: [
                            this.getDistributionGrid(cfg)
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Selecionar distribuição de origem',
            modal: true,
            resizable: false,
            width: 800,
            height: 600,
            border: false,
            items: [
                this.getFormPanel(cfg)
            ],
            buttonAlign: 'left',
            buttons: [
                this.getHelpButton(cfg),
                '->',
                this.getSelectButton(cfg),
                this.getCancelButton(cfg),
            ]
        });

        common.distribution.SelectDistributionWindow.superclass.constructor.call(this, cfg);
    }
}); 
