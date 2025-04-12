
Ext._define('judicial.reports.SecretariatsEntrancesExitsReportWindow', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 850,

    _filename: 'relatorio-de-entradas-e-saidas-secretarias.pdf',

    _report: '/to/mpe/judicial/report_of_entrances_exits_secretariats',

    _reportName: 'Relatório de entradas/saídas das secretarias',


    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "datefield",
                        fieldLabel: "Data de início do envio",
                        name: "data_inicio_envio",
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Data de término do envio",
                        name: "data_termino_envio",
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Data de início da devolução",
                        name: "data_inicio_devolucao",
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Data de término da devolução",
                        name: "data_termino_devolucao",
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
        var date_format_inicio_envio = this.prepareDate(values.data_inicio_envio, 'd/m/Y', 'Y-m-d');
        var date_format_termino_envio = this.prepareDate(values.data_termino_envio, 'd/m/Y', 'Y-m-d');
        var date_format_inicio_devolucao = this.prepareDate(values.data_inicio_devolucao, 'd/m/Y', 'Y-m-d');
        var date_format_termino_devolucao = this.prepareDate(values.data_termino_devolucao, 'd/m/Y', 'Y-m-d');
        values.data_inicio_envio = date_format_inicio_envio;
        values.data_termino_envio = date_format_termino_envio;
        values.data_inicio_devolucao = date_format_inicio_devolucao
        values.data_termino_devolucao = date_format_termino_devolucao;
        return values;
    },
});
