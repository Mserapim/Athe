Ext._define('judicial.reports.MovementReportWindowExternalInternal', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 850,

    _filename: 'relatorio-de-movimentacoes.pdf',

    _report: '/to/mpe/judicial/report_of_internal_e_external_diligences__sent_to_officers',

    _reportName: 'Relatório E-ext - Diligências - Para Gestor',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'choicefield',
                        emptyText: 'Todas as classes',
                        withNone: true,
                        withNoneLabel: 'Todas as classes',
                        name: 'tipo_entrega',
                        hiddenName: 'tipo_entrega',
                        fieldLabel: 'Tipo de Entrega',
                        width: 270,
                        choiceId: 'judicial.TYPE_VEHICLE'
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Data de designação inicial",
                        name: "data_designacao_inicial"
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Data de designação final",
                        name: "data_designacao_final"
                    },
                    {
                       xtype: "rest-autocompletefield",
                       fieldLabel: "Orgao",
                       rest: "rh.generalorgan.Restful",
                       name: "orgao"
                    },
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Sede",
                        rest: "judicial.county.Restful",
                        name: "sede"
                    },
                ]
            });

        return this._formPanel;
    },

    prepareValues: function(values) {
        var date_format_inicial = this.prepareDate(values.data_designacao_inicial, 'd/m/Y', 'Y-m-d');
        var date_format_final = this.prepareDate(values.data_designacao_final, 'd/m/Y', 'Y-m-d');
        values.data_designacao_inicial = date_format_inicial;
        values.data_designacao_final = date_format_final;
        return values;
    },

});
