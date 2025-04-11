
Ext._define('judicial.reports.ProductivityReportWindow', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 500,

    _filename: 'relatorio-de-produtividade',

    _report: '/to/mpe/raf/productivity_report',

    _reportName: 'Relatório E-ext - Produtividade',

    prepareValues: function (values) {
        values.mes_inicial = Number.parseInt(values.mes_inicial);
        values.mes_final = Number.parseInt(values.mes_final);

        var ppromotoria_slugfy = 'Null';
        var ppromotoria_slugfy_items = this.getLocationField().getGridPanel().getStore().data.items;
        if(ppromotoria_slugfy_items.length > 0) {
            ppromotoria_slugfy_items.map(function(item) {
                if (ppromotoria_slugfy === 'Null'){
                    ppromotoria_slugfy = `'${item.data.order_nome}'`;
                }else{
                    ppromotoria_slugfy += `, '${item.data.order_nome}'`;
                }
            });
        }
        values.ppromotoria_slugfy = ppromotoria_slugfy;

        return values;
    },

    getInitialYear: function (cfg) {
        if (!this._initialYear)
            this._initialYear = Ext._create('Ext.form.NumberField', {
                xtype: 'numberfield',
                fieldLabel: 'Ano Inicial',
                name: "ano_inicial",
                allowDecimals: false,
                allowBlank: false,
                maxLength: 4,
                width: 368,
            });

        return this._initialYear;
    },

    getEndYear: function (cfg) {
        if (!this._endYear)
            this._endYear = Ext._create('Ext.form.NumberField', {
                xtype: 'numberfield',
                fieldLabel: 'Ano Final',
                name: "ano_final",
                allowDecimals: false,
                allowBlank: false,
                maxLength: 4,
                width: 368,
            });

        return this._endYear;
    },

    getLocationField: function(cfg) {
        if(!this._locationField)
            this._locationField =
            Ext._create('core.fields.MultiSelectField', {
                title: 'Lotação',
                hideLabel: true,
                name: 'location',
                hiddenName: 'location',
                displayField: 'nome',
                allowBlank: false,
                rest: "judicial.params.WorkplaceRestful",
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
                },
                height: 250,
            });

        return this._locationField;
    },

    getItemsFormPanel: function (cfg) {
        return [
            {
                xtype: 'combobox',
                editable: false,
                allowBlank: false,
                value: 0,
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
                triggerAction: 'all',
                hiddenName: "mes_inicial",
                fieldLabel: 'Mês Inicial',
                width: 368,
            },
            this.getInitialYear(cfg),
            {
                xtype: 'combobox',
                editable: false,
                allowBlank: false,
                value: 0,
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
                triggerAction: 'all',
                hiddenName: "mes_final",
                fieldLabel: 'Mês Final',
                width: 368,
            },
            this.getEndYear(cfg),
            this.getLocationField(cfg),
        ]
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getItemsFormPanel(cfg)
                ]
            });

        return this._formPanel;
    },
});
