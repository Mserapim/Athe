
Ext._define('judicial.reports.SecretariatProductionReportWindow', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 550,

    _filename: 'relatorio-de-producao-da-secretaria.pdf',

    _report: '/to/mpe/judicial/report_of_production_secretariat',

    _reportName: 'Relatório de Produção da Secretaria',


    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "datefield",
                        fieldLabel: "Data de início da criação",
                        name: "data_inicio_criacao_documento_movimento",
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Data de término da criação",
                        name: "data_termino_criacao_documento_movimento",
                    },
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Secretaria",
                        rest: "judicial.secretary.Restful",
                        name: "secretaria"
                    },
                ]
            });

        return this._formPanel;
    },

    prepareValues: function(values) {
        var date_format_inicio_criacao_documento_movimento = this.prepareDate(values.data_inicio_criacao_documento_movimento, 'd/m/Y', 'Y-m-d');
        var date_format_termino_criacao_documento_movimento = this.prepareDate(values.data_termino_criacao_documento_movimento, 'd/m/Y', 'Y-m-d');
        values.data_inicio_criacao_documento_movimento = date_format_inicio_criacao_documento_movimento;
        values.data_termino_criacao_documento_movimento = date_format_termino_criacao_documento_movimento;
        return values;
    },
});
