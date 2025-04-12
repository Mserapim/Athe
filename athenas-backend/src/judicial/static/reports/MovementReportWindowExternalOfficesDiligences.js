
Ext._define('judicial.reports.MovementReportWindowExternalOfficesDiligences', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 850,

    _filename: 'relatorio-de-movimentacoes.pdf',

    _report: '/to/mpe/judicial/report_of_external_diligences__sent_to_officers',

    _reportName: 'Relatório E-ext - Movimentações - Por Oficiais',


    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "choicefield",
                        emptyText: 'Todos',
                        withNone: true,
                        withNoneLabel: 'Todos',
                        choiceId: 'judicial.TYPE_VEHICLE',
                        fieldLabel: "Tipo de entrega",
                        hiddenName: 'tipo_entrega',
                    },
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Oficial",
                        rest: "rh.employee.Restful",
                        name: "oficial",
                        preFilter: [
                            {'property':  'officerdiligence__isnull', 'value': false, 'stage': 1}
                        ]
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Data inicial",
                        name: "data_entrega_inicial"
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Data final",
                        name: "data_entrega_final"
                    },
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Orgão",
                        rest: "rh.generalorgan.Restful",
                        name: "orgao"
                    },
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Comarca",
                        rest: "rh.comarca.ComarcaRestful",
                        name: "comarca"
                    },

                ]
            });

        return this._formPanel;
    },


    prepareValues: function(values) {
        var date_format_inicial = this.prepareDate(values.data_entrega_inicial, 'd/m/Y', 'Y-m-d');
        var date_format_final = this.prepareDate(values.data_entrega_final, 'd/m/Y', 'Y-m-d');
        values.data_entrega_inicial= date_format_inicial;
        values.data_entrega_final = date_format_final;
        return values;
    },
});
