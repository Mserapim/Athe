
Ext._define('judicial.reports.TriageReportWindow', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 300,

    _filename: 'relatorio-de-distribuicoes-cartorio.pdf',

    _report: '/to/mpe/judicial/cartorio',

    _reportName: 'Relatório de Distribuições do Cartório',

    prepareValues: function(values) {

        values.data_inicial = this.castDate(values.data_inicial);
        values.data_final = this.castDate(values.data_final);

        return values;
    },

    getFromDateField: function(cfg) {
        if(!this._fromDateField)
            this._fromDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: 'Data Início',
                name: 'data_inicial',
                maxValue: new Date(),
                listeners: {
                    scope: this,
                    change: function(field, value, older) {
                        this.updateFilter({from: Ext.util.Format.date(value, 'Y-m-d')})
                    }
                }
            });

        return this._fromDateField;
    },

    getAtDateField: function(cfg) {
        if(!this._atDateField)
            this._atDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: 'Data Fim',
                name: 'data_final',
                maxValue: new Date(),
                listeners: {
                    scope: this,
                    change: function(field, value, older) {
                        this.updateFilter({at: Ext.util.Format.date(value, 'Y-m-d')})
                    }
                }
            });

        return this._atDateField;
    },

    getItemsFormPanel: function(cfg) {
        return [
            this.getFromDateField(cfg),
            this.getAtDateField(cfg)
        ];
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
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
